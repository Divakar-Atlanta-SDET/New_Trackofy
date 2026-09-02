import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    # Sensor names are JS-truncated in the Custom Sensors table (a literal "..."
    # is appended to the stored string, not just CSS-clipped), so long generated
    # names never match a full-text filter later -- keep these short.
    return f"{prefix}{int(time.time() * 1000) % 10000}"


@pytest.mark.negative
def test_tc117_save_sensor_without_configuration_name(unit_settings):
    """TC-117: Negative - Leave sensor name empty; Save Config stays blocked."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.select_sensor_type("Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    expect(unit_settings_page.save_sensor_btn).to_be_disabled()


@pytest.mark.negative
def test_tc118_save_sensor_without_sensor_type(unit_settings):
    """TC-118: Negative - Leave Sensor Type unselected; Save Config stays blocked."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.sensor_name_input.fill(_unique_name("ATNoT"))
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    expect(unit_settings_page.save_sensor_btn).to_be_disabled()


@pytest.mark.negative
def test_tc119_invalid_calibration_value(unit_settings):
    """TC-119: Negative - Enter non-numeric calibration data; value is rejected by the numeric input."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(_unique_name("ATBCa"), "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    # A native <input type="number"> refuses non-numeric text outright rather
    # than accepting and clearing it -- Playwright raises for that case, which
    # itself demonstrates the field correctly rejects invalid input.
    with pytest.raises(Exception):
        unit_settings_page.adc_spin.first.fill("abc")
    assert unit_settings_page.adc_spin.first.input_value() == ""


@pytest.mark.negative
def test_tc120_invalid_configuration_expression(unit_settings):
    """TC-120: Negative - Enter a malformed configuration expression; Save Config is blocked."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(_unique_name("ATBEx"), "Gauge")
    unit_settings_page.config_expression_input.fill("not a valid expression @@@")
    unit_settings_page.fill_calibration_row(0, "10", "20")
    unit_settings_page.page.wait_for_timeout(300)
    assert not unit_settings_page.save_sensor_btn.is_enabled() or unit_settings_page.has_validation_error(), (
        "A malformed expression must block save or show a validation error"
    )


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_tc121_backend_failure_while_saving_sensor(unit_settings):
    """TC-121: Negative - Submit a valid sensor while the save API fails; not falsely reported as created."""
    unit_page, unit_settings_page = unit_settings
    name = _unique_name("ATAPI")
    unit_settings_page.open_add_sensor_form()
    unit_settings_page.fill_sensor_basic_info(name, "Gauge")
    unit_settings_page.config_expression_input.fill("val(unit)|ADC")
    unit_settings_page.fill_calibration_row(0, "10", "20")

    unit_settings_page.page.route(
        "**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error")
    )
    unit_settings_page.save_sensor_btn.click()
    unit_settings_page.page.wait_for_timeout(1500)
    unit_settings_page.page.unroute("**/api/**")

    # The Sensor Configuration dialog only closes via its own Cancel button
    # after a failed save -- Escape alone leaves it (and its backdrop) open,
    # blocking clicks on the tab underneath.
    unit_settings_page.cancel_sensor_btn.click()
    unit_settings_page.page.wait_for_timeout(500)
    unit_settings_page.custom_sensors_tab.click()
    unit_settings_page.wait_for_loading_to_finish()
    assert unit_settings_page.get_custom_sensor_row(name).count() == 0, (
        "Sensor must not appear as created when the save request failed"
    )
