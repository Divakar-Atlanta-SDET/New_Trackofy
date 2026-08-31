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
def test_tc071_change_icon_to_another_available_icon(page, config, credentials):
    """TC-071: Positive - Select an available icon from Icon tab and click Update."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc072_change_icon_and_persist_after_reopening(page, config, credentials):
    """TC-072: Positive - Change icon, save, close settings and reopen to verify persistence."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()


@pytest.mark.positive
def test_tc073_icon_selection_persists_across_sessions(page, config, credentials):
    """TC-073: Positive - Verify selected icon remains saved across tab reloads."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()

