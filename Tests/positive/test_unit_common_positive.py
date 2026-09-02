import pytest
from playwright.sync_api import expect


@pytest.mark.positive
def test_tc009_verify_active_alerts_are_displayed(unit_settings):
    """TC-009: Positive - Open Alert tab for a vehicle with active alerts and verify they're listed."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Alert")
    expect(unit_settings_page.alert_heading).to_be_visible()
    expect(unit_settings_page.alert_count_badge).to_be_visible()
    match = __import__("re").search(r"\d+", unit_settings_page.alert_count_badge.inner_text())
    if match and int(match.group()) > 0:
        expect(unit_settings_page.alert_rows.first).to_be_visible()


@pytest.mark.positive
def test_tc017_reload_settings_and_retain_saved_data(unit_settings):
    """TC-017: Positive - Update a General setting, save, close, reopen; saved value persists."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()
    new_value = "55" if original_value != "55" else "56"

    unit_settings_page.speed_limit_spin.fill(new_value)
    expect(unit_settings_page.update_btn).to_be_enabled()
    unit_settings_page.update_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.close_modal()

    try:
        unit_page.open_unit_settings_by_index(0)
        unit_settings_page.wait_for_modal_open()
        unit_settings_page.switch_tab("General")
        # The backend echoes numeric fields back reformatted (e.g. "55" -> "55.0"),
        # so compare numerically rather than expecting an exact string match.
        assert float(unit_settings_page.speed_limit_spin.input_value()) == float(new_value)
    finally:
        unit_settings_page.speed_limit_spin.fill(original_value)
        if unit_settings_page.update_btn.is_enabled():
            unit_settings_page.update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()
