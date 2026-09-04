import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize(
    "kpi_name",
    [
        "Total Fleet",
        "Active Devices",
        "Running",
        "Idle",
        "Stopped",
        "No Data",
        "BMS Enabled",
        "Video Enabled",
        "Expired Devices",
        "Critical Alerts",
        "Active Trips",
    ],
)
def test_home_0043_0052_kpi_label_and_value_displayed(home_page, kpi_name):
    """HOME-0043 to 0052: Each KPI card shows its label and a real numeric
    value, without overlap (checked as: the card is visible and its value
    parses as a plain number)."""
    home_page.open_fleet_tab()
    if kpi_name not in home_page.ALWAYS_ON_KPIS and not home_page.kpi_visible(kpi_name):
        pytest.skip(
            f"'{kpi_name}' card isn't currently rendered -- confirmed live behavior is that a "
            "status KPI's card disappears entirely (not '0') when its live fleet count is zero"
        )
    card = home_page.kpi_card(kpi_name)
    assert card.is_visible(), f"KPI card '{kpi_name}' is not visible"
    value = home_page.get_kpi_value(kpi_name)
    assert value, f"KPI card '{kpi_name}' has no readable value"
    assert value.replace(",", "").replace(".", "").isdigit(), (
        f"KPI card '{kpi_name}' value '{value}' does not look like a plain number"
    )


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("kpi_name", ["Running", "Idle", "Stopped", "No Data"])
def test_home_0053_0056_0074_0077_kpi_filters_and_reconciles_with_fleet(home_page, kpi_name):
    """HOME-0053/0054/0055/0056 + HOME-0074/0075/0076/0077: Clicking a status
    KPI filters Fleet to that category, and the resulting Fleet count
    reconciles exactly with the KPI's own value."""
    home_page.open_fleet_tab()
    if not home_page.kpi_visible(kpi_name):
        pytest.skip(f"'{kpi_name}' card isn't currently rendered (live count is 0) -- nothing to filter")
    kpi_value = int(home_page.get_kpi_value(kpi_name))
    if kpi_value == 0:
        pytest.skip(f"No vehicles currently in '{kpi_name}' to verify filtering against")

    home_page.click_kpi(kpi_name)
    home_page.page.wait_for_timeout(1000)
    fleet_count = home_page.fleet_result_count()
    assert fleet_count == kpi_value, (
        f"'{kpi_name}' KPI shows {kpi_value} but clicking it filtered Fleet to {fleet_count} vehicles"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0057_open_kpi_settings(home_page):
    """HOME-0057: KPI Settings dialog opens with available KPI options."""
    home_page.open_kpi_settings()
    dialog_text = home_page.kpi_settings_dialog().inner_text()
    for kpi in home_page.CONFIGURABLE_KPIS:
        assert kpi in dialog_text, f"Expected KPI option '{kpi}' in KPI Settings dialog: {dialog_text!r}"
    home_page.close_kpi_settings()


@pytest.mark.functional
@pytest.mark.home
def test_home_0058_select_all(home_page):
    """HOME-0058: Select All selects every available KPI option.

    Deliberately starts from a partial selection (not whatever state the
    account happens to already be in) -- see Bug #21 in Bug_Report.md:
    clicking Select All while already fully selected paradoxically
    deselects down to the protected minimum instead of staying at max, so
    this test's own precondition can't rely on the account's ambient state.
    """
    home_page.open_kpi_settings()
    # Force a genuinely partial starting selection first.
    for kpi in home_page.CONFIGURABLE_KPIS[:3]:
        checkbox = home_page.kpi_settings_checkbox(kpi)
        if checkbox.is_checked():
            checkbox.uncheck()
    home_page.page.wait_for_timeout(500)

    home_page.kpi_settings_select_all()
    total_options = len(home_page.CONFIGURABLE_KPIS) + 1  # +1 for "Total Vehicles"
    assert home_page.kpi_settings_selected_count() == total_options, (
        f"Select All should select all {total_options} KPIs, "
        f"got {home_page.kpi_settings_selected_count()}"
    )
    for kpi in home_page.CONFIGURABLE_KPIS:
        assert home_page.kpi_settings_checkbox(kpi).is_checked(), f"'{kpi}' checkbox not checked after Select All"
    home_page.close_kpi_settings()


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0058b_select_all_when_already_full_drops_to_minimum(home_page):
    """Regression pin for Bug #21 (Bug_Report.md, Home Module): clicking
    'Select All' while every KPI is already selected does not stay at max
    -- it paradoxically deselects down to the protected minimum of 6, with
    no change to the button's own label. This assertion documents the
    confirmed-broken behavior; it should start failing (and be flipped to
    assert full selection is preserved) once the app is fixed.
    """
    home_page.open_kpi_settings()
    home_page.kpi_settings_check_all()
    home_page.page.wait_for_timeout(500)
    total_options = len(home_page.CONFIGURABLE_KPIS) + 1
    assert home_page.kpi_settings_selected_count() == total_options, (
        f"Setup failed: expected all {total_options} KPIs selected before the probe click, "
        f"got {home_page.kpi_settings_selected_count()}"
    )

    home_page.kpi_settings_dialog().get_by_text("Select All", exact=True).click()
    home_page.page.wait_for_timeout(2500)
    after = home_page.kpi_settings_selected_count()
    assert after == 6, (
        "Bug #21: clicking 'Select All' while already fully selected should drop selection "
        f"to the protected minimum of 6 (confirmed live app behavior) -- got {after}. If this "
        "now stays at 10, the bug is fixed and this test should be flipped to assert that."
    )
    # Leave the dialog in a clean, known state for whatever runs next.
    home_page.kpi_settings_check_all()
    home_page.kpi_settings_save()
    home_page.wait_for_loading_to_finish()


@pytest.mark.functional
@pytest.mark.home
def test_home_0061_less_than_6_kpis_blocks_save(home_page):
    """HOME-0061: The minimum-6-KPIs rule is enforced -- selection can never
    actually go below 6.

    Confirmed live: the app enforces this proactively, not reactively --
    once selection reaches exactly 6, the still-checked boxes become
    disabled so a 6th uncheck is blocked outright, rather than letting you
    drop below 6 and then showing a validation message with Save disabled
    (the CSV's assumed mechanism). Either mechanism satisfies the same
    protective goal (never end up with <6 selected), so this test accepts
    whichever one the live app actually uses.
    """
    home_page.open_kpi_settings()
    home_page.kpi_settings_check_all()
    total_options = len(home_page.CONFIGURABLE_KPIS) + 1
    # Uncheck one at a time down toward the 6-minimum boundary, settling
    # the lagging "Currently selected" count after each click so the next
    # uncheck acts on a checkbox whose enabled/disabled state has caught up.
    to_uncheck = home_page.CONFIGURABLE_KPIS[:5]
    for i, kpi in enumerate(to_uncheck[:4]):
        home_page.kpi_settings_checkbox(kpi).uncheck()
        home_page.kpi_settings_wait_for_count(total_options - (i + 1))
    assert home_page.kpi_settings_selected_count() == 6, (
        f"Expected exactly 6 selected after 4 unchecks from {total_options}, "
        f"got {home_page.kpi_settings_selected_count()}"
    )

    sixth_kpi = to_uncheck[4]
    sixth_checkbox = home_page.kpi_settings_checkbox(sixth_kpi)
    try:
        sixth_checkbox.uncheck(timeout=5000)
        went_below_6 = True
    except PlaywrightTimeoutError:
        went_below_6 = False

    if went_below_6:
        assert home_page.kpi_settings_selected_count() < 6, (
            f"Expected fewer than 6 selected, got {home_page.kpi_settings_selected_count()}"
        )
        assert home_page.kpi_settings_validation_visible(), "Expected 'Select at least 6 KPIs' validation to show"
        save_button = home_page.kpi_settings_dialog().get_by_role("button", name="Save")
        assert not save_button.is_enabled(), "Save should be disabled/blocked with fewer than 6 KPIs selected"
    else:
        assert not sixth_checkbox.is_enabled(), (
            f"'{sixth_kpi}' checkbox neither unchecked nor reported disabled at the 6-KPI minimum -- "
            "the app should block going below 6 one way or the other"
        )
        assert home_page.kpi_settings_selected_count() == 6, (
            "Selection should still be exactly 6 after the blocked uncheck attempt, "
            f"got {home_page.kpi_settings_selected_count()}"
        )
    home_page.kpi_settings_cancel()


@pytest.mark.functional
@pytest.mark.home
def test_home_0064_cancel_discards_changes(home_page):
    """HOME-0064: Changing KPI selections and clicking Cancel discards them."""
    home_page.open_fleet_tab()
    before_ids = set(home_page.visible_vehicle_ids())  # sanity the page is stable
    home_page.open_kpi_settings()
    home_page.kpi_settings_checkbox("Idle").uncheck()
    home_page.kpi_settings_cancel()
    assert home_page.kpi_card("Idle").is_visible(), (
        "Idle KPI card should still be visible after Cancel discarded the unselect"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0059_0060_0065_unselect_select_save_and_reopen_reflects_state(home_page):
    """HOME-0059/0060/0065: Unselecting one KPI and saving removes it from the
    header (others unchanged); reselecting and saving restores it; reopening
    the dialog reflects the saved state correctly.

    Uses 'Idle' rather than 'Running' as the toggled KPI: confirmed live
    that a status KPI's card disappears entirely (not '0') whenever its
    live fleet count is zero, and 'Running' fluctuates to/from zero often
    enough on this account to make it an unreliable choice for a test whose
    point is the toggle mechanics, not that specific KPI's live count.
    """
    home_page.open_fleet_tab()
    assert home_page.kpi_card("Idle").is_visible(), "Idle KPI should be visible before this test starts"

    try:
        home_page.open_kpi_settings()
        home_page.kpi_settings_checkbox("Idle").uncheck()
        home_page.kpi_settings_save()
        home_page.wait_for_loading_to_finish()
        home_page.page.wait_for_timeout(1000)  # header re-render lags the save response briefly
        assert home_page.kpi_card("Stopped").is_visible(), "Unrelated 'Stopped' KPI should remain after unselecting Idle"
        assert home_page.kpi_card("Idle").count() == 0 or not home_page.kpi_card("Idle").is_visible(), (
            "Idle KPI card should be removed from the header after saving without it"
        )

        home_page.open_kpi_settings()
        assert not home_page.kpi_settings_checkbox("Idle").is_checked(), (
            "Reopening KPI Settings should reflect Idle as unselected"
        )
        home_page.kpi_settings_checkbox("Idle").check()
        home_page.kpi_settings_save()
        home_page.wait_for_loading_to_finish()
        home_page.page.wait_for_timeout(1000)  # header re-render lags the save response briefly
        assert home_page.kpi_card("Idle").is_visible(), "Idle KPI should reappear after reselecting and saving"
    finally:
        # Restore the account's default configuration (all 10) regardless of
        # pass/fail, so this test doesn't leave the account in a different
        # KPI configuration for later tests/users. Bounded retry: dialog
        # interaction under this much back-to-back load has occasionally
        # stalled on a single attempt (confirmed live, cause not fully
        # isolated) -- a page reload plus one retry has reliably recovered
        # it, and this is a cleanup path, not a behavior under test.
        for attempt in range(2):
            try:
                home_page.open_kpi_settings()
                home_page.kpi_settings_check_all()
                home_page.kpi_settings_save()
                home_page.wait_for_loading_to_finish()
                break
            except PlaywrightTimeoutError:
                if attempt == 1:
                    raise
                home_page.page.reload()
                home_page.wait_for_fleet_loaded()


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0073_kpi_api_failure_shows_clear_state(home_page, config):
    """HOME-0073: If the Home data API fails, a clear error/empty state is
    shown -- stale KPI values are not presented as current."""
    page = home_page.page
    page.route("**/user_test_home.php*", lambda route: route.abort())
    page.reload()
    page.wait_for_timeout(3000)
    page.unroute("**/user_test_home.php*")

    # Either a recognizable error/empty state is shown, or the KPI cards
    # simply never populate with misleading numbers.
    has_error_state = home_page.contains_any_text(
        ["error", "failed", "try again", "unable to load", "something went wrong"]
    )
    total_fleet_value = ""
    try:
        total_fleet_value = home_page.get_kpi_value("Total Fleet")
    except Exception:
        pass
    assert has_error_state or not total_fleet_value, (
        "When the Home data API fails, expected either a visible error state or an "
        f"empty/unpopulated Total Fleet KPI -- got value {total_fleet_value!r} with no error shown"
    )
