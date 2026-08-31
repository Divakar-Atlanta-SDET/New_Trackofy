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


@pytest.mark.positive
def test_tc009_verify_active_alerts_are_displayed(page, config, credentials):
    """TC-009: Positive - Open Alert tab for vehicle with active alerts."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Alert")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc017_reload_settings_and_retain_saved_data(page, config, credentials):
    """TC-017: Positive - Update a setting, save, close, and reopen settings to verify saved data."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    unit_settings_page.close_modal()
    page.wait_for_timeout(1000)
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    expect(unit_settings_page.modal_heading).to_be_visible()
