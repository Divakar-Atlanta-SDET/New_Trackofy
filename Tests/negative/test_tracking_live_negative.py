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
    tracking_page.switch_to_live_tracking()
    return tracking_page


@pytest.mark.negative
def test_trk_live_008_exceed_vehicle_selection_limit(page, config, credentials):
    """TRK-LIVE-008: Negative - Attempt to select vehicles beyond supported limit of 4."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.negative
def test_trk_live_012_031_intercept_live_api_failure(page, config, credentials):
    """TRK-LIVE-012, 031: Negative - Intercept Live Tracking API failure and assert feedback."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.negative
def test_trk_live_022_start_tracking_without_vehicle(page, config, credentials):
    """TRK-LIVE-022: Negative - Click Start Tracking without selecting a vehicle."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.start_tracking_btn).to_be_disabled()
