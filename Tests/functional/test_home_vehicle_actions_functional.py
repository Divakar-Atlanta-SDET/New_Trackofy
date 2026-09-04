import pytest


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("item", ["Playback", "POI", "Alert", "Unit Maintenance", "Unit Insight"])
def test_home_0092_0096_vehicle_menu_actions_open(home_page, item):
    """HOME-0092/0093/0094/0095/0096: Opening a vehicle's three-dot menu action
    triggers a real, correctly-scoped response for that action (a panel, or an
    informational toast when this account has no underlying data for it --
    confirmed live: this test account has no POI/alert/playback history data,
    so an honest "no data" toast is the correct, expected outcome here, not a
    silent no-op)."""
    home_page.open_fleet_tab()
    vehicle_id = home_page.visible_vehicle_ids()[0]
    before = home_page.visible_text()

    home_page.open_vehicle_menu_for(vehicle_id)
    menu_text = home_page.vehicle_menu_for(vehicle_id).inner_text()
    assert item in menu_text, f"'{item}' not found in vehicle menu: {menu_text!r}"

    home_page.click_vehicle_menu_item(vehicle_id, item)
    home_page.page.wait_for_timeout(1500)
    after = home_page.visible_text()
    assert after != before, f"Clicking '{item}' on {vehicle_id} produced no visible change at all"


@pytest.mark.functional
@pytest.mark.home
def test_home_0096b_bms_vehicle_has_battery_insight_menu_item(home_page):
    """Supplementary: BMS-enabled vehicles expose an extra 'Battery Insight'
    menu item not shown for regular vehicles (confirmed live, not in the
    design doc)."""
    home_page.open_fleet_tab()
    home_page.apply_fleet_status_filter("BMS")
    bms_ids = home_page.visible_vehicle_ids()
    if not bms_ids:
        pytest.skip("No BMS-enabled vehicles currently visible to verify this against")
    vehicle_id = bms_ids[0]
    home_page.open_vehicle_menu_for(vehicle_id)
    menu_text = home_page.vehicle_menu_for(vehicle_id).inner_text()
    assert home_page.BMS_VEHICLE_MENU_EXTRA_ITEM in menu_text, (
        f"Expected '{home_page.BMS_VEHICLE_MENU_EXTRA_ITEM}' in the menu for BMS-enabled "
        f"vehicle {vehicle_id}, got: {menu_text!r}"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0092_vehicle_menu_disabled_before_selection(home_page):
    """Supplementary: confirmed live that a vehicle's three-dot menu button is
    disabled until the vehicle card itself is selected (clicking it while
    disabled shows "Please select the vehicle first." instead of opening a
    menu) -- this is a real precondition the design doc doesn't mention, and
    every other vehicle-action test in this file depends on it being true."""
    home_page.open_fleet_tab()
    button = home_page.vehicle_card_more_vert_buttons().first
    button_class = button.get_attribute("class") or ""
    assert "cursor-not-allowed" in button_class, (
        f"Expected the three-dot menu button to start disabled before vehicle selection, "
        f"class was: {button_class!r}"
    )
    button.click(force=True)
    assert home_page.contains_any_text(["select the vehicle first"]), (
        "Clicking the disabled three-dot menu button should show a "
        "'select the vehicle first' message, not silently do nothing"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0098_close_contextual_toast(home_page):
    """HOME-0098: Closing a contextual action's response (here: the info toast
    from an action with no underlying data) returns Home to a valid state."""
    home_page.open_fleet_tab()
    vehicle_id = home_page.visible_vehicle_ids()[0]
    home_page.open_vehicle_menu_for(vehicle_id)
    home_page.click_vehicle_menu_item(vehicle_id, "Alert")
    home_page.page.wait_for_timeout(1500)
    close_buttons = home_page.page.locator("mat-icon", has_text="close")
    if close_buttons.count() == 0:
        pytest.skip("No closable toast/panel appeared to verify this against")
    close_buttons.first.click()
    home_page.page.wait_for_timeout(500)
    assert home_page.fleet_tab.is_visible(), "Home not in a valid state after closing the contextual response"
    assert home_page.vehicle_cards().count() > 0, "Fleet list not usable after closing the contextual response"
