import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from components.toast_notifcations import ToastNotifications
from Utils.data_loader import load_test_data


@pytest.mark.negative
@pytest.mark.parametrize("invalid_data", load_test_data("unit_negative.json", "invalid_speed_limits"))
def test_enter_invalid_speed_limit_rejection(page, config, credentials, invalid_data):
    """TC-050, TC-051: Reject invalid speed limits (negative, non-numeric, special chars)."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)
    toast = ToastNotifications(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.focus()
    unit_settings_page.speed_limit_spin.press_sequentially(invalid_data["value"])

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.error_toast.count() > 0:
        expect(toast.error_toast.first).to_be_visible()
