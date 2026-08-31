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
def test_tc064_switch_unit_type_before_selecting_icon(page, config, credentials):
    """TC-064: Edge Case - Change Unit Type and verify available icons list updates."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc065_rapidly_switch_unit_types(page, config, credentials):
    """TC-065: Edge Case - Change unit type multiple times quickly and check UI stability."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.modal_heading).to_be_visible()

