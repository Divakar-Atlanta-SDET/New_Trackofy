import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    # Sensor names are JS-truncated in the Custom Sensors table (a literal "..."
    # is appended to the stored string, not just CSS-clipped), so long generated
    # names never match a full-text filter later -- keep these short.
    return f"{prefix}{int(time.time() * 1000) % 10000}"


@pytest.mark.positive
def test_tc122_open_add_sensor_configuration(unit_settings):
    """TC-122: Positive - Click Add Sensor and verify the Sensor Configuration form opens."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    expect(unit_settings_page.sensor_config_heading).to_be_visible()


@pytest.mark.positive
def test_tc123_create_sensor_configuration_with_valid_basic_data(unit_settings):
    """TC-123: Positive - Create sensor configuration with valid name/type/expression/calibration; verify saved."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATBas")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("value(unit)|ADC*0.1")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    expect(unit_settings_page.save_sensor_btn).to_be_enabled()
    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    try:
        expect(unit_settings_page.get_custom_sensor_row(name)).to_be_visible()
    finally:
        unit_settings_page.delete_custom_sensor(name)


@pytest.mark.positive
def test_tc124_add_configuration_expression(unit_settings):
    """TC-124: Positive - Enter a valid configuration expression, save, and verify it persisted."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATExp")
    expression = "temp(C)|ADC*0.5"
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill(expression)
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    try:
        row = unit_settings_page.get_custom_sensor_row(name)
        expect(row).to_be_visible()
        row.locator("button[mattooltip='View Sensor Details']").click()
        detail = unit_settings_page.topmost_dialog
        expect(detail).to_contain_text(expression.split("|")[0].split("(")[0])
        unit_settings_page.page.keyboard.press("Escape")
    finally:
        unit_settings_page.delete_custom_sensor(name)


@pytest.mark.positive
def test_tc125_add_calibration_row(unit_settings):
    """TC-125: Positive - Add a calibration row with valid ADC/Liter values; row is retained."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATCal")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    assert unit_settings_page.adc_spin.first.input_value() == "10"
    assert unit_settings_page.liter_spin.first.input_value() == "20"
    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    try:
        expect(unit_settings_page.get_custom_sensor_row(name)).to_be_visible()
    finally:
        unit_settings_page.delete_custom_sensor(name)


@pytest.mark.positive
def test_edit_sensor_configuration(unit_settings):
    """Positive - Edit an existing custom sensor's calibration value and verify it's saved."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATEdt")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    try:
        unit_settings_page.open_edit_sensor_form(name)
        assert unit_settings_page.sensor_name_input.input_value() == name, (
            "Edit form should open pre-filled with the sensor's current values"
        )
        unit_settings_page.adc_spin.first.fill("99")
        expect(unit_settings_page.save_sensor_btn).to_be_enabled()
        unit_settings_page.save_sensor_btn.click()
        unit_settings_page.wait_for_loading_to_finish()

        # verify the edit persisted by reopening the form
        unit_settings_page.open_edit_sensor_form(name)
        assert unit_settings_page.adc_spin.first.input_value() == "99", (
            "Edited calibration value should persist after saving"
        )
        unit_settings_page.cancel_sensor_btn.click()
    finally:
        unit_settings_page.delete_custom_sensor(name)


@pytest.mark.positive
def test_tc126_add_multiple_calibration_rows(unit_settings):
    """TC-126: Positive - Add multiple calibration rows with valid values; all are displayed and saved."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATMul")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.add_calibration_row_btn.click()
    unit_settings_page.page.wait_for_timeout(300)
    unit_settings_page.fill_calibration_row(1, "30", "40")
    assert unit_settings_page.adc_spin.count() == 2

    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    try:
        expect(unit_settings_page.get_custom_sensor_row(name)).to_be_visible()
    finally:
        unit_settings_page.delete_custom_sensor(name)
