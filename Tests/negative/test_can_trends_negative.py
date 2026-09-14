import pytest


@pytest.mark.negative
@pytest.mark.can
def test_can_trends_neg_001_apply_with_nothing_selected_does_not_render_a_chart(can_trends_page):
    """Confirmed live: Apply stays enabled with no Protocol/Units/Metric
    selected (not disabled up front) -- verify clicking it in that state
    is handled gracefully: no server error, and the "select at least one
    unit and a metric" placeholder stays in place rather than a bogus
    chart appearing."""
    can_trends_page.apply()
    assert can_trends_page.contains_texts(["Select at least one unit and a metric"]), (
        "Clicking Apply with nothing selected should leave the no-selection placeholder in place"
    )


@pytest.mark.negative
@pytest.mark.can
def test_can_trends_neg_002_units_has_no_options_until_protocol_selected(can_trends_page):
    """Confirmed live: the Units control itself stays enabled without a
    Protocol selected (not disabled) -- but opening it before a Protocol
    is chosen should offer no real units to pick, not a live list."""
    can_trends_page.open_units_dropdown()
    # Scoped to the just-opened overlay panel -- a page-wide
    # get_by_role("option") also matches the unrelated, always-present
    # Language selector's options (confirmed live).
    panel = can_trends_page.page.locator(".cdk-overlay-pane").last
    options = panel.get_by_role("option")
    real_options = [
        options.nth(i).inner_text().strip()
        for i in range(options.count())
        if options.nth(i).inner_text().strip() and not options.nth(i).inner_text().strip().startswith("Select")
    ]
    can_trends_page.close_units_dropdown()
    assert not real_options, (
        f"Units offered selectable options before any Protocol was chosen: {real_options}"
    )


@pytest.mark.negative
@pytest.mark.can
def test_can_trends_neg_003_more_than_five_units_is_capped_or_rejected(can_trends_page):
    """Explanation doc and live copy both state "up to 5 units" -- verify
    the UI actually enforces that cap rather than silently accepting a
    6th selection or erroring at Apply time."""
    can_trends_page.select_first_available_protocol()

    can_trends_page.open_units_dropdown()
    all_options = can_trends_page.page.get_by_role("option")
    option_count = all_options.count()
    if option_count < 6:
        can_trends_page.close_units_dropdown()
        pytest.skip(f"Only {option_count} unit(s) available for this protocol -- cannot exercise the 6th-selection case")

    for i in range(6):
        can_trends_page.safe_click(all_options.nth(i))
        can_trends_page.page.wait_for_timeout(200)
    can_trends_page.close_units_dropdown()

    selected = can_trends_page.selected_unit_count()
    assert selected <= 5, f"Selecting 6 units resulted in {selected} selected -- 5-unit cap not enforced"
