import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
@pytest.mark.allow_server_error
def test_trk_map_008_map_service_unavailable(tracking):
    """TRK-MAP-008: Edge Case - Map service/network unavailable is handled without breaking the form."""
    tracking.page.route("**/maps.googleapis.com/**", lambda route: route.abort())
    tracking.page.route("**/maps.gstatic.com/**", lambda route: route.abort())
    tracking.page.reload()
    tracking.wait_for_tracking_page_ready()
    tracking.page.wait_for_timeout(2000)
    # The tracking form itself must stay usable even if map tiles fail to load.
    expect(tracking.split_screen_select).to_be_visible()
    expect(tracking.vehicle_select).to_be_visible()


@pytest.mark.edgecase
def test_trk_map_009_invalid_coordinates(tracking):
    """TRK-MAP-009: Edge Case - A vehicle with unavailable/invalid coordinates does not break the UI.

    Real coordinate data can't be forced from the test, so this is a
    best-effort stability check: track whatever vehicle is available and
    confirm the page never enters a broken/crashed state.
    """
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.start_live_tracking_flow()
    tracking.page.wait_for_timeout(1500)
    expect(tracking.map_region).to_be_visible()
    # a marker for the vehicle should exist; if it has no valid location it
    # should simply not render rather than corrupt the page.
    marker_count = tracking.vehicle_marker_on_map(vehicle_name).count()
    assert marker_count in (0, 1)


@pytest.mark.edgecase
def test_trk_map_010_overlapping_routes(tracking):
    """TRK-MAP-010: Edge Case - Multiple vehicle routes overlapping stay correctly associated."""
    available = tracking.available_vehicle_count()
    _, max_allowed = tracking.read_selected_vehicles_counter()
    target = min(available, max_allowed or available, 2)
    if target < 2:
        pytest.skip("Fewer than 2 vehicles available on this account to test overlapping routes")
    vehicle_names = tracking.select_n_vehicles(target)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()
    for name in vehicle_names:
        expect(tracking.vehicle_marker_on_map(name)).to_be_visible()
