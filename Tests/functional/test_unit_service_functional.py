import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_verify_service_subtabs_navigation(unit_settings):
    """TC-127, TC-128: Open Service tab and switch between sub-tabs."""
    unit_page, unit_settings_page = unit_settings

    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.switch_service_subtab("Pollution")
    unit_settings_page.switch_service_subtab("Insurance")
    unit_settings_page.switch_service_subtab("Service")

    expect(unit_settings_page.modal_heading).to_be_visible()
