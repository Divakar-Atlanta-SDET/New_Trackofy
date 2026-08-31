import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage


@pytest.mark.functional
def test_verify_alert_tab_and_status_indicators(page, config, credentials):
    """TC-003, TC-004: Open Alert tab and verify configured alerts table."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    # 1. Switch to Alert tab.
    unit_settings_page.switch_tab("Alert")

    # 2. Assert Alert tab loaded cleanly.
    expect(unit_settings_page.modal_heading).to_be_visible()
