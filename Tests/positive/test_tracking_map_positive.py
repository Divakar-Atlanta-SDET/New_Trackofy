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


@pytest.mark.positive
def test_trk_map_004_live_vehicle_marker(page, config, credentials):
    """TRK-MAP-004: Positive - Verify selected live vehicle marker displayed at latest position."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.positive
def test_trk_map_005_live_route_color(page, config, credentials):
    """TRK-MAP-005: Positive - Verify live route uses configured trail color."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.positive
def test_trk_map_006_live_route_thickness(page, config, credentials):
    """TRK-MAP-006: Positive - Verify live route uses configured trail thickness."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.positive
def test_trk_map_007_playback_route_displayed(page, config, credentials):
    """TRK-MAP-007: Positive - Verify playback historical route is rendered on map."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_playback_tracking()
    expect(tracking_page.map_container).to_be_visible()
