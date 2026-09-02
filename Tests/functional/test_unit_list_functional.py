import pytest
from playwright.sync_api import expect

from Pages.unit_page import UnitPage
from Utils.data_loader import load_test_data


@pytest.mark.functional
def test_unit_list_page_loads_and_displays_table_and_count(authenticated_page):
    """TC-011: Verify Unit List loads successfully and displays unit count badge."""
    unit_page = UnitPage(authenticated_page)
    unit_page.open_unit_list()

    expect(unit_page.unit_list_heading).to_be_visible()
    expect(unit_page.unit_count_badge).to_be_visible()
    expect(unit_page.table).to_be_visible()
    assert unit_page.get_unit_count() > 0


@pytest.mark.functional
@pytest.mark.parametrize("filter_data", load_test_data("unit_functional.json", "unit_type_filters"))
def test_unit_list_type_filters(authenticated_page, filter_data):
    """TC-024: Functional - Filter Unit list by parametrized unit types (Car, Bus, Truck, Scooty)."""
    unit_page = UnitPage(authenticated_page)
    unit_page.open_unit_list()
    unit_page.filter_by_unit_type(filter_data["unit_type"])
    expect(unit_page.table).to_be_visible()


@pytest.mark.functional
def test_open_and_switch_unit_settings_tabs(unit_settings):
    """TC-013, TC-014: Open Unit Settings modal, switch all tabs, and close."""
    unit_page, unit_settings_page = unit_settings

    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("Service")
    unit_settings_page.switch_tab("Alert")
    unit_settings_page.switch_tab("General")

    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()
