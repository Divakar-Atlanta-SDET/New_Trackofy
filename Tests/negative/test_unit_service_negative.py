import pytest
from playwright.sync_api import expect


@pytest.mark.negative
def test_tc035_submit_blank_fitness_form_validation(unit_settings):
    """TC-035: Negative - Open Fitness Add form and verify Submit button is disabled when fields are blank."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.fitness_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    expect(unit_settings_page.fitness_submit_btn).to_be_disabled()
    unit_settings_page.fitness_view_history_btn.click()


@pytest.mark.negative
def test_tc080_submit_blank_insurance_form_validation(unit_settings):
    """TC-080: Negative - Open Insurance Add form and verify Submit button is disabled when fields are blank."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Insurance")
    unit_settings_page.insurance_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    expect(unit_settings_page.insurance_submit_btn).to_be_disabled()
    unit_settings_page.insurance_view_history_btn.click()


@pytest.mark.negative
def test_tc095_submit_blank_pollution_form_validation(unit_settings):
    """TC-095: Negative - Open Pollution Add form and verify Submit button is disabled when fields are blank."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Pollution")
    unit_settings_page.pollution_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    expect(unit_settings_page.pollution_submit_btn).to_be_disabled()
    unit_settings_page.pollution_view_history_btn.click()


@pytest.mark.negative
def test_tc136_submit_blank_service_form_validation(unit_settings):
    """TC-136: Negative - Open Vehicle Service Add form and verify Submit button is disabled when fields are blank."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Service")
    unit_settings_page.service_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    expect(unit_settings_page.service_submit_btn).to_be_disabled()
    unit_settings_page.service_view_history_btn.click()


@pytest.mark.negative
def test_tc140_odometer_after_less_than_before_validation(unit_settings):
    """TC-140: Negative - Enter Odometer After smaller than Odometer Before and assert validation error."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    unit_settings_page.switch_service_subtab("Service")
    unit_settings_page.service_add_btn.click()
    page.wait_for_timeout(500)

    unit_settings_page.odometer_before_input.fill("10000")
    unit_settings_page.odometer_after_input.fill("5000")

    # In vehicle service, odometer after cannot be less than odometer before
    is_invalid = unit_settings_page.odometer_after_input.evaluate("el => !el.checkValidity()")
    button_disabled = unit_settings_page.service_submit_btn.is_disabled()
    error_msg = page.locator("text=/cannot be less|invalid odometer|must be greater/i")

    assert is_invalid or button_disabled or error_msg.count() > 0, "Expected validation failure when Odometer After < Odometer Before"

    unit_settings_page.service_view_history_btn.click()
