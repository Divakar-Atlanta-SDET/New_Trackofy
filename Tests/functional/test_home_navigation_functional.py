import pytest
from playwright.sync_api import expect


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
    assert home_page.group_cards().count() > 0, "Groups tab active but no group cards displayed"


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


@pytest.mark.functional
@pytest.mark.home
def test_home_0297_rapid_tab_switching(home_page):
    """The final tab must own the rendered cards after rapid tab changes."""
    for tab in (home_page.groups_tab, home_page.drivers_tab, home_page.fleet_tab) * 3:
        tab.click()
    expect(home_page.vehicle_cards().first).to_be_visible()
    expect(home_page.driver_cards()).to_have_count(0)
    expect(home_page.group_cards()).to_have_count(0)


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("entity", ["Groups", "Drivers"])
def test_home_0312_0313_no_duplicate_entities(home_page, entity):
    """Rendered group/driver identities must not duplicate after refresh."""
    getattr(home_page, f"open_{entity.lower()}_tab")()
    names = home_page.rendered_entity_names(entity)
    assert names and len(names) == len(set(names))
    home_page.page.reload()
    home_page.wait_for_visible(home_page.fleet_tab)
    getattr(home_page, f"open_{entity.lower()}_tab")()
    names = home_page.rendered_entity_names(entity)
    assert names and len(names) == len(set(names))


@pytest.mark.functional
@pytest.mark.home
def test_home_0013_side_panel_collapse_expand(home_page):
    """The left panel can be collapsed and restored with the map still usable."""
    home_page.collapse_left_panel()
    expect(home_page.search_input).not_to_be_visible()
    home_page.switch_to_hybrid_mode()
    assert home_page.map_mode_is_selected("Hybrid")
    home_page.expand_left_panel()
    expect(home_page.search_input).to_be_visible()
    expect(home_page.vehicle_cards().first).to_be_visible()


@pytest.mark.functional
@pytest.mark.home
def test_home_settings_controls_and_cancel(home_page):
    """Home Settings exposes the current List/Group and marker configuration."""
    home_page.open_home_settings()
    text = home_page.home_settings_dialog().inner_text()
    for label in ("Default view", "List", "Group", "Map Marker", "Label", "Status", "Glow", "More Options"):
        assert label in text
    home_page.home_settings_cancel()
    expect(home_page.home_settings_dialog()).not_to_be_visible()
    expect(home_page.vehicle_cards().first).to_be_visible()


@pytest.mark.functional
@pytest.mark.home
def test_home_0303_kpi_dialog_keyboard_focus(home_page):
    """KPI dialog receives focus, contains Tab navigation and closes with Escape."""
    home_page.kpi_settings_button.focus()
    home_page.page.keyboard.press("Enter")
    expect(home_page.kpi_settings_dialog()).to_be_visible()
    expect(home_page.kpi_settings_checkbox("Running")).to_be_visible()
    home_page.page.keyboard.press("Tab")
    assert home_page.focus_is_inside(home_page.kpi_settings_dialog()), "Tab escaped the active KPI dialog"
    home_page.page.keyboard.press("Escape")
    expect(home_page.kpi_settings_dialog()).not_to_be_visible()


@pytest.mark.functional
@pytest.mark.home
def test_home_0326_refresh_unsaved_geolink(home_page):
    """Refresh discards an unsaved GeoLink and returns to usable Home."""
    home_page.open_geolinks()
    count = home_page.geolinks_count()
    home_page.click_create_geolink()
    home_page.fill_geolink_share_name("pytest-unsaved-refresh")
    home_page.page.reload()
    home_page.wait_for_fleet_loaded()
    home_page.open_geolinks()
    assert home_page.geolinks_count() == count
    assert home_page.geolink_row("pytest-unsaved-refresh").count() == 0
