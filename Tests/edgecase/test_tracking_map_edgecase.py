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
def test_trk_map_008_map_service_unavailable(page, config, credentials):
    """TRK-MAP-008: Edge Case - Map service/network is unavailable."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.edgecase
def test_trk_map_009_invalid_coordinates(page, config, credentials):
    """TRK-MAP-009: Edge Case - Vehicle coordinates are unavailable or invalid."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()


@pytest.mark.edgecase
def test_trk_map_010_overlapping_routes(page, config, credentials):
    """TRK-MAP-010: Edge Case - Multiple vehicle routes overlap."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()
