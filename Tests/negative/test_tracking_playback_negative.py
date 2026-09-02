import pytest
from playwright.sync_api import expect

from Utils.data_loader import load_test_data


@pytest.mark.negative
def test_trk_play_004_046_load_playback_missing_vehicle(tracking):
    """TRK-PLAY-004, 046: Negative - Attempt Load Playback without selecting a vehicle."""
    tracking.switch_to_playback_tracking()
    expect(tracking.load_playback_btn).to_be_disabled()


@pytest.mark.negative
@pytest.mark.parametrize("invalid_range", load_test_data("tracking_negative.json", "invalid_date_ranges"))
def test_trk_play_011_012_invalid_date_ranges(tracking, invalid_range):
    """TRK-PLAY-011, 012: Negative - From Date later than To Date is rejected or flagged invalid."""
    tracking.switch_to_playback_tracking()
    tracking.set_date_input(tracking.from_date_input, invalid_range["from_date"])
    tracking.set_date_input(tracking.to_date_input, invalid_range["to_date"])
    # Confirmed live: an inverted range marks the From Date field aria-invalid.
    assert (
        tracking.from_date_input.get_attribute("aria-invalid") == "true"
        or tracking.load_playback_btn.is_disabled()
    ), "An inverted date range must be flagged invalid or block Load Playback"


@pytest.mark.negative
@pytest.mark.parametrize("invalid_time", load_test_data("tracking_negative.json", "invalid_time_ranges"))
def test_trk_play_019_invalid_time_ranges(tracking, invalid_time):
    """TRK-PLAY-019: Negative - From Time later than To Time on the same date is rejected or flagged."""
    tracking.switch_to_playback_tracking()
    today_value = tracking.from_date_input.input_value()
    tracking.set_date_input(tracking.to_date_input, today_value)
    tracking.set_date_input(tracking.from_time_input, invalid_time["from_time"])
    tracking.set_date_input(tracking.to_time_input, invalid_time["to_time"])
    assert (
        tracking.from_time_input.get_attribute("aria-invalid") == "true"
        or tracking.load_playback_btn.is_disabled()
    ), "An inverted same-day time range must be flagged invalid or block Load Playback"


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_trk_play_052_intercept_playback_api_failure(tracking):
    """TRK-PLAY-052: Negative - Playback API fails; no false playback result is displayed."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.page.route("**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    tracking.page.route(
        "**/trackofy_api_new/**", lambda route: route.fulfill(status=500, body="Internal Server Error")
    )
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
    tracking.page.wait_for_timeout(2500)
    assert not tracking.contains_any_text(["Playback loaded successfully"]) or tracking.contains_any_text(
        ["error", "failed", "unable"]
    )
