import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_trk_play_001_verify_default_playback_fields(tracking):
    """TRK-PLAY-001: Functional - Verify default Playback fields are displayed."""
    tracking.switch_to_playback_tracking()
    expect(tracking.vehicle_select).to_be_visible()
    expect(tracking.from_date_input).to_be_visible()
    expect(tracking.to_date_input).to_be_visible()
    expect(tracking.from_time_input).to_be_visible()
    expect(tracking.to_time_input).to_be_visible()
    expect(tracking.more_filters_btn).to_be_visible()
    expect(tracking.reset_btn).to_be_visible()
    expect(tracking.load_playback_btn).to_be_visible()


@pytest.mark.functional
def test_trk_play_006_007_open_calendar_pickers(tracking):
    """TRK-PLAY-006, 007: Functional - Open From Date and To Date calendar pickers."""
    tracking.switch_to_playback_tracking()
    expect(tracking.open_calendar_btns.first).to_be_visible()
    tracking.open_calendar_btns.first.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.page.locator(".mat-calendar, [role='dialog']").last).to_be_visible()
    tracking.page.keyboard.press("Escape")


@pytest.mark.functional
def test_trk_play_040_041_toggle_more_filters(tracking):
    """TRK-PLAY-040, 041: Functional - Open and close the More Filters panel."""
    tracking.switch_to_playback_tracking()
    expect(tracking.hold_time_select).to_be_hidden()
    tracking.toggle_more_filters()
    expect(tracking.hold_time_select).to_be_visible()
    expect(tracking.overspeeding_select).to_be_visible()
    tracking.toggle_more_filters()
    expect(tracking.hold_time_select).to_be_hidden()


@pytest.mark.functional
def test_trk_play_044_045_reset_playback_form(tracking):
    """TRK-PLAY-044, 045: Functional - Reset restores the pre-change baseline."""
    tracking.switch_to_playback_tracking()
    baseline_from_date = tracking.from_date_input.input_value()

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    expect(tracking.load_playback_btn).to_be_enabled()

    tracking.reset_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.load_playback_btn).to_be_disabled()
    assert tracking.from_date_input.input_value() == baseline_from_date
