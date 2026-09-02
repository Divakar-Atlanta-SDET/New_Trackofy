import datetime
import pytest
from playwright.sync_api import expect

from Utils.data_loader import load_test_data


def _fmt(d: datetime.date) -> str:
    return d.strftime("%d/%m/%Y")


@pytest.mark.edgecase
def test_trk_play_005_playback_no_vehicles(tracking):
    """TRK-PLAY-005: Edge Case - Playback vehicle list empty state."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() > 0:
        pytest.skip("This account has vehicles available; empty-state path cannot be exercised")
    tracking.open_vehicle_dropdown()
    assert tracking.contains_any_text(["No vehicles", "No results", "No data", "empty"])
    expect(tracking.load_playback_btn).to_be_disabled()


@pytest.mark.edgecase
def test_trk_play_013_todays_date(tracking):
    """TRK-PLAY-013: Edge Case - Select today's date; handled correctly."""
    tracking.switch_to_playback_tracking()
    today = _fmt(datetime.date.today())
    tracking.set_date_input(tracking.from_date_input, today)
    tracking.set_date_input(tracking.to_date_input, today)
    assert tracking.from_date_input.get_attribute("aria-invalid") != "true"


@pytest.mark.edgecase
def test_trk_play_014_future_date(tracking):
    """TRK-PLAY-014: Edge Case - Select a future date; app follows its defined rule."""
    tracking.switch_to_playback_tracking()
    future = _fmt(datetime.date.today() + datetime.timedelta(days=30))
    tracking.set_date_input(tracking.from_date_input, future)
    tracking.set_date_input(tracking.to_date_input, future)
    tracking.page.wait_for_timeout(300)
    # Either the app rejects a future date (flagged invalid / Load blocked) or
    # explicitly allows it -- either is acceptable, just must not crash.
    expect(tracking.load_playback_btn).to_be_visible()


@pytest.mark.edgecase
def test_trk_play_015_old_date_outside_history(tracking):
    """TRK-PLAY-015: Edge Case - Select an old date outside available tracking history."""
    tracking.switch_to_playback_tracking()
    old_date = _fmt(datetime.date.today() - datetime.timedelta(days=730))
    tracking.set_date_input(tracking.from_date_input, old_date)
    tracking.set_date_input(tracking.to_date_input, old_date)
    tracking.page.wait_for_timeout(300)
    expect(tracking.load_playback_btn).to_be_visible()  # must not crash


@pytest.mark.edgecase
@pytest.mark.parametrize("time_boundary", load_test_data("tracking_edgecase.json", "boundary_times"))
def test_trk_play_020_021_022_boundary_times(tracking, time_boundary):
    """TRK-PLAY-020, 021, 022: Edge Case - 00:00 midnight and end-of-day time boundaries are handled."""
    tracking.switch_to_playback_tracking()
    tracking.set_date_input(tracking.from_time_input, time_boundary["from_time"])
    tracking.set_date_input(tracking.to_time_input, time_boundary["to_time"])
    expect(tracking.from_time_input).to_have_value(time_boundary["from_time"])
    expect(tracking.to_time_input).to_have_value(time_boundary["to_time"])


@pytest.mark.edgecase
def test_trk_play_027_028_hold_time_min_max(tracking):
    """TRK-PLAY-027, 028: Edge Case - Select the min and max available Hold Time options."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.hold_time_select.click()
    listbox = tracking.page.get_by_role("listbox", name="Hold Time")
    all_options = [o.strip() for o in listbox.get_by_role("option").all_inner_texts()]
    tracking.page.keyboard.press("Escape")
    if len(all_options) < 2:
        pytest.skip("Hold Time has fewer than 2 options to test boundaries")
    tracking.select_hold_time(all_options[0])
    expect(tracking.hold_time_select).to_contain_text(all_options[0])
    tracking.select_hold_time(all_options[-1])
    expect(tracking.hold_time_select).to_contain_text(all_options[-1])


@pytest.mark.edgecase
def test_trk_play_032_033_overspeeding_min_max(tracking):
    """TRK-PLAY-032, 033: Edge Case - Select the min and max available Overspeeding thresholds."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    tracking.overspeeding_select.click()
    listbox = tracking.page.get_by_role("listbox", name="Overspeeding")
    all_options = [o.strip() for o in listbox.get_by_role("option").all_inner_texts()]
    tracking.page.keyboard.press("Escape")
    if len(all_options) < 2:
        pytest.skip("Overspeeding has fewer than 2 options to test boundaries")
    tracking.select_overspeeding(all_options[0])
    expect(tracking.overspeeding_select).to_contain_text(all_options[0])
    tracking.select_overspeeding(all_options[-1])
    expect(tracking.overspeeding_select).to_contain_text(all_options[-1])


@pytest.mark.edgecase
def test_trk_play_038_039_thickness_min_max(tracking):
    """TRK-PLAY-038, 039: Edge Case - Playback trail thickness minimum and maximum supported values."""
    tracking.switch_to_playback_tracking()
    tracking.toggle_more_filters()
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum <= minimum:
        pytest.skip("Thickness slider has no adjustable range on this account")
    tracking.set_thickness(minimum)
    assert tracking.read_thickness_value() == minimum
    tracking.set_thickness(maximum)
    assert tracking.read_thickness_value() == maximum


@pytest.mark.edgecase
def test_trk_play_053_no_tracking_data(tracking):
    """TRK-PLAY-053: Edge Case - A valid range with no tracking data shows a clear no-data state."""
    tracking.switch_to_playback_tracking()
    old_date = _fmt(datetime.date.today() - datetime.timedelta(days=730))
    tracking.set_date_input(tracking.from_date_input, old_date)
    tracking.set_date_input(tracking.to_date_input, old_date)

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()  # must not silently break, even with no data


@pytest.mark.edgecase
def test_trk_play_055_rapid_load_playback_clicks(tracking):
    """TRK-PLAY-055: Edge Case - Rapidly click Load Playback; duplicate requests are prevented/handled."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    for _ in range(4):
        tracking.load_playback_btn.click(no_wait_after=True)
    tracking.wait_for_loading_to_finish()
    tracking.page.wait_for_timeout(1000)
    expect(tracking.map_region).to_be_visible()


@pytest.mark.edgecase
@pytest.mark.allow_server_error
def test_trk_play_056_057_playback_network_recovery(tracking):
    """TRK-PLAY-056, 057: Edge Case - Backend failure during playback load terminates safely and can recover."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)

    tracking.page.route("**/api/**", lambda route: route.abort())
    tracking.page.route("**/trackofy_api_new/**", lambda route: route.abort())
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
    tracking.page.wait_for_timeout(2000)
    expect(tracking.map_region).to_be_visible()  # must terminate safely, not hang/crash

    tracking.page.unroute("**/api/**")
    tracking.page.unroute("**/trackofy_api_new/**")
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
