import pytest
from playwright.sync_api import expect

from Utils.data_loader import load_test_data


@pytest.mark.edgecase
@pytest.mark.parametrize("boundary_data", load_test_data("unit_edgecase.json", "boundary_speed_limits"))
def test_boundary_speed_limits(unit_settings, boundary_data):
    """TC-039, TC-040: Edge Case - Boundary speed limits (0, 50.5) are accepted and persisted."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    try:
        unit_settings_page.update_speed_limit(boundary_data["value"])
        assert unit_settings_page.speed_limit_spin.input_value() == boundary_data["value"]
    finally:
        unit_settings_page.speed_limit_spin.fill(original_value)
        if unit_settings_page.update_btn.is_enabled():
            unit_settings_page.update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()


@pytest.mark.edgecase
@pytest.mark.parametrize("space_data", load_test_data("unit_edgecase.json", "whitespace_padded_inputs"))
def test_whitespace_padded_inputs(unit_settings, space_data):
    """TC-041: Edge Case - Leading/trailing whitespace in a numeric field is trimmed, not corrupted."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    try:
        unit_settings_page.update_speed_limit(space_data["value"])
        assert unit_settings_page.speed_limit_spin.input_value() == space_data["expected_trimmed"]
    finally:
        unit_settings_page.speed_limit_spin.fill(original_value)
        if unit_settings_page.update_btn.is_enabled():
            unit_settings_page.update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()


@pytest.mark.edgecase
def test_tc042_update_without_changing_any_value(unit_settings):
    """TC-042: Edge Case - Click Update without edits; existing values are not corrupted."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
        unit_settings_page.wait_for_loading_to_finish()
    assert unit_settings_page.speed_limit_spin.input_value() == original_value


@pytest.mark.edgecase
def test_tc043_change_colour_and_cancel_without_update(unit_settings):
    """TC-043: Edge Case - Change polyline colour but do not Update; close and reopen keeps original colour."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_colour = unit_settings_page.polyline_colour_input.input_value()
    new_colour = "#00ff00" if original_colour.lower() != "#00ff00" else "#ff00ff"

    unit_settings_page.polyline_colour_input.fill(new_colour)
    unit_settings_page.close_modal()

    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    unit_settings_page.switch_tab("General")
    assert unit_settings_page.polyline_colour_input.input_value().lower() == original_colour.lower(), (
        "Unsaved colour change must not persist after closing without Update"
    )
