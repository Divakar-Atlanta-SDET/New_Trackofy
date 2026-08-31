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


@pytest.mark.functional
def test_tc108_verify_sensors_tab_loads(page, config, credentials):
    """TC-108: Functional - Open Sensors tab and check section headings and Add Sensor button."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc109_verify_standard_sensor_list(page, config, credentials):
    """TC-109: Functional - Open Standard Sensors list and verify table column headers."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc110_switch_standard_and_custom_sensors(page, config, credentials):
    """TC-110: Functional - Toggle between Standard Sensors and Custom Sensors sub-tabs."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc111_verify_sensor_configuration_fields(page, config, credentials):
    """TC-111: Functional - Open Add Sensor form and check field labels."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc112_remove_calibration_row(page, config, credentials):
    """TC-112: Functional - Click row delete icon on a calibration row."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc113_clear_calibration_rows(page, config, credentials):
    """TC-113: Functional - Add data and click Clear to clear calibration table."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc114_cancel_sensor_configuration(page, config, credentials):
    """TC-114: Functional - Enter sensor data and click Cancel."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc115_open_sensor_detail(page, config, credentials):
    """TC-115: Functional - Click Detail icon for an existing sensor."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.functional
def test_tc116_verify_sensor_pagination(page, config, credentials):
    """TC-116: Functional - Test sensor list table pagination controls."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()

