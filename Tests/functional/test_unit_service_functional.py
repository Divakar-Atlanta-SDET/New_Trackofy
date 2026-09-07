import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_verify_service_subtabs_navigation(unit_settings):
    """TC-127, TC-128: Open Service tab and switch between sub-tabs;
    each sub-tab shows its own real content, not just a stable modal."""
    unit_page, unit_settings_page = unit_settings

    unit_settings_page.switch_service_subtab("Fitness")
    expect(unit_settings_page.fitness_history_heading).to_be_visible()

    unit_settings_page.switch_service_subtab("Pollution")
    expect(unit_settings_page.pollution_history_heading).to_be_visible()

    unit_settings_page.switch_service_subtab("Insurance")
    expect(unit_settings_page.insurance_history_heading).to_be_visible()

    unit_settings_page.switch_service_subtab("Service")
    expect(unit_settings_page.service_history_heading).to_be_visible()
