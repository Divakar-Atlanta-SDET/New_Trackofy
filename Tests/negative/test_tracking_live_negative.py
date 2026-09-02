import pytest
from playwright.sync_api import expect


@pytest.mark.negative
def test_trk_live_008_exceed_vehicle_selection_limit(tracking):
    """TRK-LIVE-008: Negative - Attempt to select a vehicle beyond the app-reported max limit."""
    available = tracking.available_vehicle_count()
    _, max_allowed = tracking.read_selected_vehicles_counter()
    if not max_allowed or available <= max_allowed:
        pytest.skip("Not enough vehicles on this account to exceed the selection limit")

    tracking.select_n_vehicles(max_allowed)
    selected_at_max, reported_max = tracking.read_selected_vehicles_counter()
    assert selected_at_max == max_allowed == reported_max

    tracking.attempt_select_one_more_vehicle(already_selected=max_allowed)
    selected_after_attempt, _ = tracking.read_selected_vehicles_counter()
    assert selected_after_attempt == max_allowed, "Selecting beyond the reported max must be rejected"


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_trk_live_012_vehicle_list_api_failure(authenticated_page):
    """TRK-LIVE-012: Negative - Vehicle list API fails; no false available-selection state."""
    from Pages.tracking_page import TrackingPage

    page = authenticated_page
    page.route("**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.route("**/trackofy_api_new/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    tracking_page = TrackingPage(page)
    tracking_page.page.goto("/tracking")
    page.wait_for_timeout(2500)
    # With the vehicle-data API down, Start Tracking must not be falsely usable.
    expect(tracking_page.start_tracking_btn).to_be_disabled()


@pytest.mark.negative
def test_trk_live_022_start_tracking_without_vehicle(tracking):
    """TRK-LIVE-022: Negative - Click Start Tracking without selecting a vehicle."""
    expect(tracking.start_tracking_btn).to_be_disabled()
