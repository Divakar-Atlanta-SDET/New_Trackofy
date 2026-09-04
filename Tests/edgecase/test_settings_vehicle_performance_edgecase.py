import pytest
from playwright.sync_api import expect

from Pages.vehicle_performance_page import PARAMETERS


@pytest.mark.edgecase
def test_set_079_range_boundary_values(vehicle_performance_page):
    """SET-079: Minimum and maximum allowed range values are accepted, matching
    the app's own configured limits (read live, not assumed)."""
    vehicle_performance_page.open_configure_form()
    for parameter in PARAMETERS:
        true_min, true_max = vehicle_performance_page.read_true_bounds(parameter)
        vehicle_performance_page.set_range(parameter, true_min, true_max)
        vehicle_performance_page.page.wait_for_timeout(200)
        assert vehicle_performance_page.read_slider_value(vehicle_performance_page.min_sliders[parameter]) == true_min
        assert vehicle_performance_page.read_slider_value(vehicle_performance_page.max_sliders[parameter]) == true_max
    vehicle_performance_page.close_dialog()
