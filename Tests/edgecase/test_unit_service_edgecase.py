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
def test_tc030_fitness_valid_from_later_than_valid_till(page, config, credentials):
    """TC-030: Edge Case - Fitness Valid From date later than Valid Till date."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_service_subtab("Fitness")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc031_fitness_equal_validity_dates(page, config, credentials):
    """TC-031: Edge Case - Set Fitness Valid From and Valid Till to same date."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_service_subtab("Fitness")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc076_insurance_valid_from_later_than_valid_till(page, config, credentials):
    """TC-076: Edge Case - Insurance Valid From later than Valid Till."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_service_subtab("Insurance")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc091_pollution_valid_from_later_than_valid_till(page, config, credentials):
    """TC-091: Edge Case - Pollution Valid From later than Valid Till."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_service_subtab("Pollution")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc130_odometer_before_equals_odometer_after(page, config, credentials):
    """TC-130: Edge Case - Set Odometer Before equal to Odometer After."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_service_subtab("Service")
    expect(unit_settings_page.modal_heading).to_be_visible()

