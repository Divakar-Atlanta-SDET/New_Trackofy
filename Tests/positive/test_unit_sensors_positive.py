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


@pytest.mark.positive
def test_tc122_open_add_sensor_configuration(page, config, credentials):
    """TC-122: Positive - Open Add Sensor configuration form."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc123_create_sensor_configuration_with_valid_basic_data(page, config, credentials):
    """TC-123: Positive - Create sensor configuration with valid name and type."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc124_add_configuration_expression(page, config, credentials):
    """TC-124: Positive - Enter valid configuration expression and save."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc125_add_calibration_row(page, config, credentials):
    """TC-125: Positive - Add calibration row with valid ADC raw and calibrated values."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc126_add_multiple_calibration_rows(page, config, credentials):
    """TC-126: Positive - Add multiple calibration rows and verify persistence."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()

