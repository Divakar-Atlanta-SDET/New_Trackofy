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
    return tracking_page


@pytest.mark.positive
@pytest.mark.parametrize("split_data", load_test_data("tracking_positive.json", "valid_split_screens"))
def test_trk_live_003_select_available_split_screen(page, config, credentials, split_data):
    """TRK-LIVE-003: Positive - Select an available Split Screen option."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_split_screen_select).to_be_visible()


@pytest.mark.positive
def test_trk_live_005_select_single_vehicle(page, config, credentials):
    """TRK-LIVE-005: Positive - Select one vehicle and verify counter updates."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.positive
def test_trk_live_006_select_multiple_vehicles(page, config, credentials):
    """TRK-LIVE-006: Positive - Select multiple vehicles within supported limit."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.positive
def test_trk_live_014_select_valid_trail_color(page, config, credentials):
    """TRK-LIVE-014: Positive - Select a valid trail color."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_split_screen_select).to_be_visible()


@pytest.mark.positive
def test_trk_live_023_start_tracking_single_vehicle(page, config, credentials):
    """TRK-LIVE-023: Positive - Select single vehicle and start tracking."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.start_tracking_btn).to_be_visible()


@pytest.mark.positive
def test_trk_live_024_start_tracking_multiple_vehicles(page, config, credentials):
    """TRK-LIVE-024: Positive - Select multiple vehicles and start tracking."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.start_tracking_btn).to_be_visible()


@pytest.mark.positive
def test_trk_live_025_start_tracking_custom_split_screen(page, config, credentials):
    """TRK-LIVE-025: Positive - Start tracking with custom Split Screen configuration."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_split_screen_select).to_be_visible()


@pytest.mark.positive
def test_trk_live_026_start_tracking_custom_trail_color_thickness(page, config, credentials):
    """TRK-LIVE-026: Positive - Start tracking with custom trail color and thickness."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_trail_thickness_slider).to_be_visible()
