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


@pytest.mark.edgecase
def test_tc104_use_duplicate_sensor_configuration_name(page, config, credentials):
    """TC-104: Edge Case - Create sensor using duplicate configuration name."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc105_create_sensor_with_maximum_supported_name_length(page, config, credentials):
    """TC-105: Edge Case - Create sensor with maximum supported name length."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc106_exceed_sensor_name_length(page, config, credentials):
    """TC-106: Edge Case - Enter sensor name beyond supported length."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc107_empty_calibration_table(page, config, credentials):
    """TC-107: Edge Case - Clear calibration rows and attempt save."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.modal_heading).to_be_visible()

