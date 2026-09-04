import pytest
from playwright.sync_api import expect


@pytest.mark.negative
def test_set_058_category_is_mandatory(driver_performance_page):
    """SET-058: Leaving Category unselected blocks Save Configuration."""
    driver_performance_page.open_configure_form()
    driver_performance_page.select_parameter("Overspeed Limit")
    driver_performance_page.configure_parameter("Overspeed Limit", Limit="60", Count="2")
    # A missing category must at least block Save; the "Category is required"
    # message only appears once the field is touched/blurred, confirmed live,
    # so the disabled-Save state is the reliable, always-true signal here.
    expect(driver_performance_page.save_btn).to_be_disabled()


@pytest.mark.negative
def test_set_061_reject_invalid_range(driver_performance_page):
    """SET-061: Minimum greater than Maximum is rejected."""
    driver_performance_page.open_configure_form()
    categories = driver_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    driver_performance_page.select_category(categories[0])
    driver_performance_page.select_parameter("Distance Range")
    driver_performance_page.configure_parameter("Distance Range", Minimum="100", Maximum="50")
    expect(driver_performance_page.save_btn).to_be_disabled()
    driver_performance_page.close_dialog()
