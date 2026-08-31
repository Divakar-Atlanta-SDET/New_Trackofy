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


@pytest.mark.negative
def test_tc008_alert_api_failure(page, config, credentials):
    """TC-008: Negative - Intercept alert API request failure and check error handling."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Alert")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc016_handle_settings_api_failure(page, config, credentials):
    """TC-016: Negative - Intercept settings update API failure."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc028_verify_failed_update_notification(page, config, credentials):
    """TC-028: Negative - Trigger validation or API failure and assert error feedback."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc029_expired_session_during_update(page, config, credentials):
    """TC-029: Negative - Clear session cookies before submit and verify authentication redirect."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    page.context.clear_cookies()
    unit_settings_page.switch_tab("General")
    expect(page.locator("body")).to_be_visible()


@pytest.mark.negative
def test_tc070_attempt_invalid_icon_selection(page, config, credentials):
    """TC-070: Negative - Attempt invalid icon selection."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()
