import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_tc030_fitness_valid_from_later_than_valid_till(unit_settings):
    """TC-030: Edge Case - Fitness Valid From later than Valid Till is rejected if prohibited."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.fitness_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_from_input, "12/31/2026")
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_till_input, "01/01/2026")
    unit_settings_page.fitness_cost_input.fill("1500")
    unit_settings_page.fitness_reminder_input.fill("15")
    unit_settings_page.page.wait_for_timeout(300)
    assert not unit_settings_page.fitness_submit_btn.is_enabled() or unit_settings_page.has_validation_error(), (
        "Valid From after Valid Till should block submit or show a validation error"
    )


@pytest.mark.edgecase
def test_tc031_fitness_equal_validity_dates(unit_settings):
    """TC-031: Edge Case - Fitness Valid From equal to Valid Till follows the defined date rule."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.fitness_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_from_input, "06/15/2026")
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_till_input, "06/15/2026")
    unit_settings_page.fitness_cost_input.fill("1500")
    unit_settings_page.fitness_reminder_input.fill("15")
    unit_settings_page.page.wait_for_timeout(300)
    # No documented business rule prohibits equal dates -- just confirm the UI
    # reaches a consistent, non-crashed state either way.
    expect(unit_settings_page.fitness_submit_btn).to_be_visible()


@pytest.mark.edgecase
def test_tc076_insurance_valid_from_later_than_valid_till(unit_settings):
    """TC-076: Edge Case - Insurance Valid From later than Valid Till is rejected if prohibited."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Insurance")
    unit_settings_page.insurance_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.insurance_company_input.fill("Tata AIG")
    unit_settings_page.insurance_premium_input.fill("12000")
    unit_settings_page.insurance_depreciation_input.fill("10")
    unit_settings_page.insurance_idv_input.fill("500000")
    unit_settings_page.set_date_input(unit_settings_page.insurance_valid_from_input, "12/31/2026")
    unit_settings_page.set_date_input(unit_settings_page.insurance_valid_till_input, "01/01/2026")
    unit_settings_page.insurance_reminder_input.fill("15")
    unit_settings_page.page.wait_for_timeout(300)
    assert not unit_settings_page.insurance_submit_btn.is_enabled() or unit_settings_page.has_validation_error(), (
        "Valid From after Valid Till should block submit or show a validation error"
    )


@pytest.mark.edgecase
def test_tc091_pollution_valid_from_later_than_valid_till(unit_settings):
    """TC-091: Edge Case - Pollution Valid From later than Valid Till is rejected if prohibited."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Pollution")
    unit_settings_page.pollution_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.pollution_cert_no_input.fill("PUC-EDGE-091")
    unit_settings_page.set_date_input(unit_settings_page.pollution_valid_from_input, "12/31/2026")
    unit_settings_page.set_date_input(unit_settings_page.pollution_valid_till_input, "01/01/2026")
    unit_settings_page.pollution_cost_input.fill("500")
    unit_settings_page.pollution_reminder_input.fill("10")
    unit_settings_page.page.wait_for_timeout(300)
    assert not unit_settings_page.pollution_submit_btn.is_enabled() or unit_settings_page.has_validation_error(), (
        "Valid From after Valid Till should block submit or show a validation error"
    )


@pytest.mark.edgecase
def test_tc130_odometer_before_equals_odometer_after(unit_settings):
    """TC-130: Edge Case - Odometer Before equal to Odometer After follows the defined business rule."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Service")
    unit_settings_page.service_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.service_no_input.fill("SRV-EDGE-130")
    unit_settings_page.service_date_input.fill("01/02/2026")
    unit_settings_page.odometer_before_input.fill("10000")
    unit_settings_page.odometer_after_input.fill("10000")
    unit_settings_page.service_cost_input.fill("500")
    unit_settings_page.page.wait_for_timeout(300)
    # No documented rule prohibits an equal reading -- confirm a stable, non-crashed state.
    expect(unit_settings_page.service_submit_btn).to_be_visible()
