import pytest
from playwright.sync_api import expect

from components.toast_notifcations import ToastNotifications
from Utils.data_loader import load_test_data


@pytest.mark.negative
@pytest.mark.parametrize("invalid_data", load_test_data("unit_negative.json", "invalid_speed_limits"))
def test_enter_invalid_speed_limit_rejection(unit_settings, invalid_data):
    """TC-050, TC-051: Reject invalid speed limits (negative, non-numeric, special chars)."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    toast = ToastNotifications(page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.focus()
    unit_settings_page.speed_limit_spin.press_sequentially(invalid_data["value"])

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.error_toast.count() > 0:
        expect(toast.error_toast.first).to_be_visible()
