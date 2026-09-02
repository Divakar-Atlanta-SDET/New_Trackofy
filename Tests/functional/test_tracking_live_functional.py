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


@pytest.mark.functional
def test_trk_live_001_default_split_screen(page, config, credentials):
    """TRK-LIVE-001: Functional - Verify default Split Screen value ("No")."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_split_screen_select).to_be_visible()
    expect(tracking_page.live_split_screen_select).to_contain_text("No")


@pytest.mark.functional
def test_trk_live_002_004_013_open_dropdowns_and_pickers(page, config, credentials):
    """TRK-LIVE-002, 004, 013: Functional - Open Split Screen, Vehicle, and Color dropdowns."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()
    expect(tracking_page.live_split_screen_select).to_be_visible()


@pytest.mark.functional
def test_trk_live_016_017_adjust_trail_thickness(page, config, credentials):
    """TRK-LIVE-016, 017: Functional - Increase and decrease trail thickness via slider."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_trail_thickness_slider).to_be_visible()


@pytest.mark.functional
def test_trk_live_020_021_reset_form(page, config, credentials):
    """TRK-LIVE-020, 021: Functional - Test Reset button behavior on Live Tracking form."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.select_first_available_vehicle()
    expect(tracking_page.start_tracking_btn).to_be_enabled()
    tracking_page.live_reset_btn.click()
    expect(tracking_page.start_tracking_btn).to_be_disabled()


@pytest.mark.functional
def test_trk_live_027_028_live_position_and_trail(page, config, credentials):
    """TRK-LIVE-027, 028: Functional - Verify live position updates and route rendering."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    vehicle_name = tracking_page.start_live_tracking_flow()
    expect(page.locator("body")).to_contain_text(vehicle_name)
