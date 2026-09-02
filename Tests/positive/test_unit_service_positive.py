import tempfile
import time
import pytest
from playwright.sync_api import expect


def _unique(prefix: str) -> str:
    # Table cells are JS-truncated once long enough (a literal "..." is baked
    # into the stored string, not just CSS-clipped), so keep these short.
    return f"{prefix}{int(time.time() * 1000) % 10000}"


def _dummy_pdf():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4 dummy cert")
        return f.name


@pytest.mark.positive
def test_tc038_submit_valid_fitness_certificate_data(unit_settings):
    """TC-038: Submit valid Fitness certificate data and verify it's saved to history."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Fitness")
    unit_settings_page.fitness_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    cost = str(1000 + int(time.time()) % 900)
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_from_input, "01/01/2026")
    unit_settings_page.set_date_input(unit_settings_page.fitness_valid_till_input, "12/31/2026")
    unit_settings_page.fitness_cost_input.fill(cost)
    unit_settings_page.fitness_reminder_input.fill("15")

    expect(unit_settings_page.fitness_submit_btn).to_be_enabled()
    unit_settings_page.fitness_submit_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.page.wait_for_timeout(1000)

    row = unit_settings_page.find_service_history_row_on_last_page(cost)
    try:
        expect(row).to_be_visible()
    finally:
        unit_settings_page.delete_service_history_row(row)


@pytest.mark.positive
def test_tc101_submit_valid_pollution_certificate(unit_settings):
    """TC-101: Fill valid Pollution certificate data (with file), submit, and verify saved to history."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Pollution")
    unit_settings_page.pollution_add_cert_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    cert_no = _unique("PUC")
    unit_settings_page.pollution_cert_no_input.fill(cert_no)
    unit_settings_page.set_date_input(unit_settings_page.pollution_valid_from_input, "01/01/2026")
    unit_settings_page.set_date_input(unit_settings_page.pollution_valid_till_input, "06/30/2026")
    unit_settings_page.pollution_cost_input.fill("500")
    unit_settings_page.pollution_reminder_input.fill("10")
    unit_settings_page.upload_certificate_file(_dummy_pdf())

    expect(unit_settings_page.pollution_submit_btn).to_be_enabled()
    unit_settings_page.pollution_submit_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.page.wait_for_timeout(1000)

    row = unit_settings_page.find_service_history_row_on_last_page(cert_no)
    try:
        expect(row).to_be_visible()
    finally:
        unit_settings_page.delete_service_history_row(row)


@pytest.mark.positive
def test_tc087_fill_valid_insurance_data(unit_settings):
    """TC-087: Fill valid Insurance data (with file), submit, and verify saved to history."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Insurance")
    unit_settings_page.insurance_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    company = _unique("InsCo")
    unit_settings_page.insurance_company_input.fill(company)
    unit_settings_page.insurance_premium_input.fill("12000")
    unit_settings_page.insurance_depreciation_input.fill("10")
    unit_settings_page.insurance_idv_input.fill("500000")
    unit_settings_page.set_date_input(unit_settings_page.insurance_valid_from_input, "01/01/2026")
    unit_settings_page.set_date_input(unit_settings_page.insurance_valid_till_input, "12/31/2026")
    unit_settings_page.insurance_reminder_input.fill("15")
    unit_settings_page.upload_certificate_file(_dummy_pdf())

    expect(unit_settings_page.insurance_submit_btn).to_be_enabled()
    unit_settings_page.insurance_submit_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.page.wait_for_timeout(1000)

    row = unit_settings_page.find_service_history_row_on_last_page(company)
    try:
        expect(row).to_be_visible()
    finally:
        unit_settings_page.delete_service_history_row(row)


@pytest.mark.positive
def test_tc145_tc146_fill_valid_service_data_and_parts(unit_settings):
    """TC-145, TC-146: Submit a valid Vehicle Service record with a part, and verify it's saved."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_service_subtab("Service")
    unit_settings_page.service_add_btn.click()
    unit_settings_page.page.wait_for_timeout(500)

    service_no = _unique("SRV")
    unit_settings_page.service_no_input.fill(service_no)
    unit_settings_page.service_date_input.fill("01/02/2026")
    unit_settings_page.odometer_before_input.fill("10000")
    unit_settings_page.odometer_after_input.fill("10500")
    unit_settings_page.service_cost_input.fill("3500")
    unit_settings_page.next_service_odometer_input.fill("15000")
    unit_settings_page.next_service_duration_input.fill("180")
    unit_settings_page.service_reminder_input.fill("15")

    if unit_settings_page.add_part_btn.is_visible():
        unit_settings_page.add_part_btn.click()
        unit_settings_page.page.wait_for_timeout(300)
        unit_settings_page.part_name_input.fill("Brake Pads")
        unit_settings_page.part_cost_input.fill("1200")

    expect(unit_settings_page.service_submit_btn).to_be_enabled()
    unit_settings_page.service_submit_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.page.wait_for_timeout(1000)

    row = unit_settings_page.find_service_history_row_on_last_page(service_no)
    try:
        expect(row).to_be_visible()
    finally:
        unit_settings_page.delete_service_history_row(row)
