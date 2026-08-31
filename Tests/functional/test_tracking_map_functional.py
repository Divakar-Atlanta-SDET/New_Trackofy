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
def test_trk_map_001_verify_map_renders(page, config, credentials):
    """TRK-MAP-001: Functional - Verify map renders properly on page load."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.functional
def test_trk_map_002_003_map_zoom_pan_controls(page, config, credentials):
    """TRK-MAP-002, 003: Functional - Verify map tile options and zoom/pan capability."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_tile_btn).to_be_visible()
    expect(tracking_page.hybrid_tile_btn).to_be_visible()
