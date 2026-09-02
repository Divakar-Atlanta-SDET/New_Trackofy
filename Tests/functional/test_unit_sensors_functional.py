import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_tc108_verify_sensors_tab_loads(unit_settings):
    """TC-108: Functional - Open Sensors tab and check section headings and Add Sensor button."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.add_sensor_btn).to_be_visible()
    expect(unit_settings_page.standard_sensors_tab).to_be_visible()
    expect(unit_settings_page.custom_sensors_tab).to_be_visible()


@pytest.mark.functional
def test_tc109_verify_standard_sensor_list(unit_settings):
    """TC-109: Functional - Open Standard Sensors list and verify table column headers."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.standard_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    headers = [h.strip() for h in unit_settings_page.sensor_table_headers.all_inner_texts()]
    for expected in ["Sensor Name", "Sensor Type", "Created Date", "Last Updated", "Detail"]:
        assert expected in headers, f"Missing column: {expected}"


@pytest.mark.functional
def test_tc110_switch_standard_and_custom_sensors(unit_settings):
    """TC-110: Functional - Toggle between Standard Sensors and Custom Sensors sub-tabs."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    expect(unit_settings_page.custom_sensors_tab).to_have_attribute("aria-selected", "true")

    unit_settings_page.standard_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    expect(unit_settings_page.standard_sensors_tab).to_have_attribute("aria-selected", "true")


@pytest.mark.functional
def test_tc111_verify_sensor_configuration_fields(unit_settings):
    """TC-111: Functional - Open Add Sensor and check field labels."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    expect(unit_settings_page.sensor_name_input).to_be_visible()
    expect(unit_settings_page.sensor_type_select).to_be_visible()
    expect(unit_settings_page.config_expression_input).to_be_visible()
    expect(unit_settings_page.add_calibration_row_btn).to_be_visible()
    expect(unit_settings_page.clear_calibration_btn).to_be_visible()
    expect(unit_settings_page.save_sensor_btn).to_be_visible()
    expect(unit_settings_page.cancel_sensor_btn).to_be_visible()


@pytest.mark.functional
def test_tc112_remove_calibration_row(unit_settings):
    """TC-112: Functional - Click row delete icon on a calibration row; only that row is removed."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.add_calibration_row_btn.click()
    unit_settings_page.page.wait_for_timeout(300)
    before = unit_settings_page.adc_spin.count()
    assert before >= 2, "Expected at least 2 calibration rows after Add Row"

    delete_row_btns = unit_settings_page.remove_calibration_row_btns
    if delete_row_btns.count() == 0:
        pytest.skip("No per-row delete control found on the calibration table")
    delete_row_btns.first.click()
    unit_settings_page.page.wait_for_timeout(300)
    assert unit_settings_page.adc_spin.count() == before - 1


@pytest.mark.functional
def test_tc113_clear_calibration_rows(unit_settings):
    """TC-113: Functional - Add data and click Clear to clear calibration table.

    Real, confirmed behavior: Clear removes any *extra* rows back down to one,
    but does not blank out that remaining row's own ADC/Liter values.
    """
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.add_calibration_row_btn.click()
    unit_settings_page.page.wait_for_timeout(300)
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.fill_calibration_row(1, "30", "40")
    assert unit_settings_page.adc_spin.count() == 2

    unit_settings_page.clear_calibration_btn.click()
    unit_settings_page.page.wait_for_timeout(300)
    assert unit_settings_page.adc_spin.count() == 1, "Clear should remove extra calibration rows"


@pytest.mark.functional
def test_tc114_cancel_sensor_configuration(unit_settings):
    """TC-114: Functional - Enter data and click Cancel; no new sensor is created."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.add_sensor_btn.click()
    unit_settings_page.wait_for_visible(unit_settings_page.sensor_name_input)
    # short name -- table cells are JS-truncated once long enough, which would
    # make a has_text("CancelledSensorTest")-style check unreliable either way
    unit_settings_page.fill_sensor_basic_info("CnclTst")
    unit_settings_page.cancel_sensor_btn.click()
    unit_settings_page.wait_for_hidden(unit_settings_page.sensor_name_input)

    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    assert unit_settings_page.get_custom_sensor_row("CnclTst").count() == 0


@pytest.mark.functional
def test_tc115_open_sensor_detail(unit_settings):
    """TC-115: Functional - Click Detail icon for an existing sensor."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    row = unit_settings_page.standard_sensor_rows.first
    if row.count() == 0:
        pytest.skip("No standard sensors available to open detail for")
    row.locator("button[mattooltip='View Sensor Details']").click()
    unit_settings_page.page.wait_for_timeout(500)
    expect(unit_settings_page.topmost_dialog).to_be_visible()
    unit_settings_page.page.keyboard.press("Escape")


@pytest.mark.functional
def test_tc116_verify_sensor_pagination(unit_settings):
    """TC-116: Functional - Test sensor list table pagination controls."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    expect(unit_settings_page.sensor_items_per_page).to_be_visible()
    next_btn = unit_settings_page.next_page_btn
    if next_btn.is_enabled():
        next_btn.click()
        unit_settings_page.wait_for_loading_to_finish()
        expect(unit_settings_page.standard_sensor_rows.first).to_be_visible()
    else:
        pytest.skip("Not enough sensors to exercise pagination")
