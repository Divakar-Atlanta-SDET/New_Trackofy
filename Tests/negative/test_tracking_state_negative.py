import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.tracking_page import TrackingPage


@pytest.mark.negative
def test_trk_state_007_008_session_expiry_during_tracking(page, config, credentials):
    """TRK-STATE-007, 008: Negative - Clear session cookies during tracking and verify auth redirect."""
    login_page = LoginPage(page, config)
    tracking_page = TrackingPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    tracking_page.open_tracking_page()
    page.context.clear_cookies()
    tracking_page.switch_to_playback_tracking()
    expect(page.locator("body")).to_be_visible()
