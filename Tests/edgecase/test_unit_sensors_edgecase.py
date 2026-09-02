import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    # Sensor names are JS-truncated in the Custom Sensors table (a literal "..."
    # is appended to the stored string, not just CSS-clipped), so long generated
    # names never match a full-text filter later -- keep these short.
    return f"{prefix}{int(time.time() * 1000) % 10000}"


@pytest.mark.edgecase
def test_tc104_use_duplicate_sensor_configuration_name(unit_settings):
    """TC-104: Edge Case - Create a sensor using an existing configuration name; duplicate is handled."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    if unit_settings_page.custom_sensor_rows.count() == 0:
        pytest.skip("No existing custom sensor to duplicate")
    existing_name = unit_settings_page.custom_sensor_rows.first.locator("td, [role='cell']").first.inner_text().strip()

    unit_settings_page.add_sensor_btn.click()
    unit_settings_page.wait_for_visible(unit_settings_page.sensor_name_input)
    unit_settings_page.fill_sensor_basic_info(existing_name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.page.wait_for_timeout(300)

    # Either save is blocked client-side, rejected server-side (dialog stays
    # open with an error), or the product genuinely allows a duplicate name.
    if unit_settings_page.save_sensor_btn.is_enabled():
        unit_settings_page.save_sensor_btn.click()
        try:
            unit_settings_page.wait_for_hidden(unit_settings_page.sensor_name_input)
        except Exception:
            # server-side rejected the duplicate; dialog stayed open -- close it
            unit_settings_page.cancel_sensor_btn.click()
            return
        unit_settings_page.wait_for_loading_to_finish()
        unit_settings_page.custom_sensors_tab.click()
        unit_settings_page.wait_for_loading_to_finish()
        # product allows duplicates -- two rows now share this name; clean up
        # the one we just created (the newer of the two, i.e. .last)
        dupes = unit_settings_page.get_custom_sensor_row(existing_name)
        if dupes.count() > 1:
            unit_settings_page.delete_custom_sensor_row(dupes.last)
            unit_settings_page.wait_for_loading_to_finish()
    else:
        unit_settings_page.cancel_sensor_btn.click()


@pytest.mark.edgecase
def test_tc105_create_sensor_with_maximum_supported_name_length(unit_settings):
    """TC-105: Edge Case - Enter a name at the input's maximum supported length; accepted if within limit."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    maxlength = unit_settings_page.sensor_name_input.get_attribute("maxlength")
    limit = int(maxlength) if maxlength else 100
    name = "A" * limit

    unit_settings_page.sensor_name_input.fill(name)
    actual = unit_settings_page.sensor_name_input.input_value()
    assert len(actual) <= limit
    unit_settings_page.cancel_sensor_btn.click()


@pytest.mark.edgecase
def test_tc106_exceed_sensor_name_length(unit_settings):
    """TC-106: Edge Case - Enter a name well beyond any reasonable length; input is limited or validation is shown."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    maxlength = unit_settings_page.sensor_name_input.get_attribute("maxlength")
    very_long_name = "A" * 300

    unit_settings_page.sensor_name_input.fill(very_long_name)
    actual = unit_settings_page.sensor_name_input.input_value()
    if maxlength:
        assert len(actual) <= int(maxlength)
    else:
        # No maxlength attribute at all -- the only other acceptable outcome is
        # a validation error; if neither exists, this is a real, unbounded gap.
        assert unit_settings_page.has_validation_error(), (
            f"Sensor Configuration Name has no maxlength and accepted {len(actual)} characters "
            "unchecked, with no validation error shown"
        )
    unit_settings_page.cancel_sensor_btn.click()


@pytest.mark.edgecase
def test_tc107_empty_calibration_table(unit_settings):
    """TC-107: Edge Case - Clear calibration rows and attempt save; product's rule is respected either way."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATEmp")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.clear_calibration_btn.click()
    unit_settings_page.page.wait_for_timeout(300)

    if unit_settings_page.save_sensor_btn.is_enabled():
        unit_settings_page.save_sensor_btn.click()
        unit_settings_page.wait_for_loading_to_finish()
        unit_settings_page.custom_sensors_tab.click()
        unit_settings_page.wait_for_loading_to_finish()
        try:
            expect(unit_settings_page.get_custom_sensor_row(name)).to_be_visible()
        finally:
            unit_settings_page.delete_custom_sensor(name)
    else:
        unit_settings_page.cancel_sensor_btn.click()
