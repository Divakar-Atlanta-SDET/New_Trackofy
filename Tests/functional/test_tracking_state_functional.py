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
    return tracking_page


@pytest.mark.functional
def test_trk_state_001_002_tab_state_isolation(page, config, credentials):
    """TRK-STATE-001, 002: Functional - Verify Live and Playback tab state isolation."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_playback_tracking()
    expect(tracking_page.playback_vehicle_select).to_be_visible()

    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_vehicle_select).to_be_visible()
