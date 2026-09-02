import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_trk_live_007_select_max_vehicle_limit(tracking):
    """TRK-LIVE-007: Edge Case - Select the app-reported maximum supported number of vehicles."""
    available = tracking.available_vehicle_count()
    _, max_allowed = tracking.read_selected_vehicles_counter()
    if not max_allowed or available < max_allowed:
        pytest.skip("Not enough vehicles on this account to reach the selection limit")
    tracking.select_n_vehicles(max_allowed)
    selected, reported_max = tracking.read_selected_vehicles_counter()
    assert selected == max_allowed == reported_max


@pytest.mark.edgecase
def test_trk_live_010_prevent_duplicate_vehicle_selection(tracking):
    """TRK-LIVE-010: Edge Case - Attempt to select the same vehicle twice; duplicate is prevented."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    selected_after_first, _ = tracking.read_selected_vehicles_counter()

    tracking.open_vehicle_dropdown()
    same_option = tracking.vehicle_options.first
    same_option_text = same_option.inner_text().strip()
    same_option.click()
    tracking.wait_for_loading_to_finish()
    selected_after_repeat, _ = tracking.read_selected_vehicles_counter()

    # Clicking the already-selected option is expected to toggle it off (1 -> 0),
    # not add a duplicate -- either way the count must never exceed 1 here.
    assert selected_after_repeat <= selected_after_first
    assert selected_after_repeat != selected_after_first + 1, (
        f"Re-selecting the already-selected vehicle ({same_option_text!r}) must not add a duplicate"
    )


@pytest.mark.edgecase
def test_trk_live_011_no_available_vehicles(tracking):
    """TRK-LIVE-011: Edge Case - Vehicle list has no available vehicles -> clear empty state."""
    if tracking.available_vehicle_count() > 0:
        pytest.skip("This account has vehicles available; empty-state path cannot be exercised")
    tracking.open_vehicle_dropdown()
    assert tracking.contains_any_text(["No vehicles", "No results", "No data", "empty"])
    expect(tracking.start_tracking_btn).to_be_disabled()


@pytest.mark.edgecase
def test_trk_live_018_019_boundary_trail_thickness(tracking):
    """TRK-LIVE-018, 019: Edge Case - Move trail thickness slider to its min and max boundaries."""
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum <= minimum:
        pytest.skip("Thickness slider has no adjustable range on this account")

    tracking.set_thickness(minimum)
    assert tracking.read_thickness_value() == minimum

    tracking.set_thickness(maximum)
    assert tracking.read_thickness_value() == maximum


@pytest.mark.edgecase
def test_trk_live_032_rapid_start_tracking_clicks(tracking):
    """TRK-LIVE-032: Edge Case - Rapidly click Start Tracking; no duplicate tracking sessions/markers."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.select_vehicle_by_index(0)
    for _ in range(4):
        tracking.start_tracking_btn.click(no_wait_after=True)
    tracking.wait_for_loading_to_finish()
    tracking.page.wait_for_timeout(1000)
    assert tracking.vehicle_marker_on_map(vehicle_name).count() == 1


@pytest.mark.edgecase
@pytest.mark.allow_server_error
def test_trk_live_033_034_network_disconnect_reconnect(tracking):
    """TRK-LIVE-033, 034: Edge Case - Backend calls failing/recovering during live tracking is handled gracefully.

    Uses page.route() to abort backend calls rather than context.set_offline():
    a real network drop causes Chromium to swap the whole tab to its own
    "You're offline" interstitial page (confirmed live), which is a browser
    artifact and would test Chromium, not the app's own resilience.
    """
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()

    tracking.page.route("**/api/**", lambda route: route.abort())
    tracking.page.route("**/trackofy_api_new/**", lambda route: route.abort())
    tracking.page.wait_for_timeout(2000)
    expect(tracking.map_region).to_be_visible()  # UI must not crash while backend calls fail

    tracking.page.unroute("**/api/**")
    tracking.page.unroute("**/trackofy_api_new/**")
    tracking.page.wait_for_timeout(2000)
    expect(tracking.map_region).to_be_visible()
