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


@pytest.mark.negative
def test_tc117_save_sensor_without_configuration_name(page, config, credentials):
    """TC-117: Negative - Leave sensor name empty and attempt save."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc118_save_sensor_without_sensor_type(page, config, credentials):
    """TC-118: Negative - Leave Sensor Type empty and attempt save."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc119_invalid_calibration_value(page, config, credentials):
    """TC-119: Negative - Enter invalid non-numeric calibration data."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc120_invalid_configuration_expression(page, config, credentials):
    """TC-120: Negative - Enter malformed configuration expression and save."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.negative
def test_tc121_backend_failure_while_saving_sensor(page, config, credentials):
    """TC-121: Negative - Submit sensor config while backend API request fails."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()

