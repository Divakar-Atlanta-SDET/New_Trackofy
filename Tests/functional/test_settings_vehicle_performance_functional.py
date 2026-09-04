import pytest
from playwright.sync_api import expect

from Pages.vehicle_performance_page import PARAMETERS


@pytest.mark.functional
def test_set_013_vehicle_performance_list_loads(vehicle_performance_page):
    """SET-013: Verify Vehicle Performance list loads without error."""
    expect(vehicle_performance_page.table).to_be_visible()


@pytest.mark.functional
def test_set_075_open_create_form(vehicle_performance_page):
    """SET-075: Open Create Unit Performance form; category and range sliders shown."""
    vehicle_performance_page.open_configure_form()
    expect(vehicle_performance_page.category_select).to_be_visible()
    for parameter in PARAMETERS:
        expect(vehicle_performance_page.min_sliders[parameter]).to_be_attached()
        expect(vehicle_performance_page.max_sliders[parameter]).to_be_attached()
    expect(vehicle_performance_page.create_btn).to_be_disabled()
