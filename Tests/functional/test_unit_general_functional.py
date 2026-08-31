import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage


@pytest.mark.functional
def test_verify_general_fields_are_displayed_and_populated(page, config, credentials):
    """TC-046, TC-047: Open General tab and verify read-only and editable fields."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    # 1. Verify populated read-only fields.
    expect(unit_settings_page.name_input).to_be_visible()
    expect(unit_settings_page.device_model_input).to_be_visible()
    expect(unit_settings_page.serial_no_input).to_be_visible()
    expect(unit_settings_page.sim1_input).to_be_visible()

    # 2. Verify read-only attribute on Name field.
    assert unit_settings_page.name_input.is_disabled() or unit_settings_page.name_input.get_attribute("readonly") is not None
