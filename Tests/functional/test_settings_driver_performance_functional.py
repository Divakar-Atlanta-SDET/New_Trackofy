import pytest
from playwright.sync_api import expect

from Pages.driver_performance_page import PARAMETERS


@pytest.mark.functional
def test_set_011_driver_performance_list_loads(driver_performance_page):
    """SET-011: Verify Driver Performance list loads without error."""
    expect(driver_performance_page.table).to_be_visible()


@pytest.mark.functional
def test_set_055_open_configure_form(driver_performance_page):
    """SET-055: Open Configure Driver Performance; category and parameter sections shown."""
    driver_performance_page.open_configure_form()
    expect(driver_performance_page.dialog).to_contain_text("Performance Parameters")
    expect(driver_performance_page.category_select).to_be_visible()
    expect(driver_performance_page.save_btn).to_be_disabled()


@pytest.mark.functional
def test_set_056_available_performance_parameters(driver_performance_page):
    """SET-056: Verify all documented performance parameters are offered."""
    driver_performance_page.open_configure_form()
    for parameter in PARAMETERS:
        expect(driver_performance_page.parameter_checkboxes[parameter]).to_be_visible()
