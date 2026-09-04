import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_set_060_deselect_parameter(driver_performance_page):
    """SET-060: Deselecting a parameter removes it from the configuration; not saved unintentionally."""
    driver_performance_page.open_configure_form()
    driver_performance_page.select_parameter("Distance Range")
    expect(driver_performance_page.parameter_article("Distance Range")).to_be_visible()

    driver_performance_page.deselect_parameter("Distance Range")
    expect(driver_performance_page.parameter_article("Distance Range")).to_be_hidden()
