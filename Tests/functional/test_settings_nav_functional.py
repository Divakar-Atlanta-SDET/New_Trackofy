import re

import pytest
from playwright.sync_api import expect

from components.navbar import Navbar


@pytest.mark.functional
def test_set_001_settings_module_opens(authenticated_page):
    """SET-001: Verify Settings module opens and the Settings side menu is displayed.

    Routes through the nav-bar link, not goto("/settings") -- confirmed live
    (2026-09-13) that a direct goto to /settings hits NEW-1 and bounces to
    /home. See test_settings_accessible_via_direct_url below for the
    dedicated regression pin on the raw-goto case itself.
    """
    Navbar(authenticated_page).go_to("Settings")
    authenticated_page.wait_for_load_state("domcontentloaded")
    expect(authenticated_page.get_by_role("complementary", name="Settings navigation")).to_be_visible()


@pytest.mark.functional
def test_settings_accessible_via_direct_url(authenticated_page, config):
    """Regression test for retest_bug_report.md NEW-1 (app-wide SPA routing
    defect): a module must be reachable by navigating straight to its URL,
    not only via an in-app nav-link click. Deliberately uses page.goto()
    directly (not SettingsSideMenu, which works around this exact bug by
    clicking through the module) -- this test exists specifically to catch
    a regression on direct URL access itself.

    Expected to FAIL until the underlying app bug is fixed: as of this
    writing, a direct goto("/settings") silently redirects to /home instead
    of loading Settings. Once the app fix lands, this test turns green
    automatically -- no code change needed here to detect it.
    """
    page = authenticated_page
    page.goto(f"{config['base_url']}/settings")
    page.wait_for_timeout(2000)
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/settings/?$"))


@pytest.mark.functional
def test_set_002_four_major_sections_displayed(settings_menu):
    """SET-002: Verify the four major Settings sections are displayed."""
    expect(settings_menu.driver_management_btn).to_be_visible()
    expect(settings_menu.vehicle_management_btn).to_be_visible()
    expect(settings_menu.alert_configuration_btn).to_be_visible()
    expect(settings_menu.route_management_btn).to_be_visible()


@pytest.mark.functional
def test_set_003_expand_collapse_driver_management(settings_menu):
    """SET-003: Expand and collapse Driver Management."""
    settings_menu._ensure_expanded(settings_menu.vehicle_management_btn)  # start from a different section expanded
    expect(settings_menu.driver_btn).to_be_hidden()

    settings_menu.driver_management_btn.click()
    expect(settings_menu.driver_btn).to_be_visible()
    expect(settings_menu.driver_performance_btn).to_be_visible()

    settings_menu.driver_management_btn.click()
    expect(settings_menu.driver_btn).to_be_hidden()


@pytest.mark.functional
def test_set_004_expand_collapse_vehicle_management(settings_menu):
    """SET-004: Expand and collapse Vehicle Management."""
    settings_menu.vehicle_management_btn.click()
    expect(settings_menu.vehicle_group_btn).to_be_visible()
    expect(settings_menu.vehicle_performance_btn).to_be_visible()
    expect(settings_menu.location_control_btn).to_be_visible()

    settings_menu.vehicle_management_btn.click()
    expect(settings_menu.vehicle_group_btn).to_be_hidden()


@pytest.mark.functional
def test_set_005_expand_alert_configuration(settings_menu):
    """SET-005: Expand Alert Configuration; all configured alert submenu types are displayed."""
    from Pages.settings_page import ALERT_TYPES

    settings_menu.alert_configuration_btn.click()
    for alert_type in ALERT_TYPES:
        expect(settings_menu.alert_type_buttons[alert_type]).to_be_visible()


@pytest.mark.functional
def test_set_006_open_route_management(settings_menu):
    """SET-006: Open Route Management; page opens and route functionality is accessible."""
    settings_menu.open_route_management()
    expect(settings_menu.page.get_by_role("heading", name="Route", exact=False)).to_be_visible()
    expect(settings_menu.page.get_by_role("button", name="Add Route")).to_be_visible()


@pytest.mark.functional
def test_set_007_settings_search(settings_menu):
    """SET-007: Verify Settings search surfaces a known submenu and it can be opened."""
    settings_menu.search_settings("Driver Performance")
    result = settings_menu.page.get_by_role("button", name="Driver Performance", exact=True)
    expect(result).to_be_visible()
    result.click()
    settings_menu.wait_for_loading_to_finish()
    expect(settings_menu.page.get_by_role("heading", name="Driver Performance", exact=False)).to_be_visible()
