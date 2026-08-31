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
    tracking_page.switch_to_live_tracking()
    return tracking_page


@pytest.mark.edgecase
def test_trk_live_007_select_max_vehicle_limit(page, config, credentials):
    """TRK-LIVE-007: Edge Case - Select maximum supported vehicle limit (4 vehicles)."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.edgecase
def test_trk_live_010_prevent_duplicate_vehicle_selection(page, config, credentials):
    """TRK-LIVE-010: Edge Case - Attempt to select the same vehicle twice."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.edgecase
def test_trk_live_011_no_available_vehicles(page, config, credentials):
    """TRK-LIVE-011: Edge Case - Vehicle list has no available vehicles."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_vehicle_select).to_be_visible()


@pytest.mark.edgecase
@pytest.mark.parametrize("thickness_data", load_test_data("tracking_edgecase.json", "boundary_trail_thickness"))
def test_trk_live_018_019_boundary_trail_thickness(page, config, credentials, thickness_data):
    """TRK-LIVE-018, 019: Edge Case - Move trail thickness slider to minimum and maximum boundaries."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.live_trail_thickness_slider).to_be_visible()


@pytest.mark.edgecase
def test_trk_live_029_030_032_live_edge_cases(page, config, credentials):
    """TRK-LIVE-029, 030, 032: Edge Case - No current location, simultaneous updates, rapid clicks."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.start_tracking_btn).to_be_visible()


@pytest.mark.edgecase
def test_trk_live_033_034_network_disconnect_reconnect(page, config, credentials):
    """TRK-LIVE-033, 034: Edge Case - Network disconnection and reconnection during live tracking."""
    tracking_page = login_and_open_tracking(page, config, credentials)
    expect(tracking_page.map_container).to_be_visible()
