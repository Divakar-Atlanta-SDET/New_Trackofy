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
def test_trk_nav_001_open_tracking_module(page, config, credentials):
    """TRK-NAV-001: Functional - Open Tracking module and verify map & bottom panel load."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()
    expect(tracking_page.live_tracking_tab).to_be_visible()


@pytest.mark.functional
def test_trk_nav_002_003_004_switch_view_presets(page, config, credentials):
    """TRK-NAV-002, 003, 004: Functional - Select Map Focus and Playback View presets."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.select_preset_map_focus()
    tracking_page.select_preset_playback_view()
    expect(tracking_page.live_tracking_tab).to_be_visible()


@pytest.mark.functional
def test_trk_nav_005_006_007_008_switch_main_tabs(page, config, credentials):
    """TRK-NAV-005 to 008: Functional - Switch between Live Tracking and Playback Tracking tabs."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    tracking_page.switch_to_playback_tracking()
    expect(tracking_page.playback_vehicle_select).to_be_visible()

    tracking_page.switch_to_live_tracking()
    expect(tracking_page.live_vehicle_select).to_be_visible()
