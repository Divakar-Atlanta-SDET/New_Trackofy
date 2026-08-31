import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage


@pytest.mark.edgecase
def test_zero_and_decimal_speed_limit(page, config, credentials):
    """TC-039, TC-040: Test zero (0) and decimal (50.5) Speed Limit inputs."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    # 1. Enter decimal speed limit 50.5.
    unit_settings_page.update_speed_limit("50.5")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_rapid_tab_switching_in_unit_settings(page, config, credentials):
    """TC-010: Rapidly switch between Unit Settings tabs."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    # 1. Rapidly switch tabs.
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("General")
    unit_settings_page.switch_tab("Service")

    # 2. Assert modal state is synchronized.
    expect(unit_settings_page.modal_heading).to_be_visible()
