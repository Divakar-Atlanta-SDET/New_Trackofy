import re

from playwright.sync_api import expect

from Pages.home_page import HomePage
from Pages.login_page import LoginPage


def test_home_tab_loads_successfully(page, config, credentials):
    """Verify that the authenticated Home tab loads and survives refresh."""
    login_page = LoginPage(page, config)
    home_page = HomePage(page, config)

    # 1. Open the Trackofy login page from a fresh browser context.
    login_page.open()

    # 2. Log in using the configured test credentials.
    login_page.login(credentials["username"], credentials["password"])

    # 3. Verify that authentication redirects to the Home route.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"))

    # 4. Verify that the Home tab and primary Home content are visible.
    expect(home_page.home_tab).to_be_visible()
    expect(home_page.home_content).to_be_visible()
    expect(home_page.loading_indicator).not_to_be_visible()
    expect(home_page.application_error).not_to_be_visible()

    # 5. Refresh the page and verify that the Home route and content remain available.
    page.reload()
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"))
    expect(home_page.home_content).to_be_visible()


def test_selected_vehicle_checkbox_displays_same_vehicle_on_map(page, config, credentials):
    """Verify that selecting a Fleet vehicle displays the same vehicle on the map."""
    login_page = LoginPage(page, config)
    home_page = HomePage(page, config)

    # 1. Open the Trackofy login page from a fresh browser context.
    login_page.open()

    # 2. Log in using the configured test credentials.
    login_page.login(credentials["username"], credentials["password"])

    # 3. Verify that authentication redirects to the Home route.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"))

    # 4. Verify that the Home tab, Fleet panel, and map region are visible.
    expect(home_page.home_tab).to_be_visible()
    expect(home_page.fleet_tab).to_be_visible()
    expect(home_page.map_region).to_be_visible()

    # 5. Wait until at least one vehicle checkbox is visible in the Fleet list.
    expect(home_page.vehicle_checkboxes.first).to_be_visible(timeout=15000)
    vehicle_id = home_page.get_first_vehicle_id()
    vehicle_checkbox = home_page.vehicle_checkbox(vehicle_id)

    # 6. Check the first available vehicle's active tracking checkbox.
    vehicle_checkbox.check()

    # 7. Verify the checkbox is checked and the active tracking summary is updated.
    expect(vehicle_checkbox).to_be_checked()
    expect(home_page.active_tracking_summary).to_contain_text("Actively tracking 1 vehicle")

    # 8. Verify the map contains a marker for the same selected vehicle.
    expect(home_page.map_vehicle_marker(vehicle_id)).to_be_visible()
    expect(home_page.selected_vehicle_map_label(vehicle_id)).to_be_visible()

    # 9. Click the vehicle marker and verify the map info window shows the same vehicle.
    home_page.map_vehicle_marker(vehicle_id).click()
    expect(home_page.map_info_window_vehicle(vehicle_id)).to_be_visible()

    # 10. Clear active tracking and verify the vehicle is no longer selected.
    home_page.clear_tracking_button.click()
    expect(vehicle_checkbox).not_to_be_checked()


def test_home_active_vehicle_count_matches_side_menu_vehicle_count(page, config, credentials):
    """Verify that the Active Devices count matches the Fleet side-menu vehicle count."""
    login_page = LoginPage(page, config)
    home_page = HomePage(page, config)

    # 1. Open the Trackofy login page from a fresh browser context.
    login_page.open()

    # 2. Log in using the configured test credentials.
    login_page.login(credentials["username"], credentials["password"])

    # 3. Verify that authentication redirects to the Home route.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"))

    # 4. Verify the Fleet side-menu has loaded vehicle records.
    expect(home_page.vehicle_checkboxes.first).to_be_visible(timeout=15000)

    # 5. Compare the Active Devices KPI with the Fleet side-menu vehicle count.
    assert home_page.get_active_devices_count() == home_page.get_side_menu_vehicle_count()
