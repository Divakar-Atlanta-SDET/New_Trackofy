import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from Utils.data_loader import load_test_data


@pytest.mark.functional
def test_unit_list_page_loads_and_displays_table_and_count(page, config, credentials):
    """TC-011: Verify Unit List loads successfully and displays unit count badge."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()

    expect(unit_page.unit_list_heading).to_be_visible()
    expect(unit_page.unit_count_badge).to_be_visible()
    expect(unit_page.table).to_be_visible()
    assert unit_page.get_unit_count() > 0


@pytest.mark.functional
@pytest.mark.parametrize("filter_data", load_test_data("unit_functional.json", "unit_type_filters"))
def test_unit_list_type_filters(page, config, credentials, filter_data):
    """TC-024: Functional - Filter Unit list by parametrized unit types (Car, Bus, Truck, Scooty)."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.filter_by_unit_type(filter_data["unit_type"])
    expect(unit_page.table).to_be_visible()


@pytest.mark.functional
def test_open_and_switch_unit_settings_tabs(page, config, credentials):
    """TC-013, TC-014: Open Unit Settings modal, switch all tabs, and close."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("Service")
    unit_settings_page.switch_tab("Alert")
    unit_settings_page.switch_tab("General")

    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()
