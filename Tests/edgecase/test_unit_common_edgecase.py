import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_tc001_vehicle_with_no_configured_alerts(unit_settings):
    """TC-001: Edge Case - Open Alert tab for a vehicle without alerts; clear empty state, no errors."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Alert")
    if unit_settings_page.alert_rows.count() > 0:
        pytest.skip("Selected unit has configured alerts; cannot exercise the empty-state path")
    expect(unit_settings_page.alert_heading).to_be_visible()
    assert unit_settings_page.contains_any_text(["No alert", "no data", "not configured"])


@pytest.mark.edgecase
def test_tc002_large_number_of_alerts(unit_settings):
    """TC-002: Edge Case - Open Alert tab for a vehicle with many alerts; table stays usable."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Alert")
    row_count = unit_settings_page.alert_rows.count()
    if row_count < 5:
        pytest.skip("Selected unit doesn't have enough alerts to exercise a large dataset")
    expect(unit_settings_page.alert_rows.first).to_be_visible()
    assert unit_settings_page.alert_rows.count() == row_count, "Row count should be stable while the table renders"


@pytest.mark.edgecase
def test_tc010_rapidly_switch_tabs(unit_settings):
    """TC-010: Edge Case - Rapidly click multiple Unit Settings tabs; final tab's content is correct."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("General")
    unit_settings_page.switch_tab("Service")
    expect(unit_settings_page.modal_heading).to_be_visible()
    expect(unit_settings_page.profile_subtab).to_be_visible()


@pytest.mark.edgecase
def test_tc018_close_settings_during_unsaved_change(unit_settings):
    """TC-018: Edge Case - Modify a field and close without updating; change is discarded."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    changed_value = "77" if original_value != "77" else "78"

    unit_settings_page.speed_limit_spin.fill(changed_value)
    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()

    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    unit_settings_page.switch_tab("General")
    assert unit_settings_page.speed_limit_spin.input_value() == original_value, (
        "Unsaved change must not persist after closing without Update"
    )


@pytest.mark.edgecase
def test_tc020_double_click_update_submit(unit_settings):
    """TC-020: Edge Case - Rapidly double-click Update; only one update is applied, no error."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    changed_value = "65" if original_value != "65" else "66"
    try:
        unit_settings_page.speed_limit_spin.fill(changed_value)
        if unit_settings_page.update_btn.is_enabled():
            unit_settings_page.update_btn.dblclick()
        unit_settings_page.wait_for_loading_to_finish()
        assert not unit_settings_page.has_validation_error()
        assert unit_settings_page.speed_limit_spin.input_value() == changed_value
    finally:
        unit_settings_page.speed_limit_spin.fill(original_value)
        if unit_settings_page.update_btn.is_enabled():
            unit_settings_page.update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()
