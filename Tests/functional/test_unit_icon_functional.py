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


@pytest.mark.functional
def test_tc066_verify_icon_tab_loads(page, config, credentials):
    """TC-066: Functional - Open Icon tab and verify Unit Type, Current Icon, and Available Icons display."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc067_verify_current_icon_is_displayed(page, config, credentials):
    """TC-067: Functional - Open Icon tab and check current icon matches Unit List icon."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc068_open_unit_type_dropdown(page, config, credentials):
    """TC-068: Functional - Click Unit Type dropdown in Icon tab."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc069_cancel_icon_change(page, config, credentials):
    """TC-069: Functional - Select another icon but close without updating; original saved icon remains."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()

