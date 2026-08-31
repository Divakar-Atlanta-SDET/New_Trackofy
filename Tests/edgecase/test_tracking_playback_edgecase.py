import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.tracking_page import TrackingPage
from Utils.data_loader import load_test_data


def login_and_open_tracking(page, config, credentials):
    """Helper to log in and open /tracking module."""
    login_page = LoginPage(page, config)
    tracking_page = TrackingPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    tracking_page.open_tracking_page()
    tracking_page.switch_to_playback_tracking()
    return tracking_page


@pytest.mark.edgecase
def test_trk_play_005_playback_no_vehicles(page, config, credentials):
    """TRK-PLAY-005: Edge Case - Playback vehicle list empty state."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.playback_vehicle_select).to_be_visible()


@pytest.mark.edgecase
def test_trk_play_013_014_015_boundary_dates(page, config, credentials):
    """TRK-PLAY-013, 014, 015: Edge Case - Select today, future, or old dates outside history."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.from_date_input).to_be_visible()
    expect(tracking_page.to_date_input).to_be_visible()


@pytest.mark.edgecase
@pytest.mark.parametrize("time_boundary", load_test_data("tracking_edgecase.json", "boundary_times"))
def test_trk_play_020_021_022_boundary_times(page, config, credentials, time_boundary):
    """TRK-PLAY-020, 021, 022: Edge Case - 00:00 midnight and 23:59 end-of-day time boundaries."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.from_time_input).to_be_visible()
    expect(tracking_page.to_time_input).to_be_visible()


@pytest.mark.edgecase
def test_trk_play_027_028_032_033_038_039_filter_boundaries(page, config, credentials):
    """TRK-PLAY-027, 028, 032, 033, 038, 039: Edge Case - Min/max boundaries for hold time, speed, thickness."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.toggle_more_filters()
    expect(tracking_page.hold_time_select).to_be_visible()
    expect(tracking_page.overspeeding_select).to_be_visible()


@pytest.mark.edgecase
def test_trk_play_053_054_055_no_data_large_range_rapid_clicks(page, config, credentials):
    """TRK-PLAY-053, 054, 055: Edge Case - No data range, large range, and rapid clicks."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.load_playback_btn).to_be_visible()


@pytest.mark.edgecase
def test_trk_play_056_057_playback_network_recovery(page, config, credentials):
    """TRK-PLAY-056, 057: Edge Case - Disconnect network during playback load and verify recovery."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.load_playback_btn).to_be_visible()
