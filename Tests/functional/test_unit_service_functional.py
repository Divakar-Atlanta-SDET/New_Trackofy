import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage


@pytest.mark.functional
def test_verify_service_subtabs_navigation(page, config, credentials):
    """TC-127, TC-128: Open Service tab and switch between sub-tabs."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    # 1. Switch to Service sub-tabs.
    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.switch_service_subtab("Pollution")
    unit_settings_page.switch_service_subtab("Insurance")
    unit_settings_page.switch_service_subtab("Service")

    # 2. Assert modal heading remains visible.
    expect(unit_settings_page.modal_heading).to_be_visible()
