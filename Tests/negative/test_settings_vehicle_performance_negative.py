import pytest
from playwright.sync_api import expect


@pytest.mark.negative
def test_set_077_category_mandatory(vehicle_performance_page):
    """SET-077: Leaving Category blank blocks Create Performance."""
    vehicle_performance_page.open_configure_form()
    vehicle_performance_page.set_range("distance", 50, 200)
    expect(vehicle_performance_page.create_btn).to_be_disabled()
    vehicle_performance_page.close_dialog()


@pytest.mark.negative
def test_set_078_min_greater_than_max_rejected(vehicle_performance_page):
    """SET-078: Setting minimum greater than maximum is rejected."""
    vehicle_performance_page.open_configure_form()
    categories = vehicle_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    vehicle_performance_page.select_category(categories[0])
    # Push the min thumb up while the max thumb stays put; a real dual-range
    # slider must keep min <= max on its own (this is only a "did the UI
    # clamp it" check via what the min thumb actually reports afterward,
    # since a raw programmatic set can't visually drag past the max thumb).
    vehicle_performance_page._set_slider(vehicle_performance_page.min_sliders["distance"], 999)
    vehicle_performance_page.page.wait_for_timeout(300)
    min_value = vehicle_performance_page.read_slider_value(vehicle_performance_page.min_sliders["distance"])
    max_value = vehicle_performance_page.read_slider_value(vehicle_performance_page.max_sliders["distance"])
    assert min_value <= max_value, (
        f"Minimum ({min_value}) must never be allowed to exceed Maximum ({max_value})"
    )
    vehicle_performance_page.close_dialog()
