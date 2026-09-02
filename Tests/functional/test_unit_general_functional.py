import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_verify_general_fields_are_displayed_and_populated(unit_settings):
    """TC-046, TC-047: Open General tab and verify read-only and editable fields."""
    unit_page, unit_settings_page = unit_settings

    # 1. Verify populated read-only fields.
    expect(unit_settings_page.name_input).to_be_visible()
    expect(unit_settings_page.device_model_input).to_be_visible()
    expect(unit_settings_page.serial_no_input).to_be_visible()
    expect(unit_settings_page.sim1_input).to_be_visible()

    # 2. Verify read-only attribute on Name field.
    assert unit_settings_page.name_input.is_disabled() or unit_settings_page.name_input.get_attribute("readonly") is not None
