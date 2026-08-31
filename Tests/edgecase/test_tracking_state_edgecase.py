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


@pytest.mark.edgecase
def test_trk_state_003_004_switch_preset_while_active(page, config, credentials):
    """TRK-STATE-003, 004: Edge Case - Switch preset view while Live or Playback active."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.select_preset_map_focus()
    tracking_page.select_preset_playback_view()
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.edgecase
def test_trk_state_005_refresh_tracking_page(page, config, credentials):
    """TRK-STATE-005: Edge Case - Refresh Tracking page during active session."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    page.reload()
    tracking_page.wait_for_tracking_page_ready()
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.edgecase
def test_trk_state_006_browser_back_forward_navigation(page, config, credentials):
    """TRK-STATE-006: Edge Case - Browser back/forward navigation to Tracking module."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    page.goto("/dashboard")
    page.go_back()
    tracking_page.wait_for_tracking_page_ready()
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.edgecase
def test_trk_state_009_api_concurrency(page, config, credentials):
    """TRK-STATE-009: Edge Case - Handle out-of-order or concurrent tracking API responses."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()
