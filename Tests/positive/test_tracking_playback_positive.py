import datetime
import pytest
from playwright.sync_api import expect

from Utils.data_loader import load_test_data


def _fmt_input(d: datetime.date) -> str:
    """Confirmed live: whatever a user types/fills into From/To Date is parsed
    as MM/DD/YYYY, even though the field DISPLAYS dates as DD/MM/YYYY (a real,
    reported product inconsistency -- see Bug_Report.md). Use this to type/fill."""
    return d.strftime("%m/%d/%Y")


def _fmt_display(d: datetime.date) -> str:
    """What the field re-displays as after a value is entered -- use this to assert."""
    return d.strftime("%d/%m/%Y")


@pytest.mark.positive
def test_trk_play_003_select_valid_vehicle(tracking):
    """TRK-PLAY-003: Positive - Select a valid vehicle for playback."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.select_vehicle_by_index(0)
    assert vehicle_name
    expect(tracking.load_playback_btn).to_be_enabled()


@pytest.mark.positive
def test_trk_play_008_same_day_range(tracking):
    """TRK-PLAY-008, 009: Positive - Select a valid same-day date range."""
    tracking.switch_to_playback_tracking()
    today = datetime.date.today()
    tracking.set_date_input(tracking.from_date_input, _fmt_input(today))
    tracking.set_date_input(tracking.to_date_input, _fmt_input(today))
    expect(tracking.from_date_input).to_have_value(_fmt_display(today))
    expect(tracking.to_date_input).to_have_value(_fmt_display(today))
    assert tracking.from_date_input.get_attribute("aria-invalid") != "true"


@pytest.mark.positive
def test_trk_play_010_multi_day_range(tracking):
    """TRK-PLAY-010: Positive - Select a valid multi-day date range."""
    tracking.switch_to_playback_tracking()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    today = datetime.date.today()
    tracking.set_date_input(tracking.from_date_input, _fmt_input(yesterday))
    tracking.set_date_input(tracking.to_date_input, _fmt_input(today))
    expect(tracking.from_date_input).to_have_value(_fmt_display(yesterday))
    expect(tracking.to_date_input).to_have_value(_fmt_display(today))
    assert tracking.from_date_input.get_attribute("aria-invalid") != "true"


@pytest.mark.positive
def test_trk_play_018_valid_time_range(tracking):
    """TRK-PLAY-018: Positive - Select a valid same-day time range."""
    tracking.switch_to_playback_tracking()
    tracking.set_date_input(tracking.from_time_input, "00:00")
    tracking.set_date_input(tracking.to_time_input, "12:00")
    expect(tracking.from_time_input).to_have_value("00:00")
    expect(tracking.to_time_input).to_have_value("12:00")


@pytest.mark.positive
def test_trk_play_023_cross_day_valid_times(tracking):
    """TRK-PLAY-023: Positive - Use different dates with valid times; cross-day range accepted."""
    tracking.switch_to_playback_tracking()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    today = datetime.date.today()
    tracking.set_date_input(tracking.from_date_input, _fmt_input(yesterday))
    tracking.set_date_input(tracking.to_date_input, _fmt_input(today))
    tracking.set_date_input(tracking.from_time_input, "20:00")
    tracking.set_date_input(tracking.to_time_input, "06:00")
    assert tracking.from_date_input.get_attribute("aria-invalid") != "true"


@pytest.mark.positive
@pytest.mark.parametrize("hold_data", load_test_data("tracking_positive.json", "valid_hold_times"))
def test_trk_play_025_026_select_hold_time(tracking, hold_data):
    """TRK-PLAY-025, 026: Positive - Select a Hold Time filter option."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.select_hold_time(hold_data["option"])
    expect(tracking.hold_time_select).to_contain_text(hold_data["option"])


@pytest.mark.positive
@pytest.mark.parametrize("speed_data", load_test_data("tracking_positive.json", "valid_overspeed_thresholds"))
def test_trk_play_030_031_select_overspeeding_threshold(tracking, speed_data):
    """TRK-PLAY-030, 031: Positive - Select an Overspeeding threshold option."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.select_overspeeding(speed_data["option"])
    expect(tracking.overspeeding_select).to_contain_text(speed_data["option"])


@pytest.mark.positive
def test_trk_play_035_load_playback_custom_color(tracking):
    """TRK-PLAY-035: Positive - Load playback after changing trail color."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    baseline_color = tracking.read_trail_color()
    new_color = "#ff0000" if baseline_color.lower() != "#ff0000" else "#00ff00"
    tracking.set_trail_color(new_color)

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    assert tracking.read_trail_color().lower() == new_color


@pytest.mark.positive
def test_trk_play_042_043_apply_more_filters(tracking):
    """TRK-PLAY-042, 043: Positive - Apply a single filter, then combine multiple filters."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.select_hold_time("> 15 Minutes")
    expect(tracking.hold_time_select).to_contain_text("> 15 Minutes")

    tracking.select_overspeeding("> 80 KM/H")
    expect(tracking.overspeeding_select).to_contain_text("> 80 KM/H")
    # applying the second filter must not have reset the first
    expect(tracking.hold_time_select).to_contain_text("> 15 Minutes")


@pytest.mark.positive
def test_trk_play_047_load_playback_same_day(tracking):
    """TRK-PLAY-047: Positive - Load valid same-day playback for the selected vehicle/time range."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.load_playback_flow()
    assert vehicle_name
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()


@pytest.mark.positive
def test_trk_play_048_load_playback_multi_day(tracking):
    """TRK-PLAY-048: Positive - Load valid multi-day playback."""
    tracking.switch_to_playback_tracking()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    today = datetime.date.today()
    tracking.set_date_input(tracking.from_date_input, _fmt_input(yesterday))
    tracking.set_date_input(tracking.to_date_input, _fmt_input(today))

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()


@pytest.mark.positive
def test_trk_play_049_load_playback_with_filters(tracking):
    """TRK-PLAY-049: Positive - Load playback with Hold Time and Overspeeding filters applied."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.select_hold_time("> 15 Minutes")
    tracking.select_overspeeding("> 80 KM/H")

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()


@pytest.mark.positive
def test_trk_play_050_load_playback_with_styled_route(tracking):
    """TRK-PLAY-050: Positive - Load playback with custom color and thickness."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum > minimum:
        tracking.set_thickness(maximum)

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
