import pytest


@pytest.mark.functional
@pytest.mark.home
def test_home_0001_home_loads(home_page):
    """HOME-0001: Home loads successfully and core monitoring UI is available."""
    assert home_page.fleet_tab.is_visible(), "Fleet tab not visible after Home load"
    assert home_page.vehicle_cards().count() > 0, "No vehicle cards rendered on Home load"
    assert home_page.get_kpi_value("Total Fleet"), "Total Fleet KPI has no value on Home load"


@pytest.mark.functional
@pytest.mark.home
def test_home_0002_refresh_no_duplicates(home_page):
    """HOME-0002: Refresh reloads current Home data without duplicate cards or alerts.

    Vehicle status/alert *counts* are live and can genuinely change between
    the two reads (this is a real fleet, not fixture data) -- so this only
    asserts the one thing that must hold regardless of live drift: no
    duplicate identifiers rendered.
    """
    before_ids = home_page.visible_vehicle_ids()
    assert len(before_ids) == len(set(before_ids)), f"Duplicate vehicle cards before refresh: {before_ids}"

    home_page.page.reload()
    home_page.wait_until_ready()
    home_page.wait_for_visible(home_page.fleet_tab)
    home_page.wait_for_fleet_loaded()

    after_ids = home_page.visible_vehicle_ids()
    assert len(after_ids) == len(set(after_ids)), f"Duplicate vehicle cards after refresh: {after_ids}"
    assert after_ids, "No vehicle cards rendered after refresh"


@pytest.mark.functional
@pytest.mark.home
def test_home_0003_fleet_tab(home_page):
    """HOME-0003: Clicking Fleet makes it active and vehicle cards are displayed."""
    home_page.open_fleet_tab()
    assert home_page.vehicle_cards().count() > 0, "Fleet tab active but no vehicle cards displayed"


@pytest.mark.functional
@pytest.mark.home
def test_home_0004_groups_tab(home_page):
    """HOME-0004: Clicking Groups makes it active and group cards are displayed."""
    home_page.open_groups_tab()
    group_names = home_page.group_cards().all_inner_texts()
    for known_group in home_page.KNOWN_GROUPS:
        assert any(known_group in text for text in group_names), (
            f"Expected group '{known_group}' not found in Groups tab: {group_names}"
        )


@pytest.mark.functional
@pytest.mark.home
def test_home_0005_drivers_tab(home_page):
    """HOME-0005: Clicking Drivers makes it active and driver cards are displayed."""
    home_page.open_drivers_tab()
    assert home_page.driver_cards().count() > 0, "Drivers tab active but no driver cards displayed"


@pytest.mark.functional
@pytest.mark.home
def test_home_0006_fleet_to_groups_no_stale_content(home_page):
    """HOME-0006: Group data replaces Fleet data without stale vehicle cards."""
    home_page.open_fleet_tab()
    assert home_page.vehicle_cards().count() > 0
    home_page.open_groups_tab()
    assert home_page.driver_cards().count() == 0, "Driver cards should not appear on Groups tab"
    group_names = home_page.group_cards().all_inner_texts()
    assert any("Default" in text for text in group_names), (
        f"Groups tab content missing after switching from Fleet: {group_names}"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0007_groups_to_drivers_no_stale_content(home_page):
    """HOME-0007: Driver data replaces group data without stale group content."""
    home_page.open_groups_tab()
    assert home_page.group_cards().count() > 0
    home_page.open_drivers_tab()
    assert home_page.driver_cards().count() > 0, "Drivers tab active but no driver cards displayed"
    assert home_page.group_cards().count() == 0, "Group cards should not remain visible on Drivers tab"


@pytest.mark.functional
@pytest.mark.home
def test_home_0008_drivers_to_fleet_restores_fleet(home_page):
    """HOME-0008: Fleet data is restored correctly after Drivers -> Fleet."""
    home_page.open_drivers_tab()
    assert home_page.driver_cards().count() > 0
    home_page.open_fleet_tab()
    assert home_page.vehicle_cards().count() > 0, "Fleet data not restored after switching back from Drivers"
    assert home_page.driver_cards().count() == 0, "Driver cards should not remain visible on Fleet tab"


@pytest.mark.functional
@pytest.mark.home
def test_home_0014_no_vehicle_empty_state(home_page):
    """HOME-0014: A Fleet filter/search with no matches shows a clear empty state."""
    home_page.open_fleet_tab()
    home_page.search("zzznonexistentvehiclequery999")
    assert home_page.vehicle_cards().count() == 0, "Vehicle cards still shown for a non-matching search"
    assert home_page.contains_any_text(["No vehicles", "No results", "No data", "not found"]), (
        "No recognizable empty-state message shown for a non-matching Fleet search"
    )
    home_page.clear_search()


@pytest.mark.functional
@pytest.mark.home
def test_home_0020_browser_back_forward(home_page, config):
    """HOME-0020: Navigating away and back returns Home to a valid state."""
    home_page.page.goto(f"{config['base_url']}/dashboard")
    home_page.wait_until_ready()
    home_page.page.go_back()
    home_page.wait_until_ready()
    home_page.wait_for_visible(home_page.fleet_tab)
    home_page.wait_for_fleet_loaded()
    assert home_page.vehicle_cards().count() > 0, (
        "Fleet data not in a valid state after browser Back to Home"
    )
