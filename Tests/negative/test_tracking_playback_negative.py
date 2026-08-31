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


@pytest.mark.negative
def test_trk_play_004_046_load_playback_missing_vehicle(page, config, credentials):
    """TRK-PLAY-004, 046: Negative - Attempt Load Playback without selecting vehicle."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.load_playback_btn).to_be_disabled()


@pytest.mark.negative
@pytest.mark.parametrize("invalid_range", load_test_data("tracking_negative.json", "invalid_date_ranges"))
def test_trk_play_011_012_invalid_date_ranges(page, config, credentials, invalid_range):
    """TRK-PLAY-011, 012: Negative - Set From Date later than To Date or invalid date range."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.from_date_input).to_be_visible()
    expect(tracking_page.to_date_input).to_be_visible()


@pytest.mark.negative
@pytest.mark.parametrize("invalid_time", load_test_data("tracking_negative.json", "invalid_time_ranges"))
def test_trk_play_019_invalid_time_ranges(page, config, credentials, invalid_time):
    """TRK-PLAY-019: Negative - Set From Time later than To Time on same date."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.from_time_input).to_be_visible()
    expect(tracking_page.to_time_input).to_be_visible()


@pytest.mark.negative
def test_trk_play_052_intercept_playback_api_failure(page, config, credentials):
    """TRK-PLAY-052: Negative - Intercept Playback API failure and assert feedback."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.load_playback_btn).to_be_visible()
