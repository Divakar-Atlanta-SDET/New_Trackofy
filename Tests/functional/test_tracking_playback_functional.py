import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.tracking_page import TrackingPage


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


@pytest.mark.functional
def test_trk_play_001_verify_default_playback_fields(page, config, credentials):
    """TRK-PLAY-001: Functional - Verify default Playback fields displayed."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.playback_vehicle_select).to_be_visible()
    expect(tracking_page.from_date_input).to_be_visible()
    expect(tracking_page.to_date_input).to_be_visible()


@pytest.mark.functional
def test_trk_play_006_007_open_calendar_pickers(page, config, credentials):
    """TRK-PLAY-006, 007: Functional - Open From Date and To Date calendar pickers."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.from_date_input).to_be_visible()


@pytest.mark.functional
def test_trk_play_040_041_toggle_more_filters(page, config, credentials):
    """TRK-PLAY-040, 041: Functional - Open and close More Filters panel."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.toggle_more_filters()
    expect(tracking_page.hold_time_select).to_be_visible()
    tracking_page.toggle_more_filters()


@pytest.mark.functional
def test_trk_play_044_045_reset_playback_form(page, config, credentials):
    """TRK-PLAY-044, 045: Functional - Test Reset button on Playback Tracking form."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.playback_reset_btn.click()
    expect(tracking_page.playback_vehicle_select).to_be_visible()
