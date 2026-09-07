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

    entered_value = unit_settings_page.speed_limit_spin.input_value()
    if entered_value != invalid_data["value"]:
        # A native <input type="number"> refused the keystrokes outright
        # (e.g. non-numeric characters) -- that IS the rejection.
        return

    # The value was accepted at the DOM level (e.g. a negative number, which
    # a plain type="number" input allows) -- the app must still reject it via
    # native constraint validation, a disabled Update, or a visible error.
    is_invalid = unit_settings_page.speed_limit_spin.evaluate("el => !el.checkValidity()")
    update_blocked = not unit_settings_page.update_btn.is_enabled()
    assert is_invalid or update_blocked or unit_settings_page.has_validation_error() or toast.error_toast.count() > 0, (
        f"Expected the invalid speed limit {invalid_data['value']!r} ({invalid_data['description']}) "
        "to be rejected via input validity, a disabled Update, or a validation error"
    )
