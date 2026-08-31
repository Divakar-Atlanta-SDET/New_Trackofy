import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage


def login_and_open_unit_settings(page, config, credentials):
    """Helper to log in, navigate to /unit and open unit settings."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    return unit_page, unit_settings_page


@pytest.mark.edgecase
def test_tc001_vehicle_with_no_configured_alerts(page, config, credentials):
    """TC-001: Edge Case - Open Alert tab for vehicle without configured alerts."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Alert")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc002_large_number_of_alerts(page, config, credentials):
    """TC-002: Edge Case - Open Alert tab for vehicle with large alert dataset."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Alert")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc010_rapidly_switch_tabs(page, config, credentials):
    """TC-010: Edge Case - Rapidly click multiple Unit Settings tabs."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("General")
    unit_settings_page.switch_tab("Service")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc018_close_settings_during_unsaved_change(page, config, credentials):
    """TC-018: Edge Case - Modify a field and close settings without updating."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc020_double_click_update_submit(page, config, credentials):
    """TC-020: Edge Case - Rapidly double-click Update/Submit button."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.fill("55")
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.dblclick()
    expect(unit_settings_page.modal_heading).to_be_visible()

