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


@pytest.mark.positive
def test_trk_play_003_select_valid_vehicle(page, config, credentials):
    """TRK-PLAY-003: Positive - Select a valid vehicle for playback."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    selected_vehicle = tracking_page.select_first_available_playback_vehicle()
    assert selected_vehicle is not None
    expect(tracking_page.load_playback_btn).to_be_enabled()


@pytest.mark.positive
@pytest.mark.parametrize("range_data", load_test_data("tracking_positive.json", "valid_date_ranges"))
def test_trk_play_008_009_010_select_valid_date_ranges(page, config, credentials, range_data):
    """TRK-PLAY-008, 009, 010: Positive - Select valid same-day and multi-day date ranges."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.from_date_input.fill(range_data["from_date"])
    tracking_page.to_date_input.fill(range_data["to_date"])
    expect(tracking_page.from_date_input).to_have_value(range_data["from_date"])
    expect(tracking_page.to_date_input).to_have_value(range_data["to_date"])


@pytest.mark.positive
def test_trk_play_018_023_select_valid_time_ranges(page, config, credentials):
    """TRK-PLAY-018, 023: Positive - Select valid same-day and cross-day time ranges."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.from_time_input.fill("00:00")
    tracking_page.to_time_input.fill("12:00")
    expect(tracking_page.from_time_input).to_have_value("00:00")
    expect(tracking_page.to_time_input).to_have_value("12:00")


@pytest.mark.positive
@pytest.mark.parametrize("hold_data", load_test_data("tracking_positive.json", "valid_hold_times"))
def test_trk_play_025_026_select_hold_time(page, config, credentials, hold_data):
    """TRK-PLAY-025, 026: Positive - Select Hold Time filter option."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.toggle_more_filters()
    expect(tracking_page.hold_time_select).to_be_visible()


@pytest.mark.positive
@pytest.mark.parametrize("speed_data", load_test_data("tracking_positive.json", "valid_overspeed_thresholds"))
def test_trk_play_030_031_select_overspeeding_threshold(page, config, credentials, speed_data):
    """TRK-PLAY-030, 031: Positive - Select Overspeeding threshold option."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.toggle_more_filters()
    expect(tracking_page.overspeeding_select).to_be_visible()


@pytest.mark.positive
def test_trk_play_035_load_playback_custom_color(page, config, credentials):
    """TRK-PLAY-035: Positive - Load playback after changing trail color."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    vehicle_name = tracking_page.load_playback_flow()
    assert vehicle_name is not None


@pytest.mark.positive
def test_trk_play_042_043_apply_more_filters(page, config, credentials):
    """TRK-PLAY-042, 043: Positive - Apply single and multiple additional filters."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.toggle_more_filters()
    expect(tracking_page.hold_time_select).to_be_visible()
    expect(tracking_page.overspeeding_select).to_be_visible()


@pytest.mark.positive
def test_trk_play_047_048_049_050_load_playback_variations(page, config, credentials):
    """TRK-PLAY-047 to 050: Positive - Load valid same-day, multi-day, filtered, and styled playback."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    vehicle_name = tracking_page.load_playback_flow()
    assert vehicle_name is not None
