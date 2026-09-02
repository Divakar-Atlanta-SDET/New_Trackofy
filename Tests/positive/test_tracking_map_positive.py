import pytest
from playwright.sync_api import expect


@pytest.mark.positive
def test_trk_map_004_live_vehicle_marker(tracking):
    """TRK-MAP-004: Positive - Selected live vehicle's marker is shown at its latest position."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.start_live_tracking_flow()
    expect(tracking.vehicle_marker_on_map(vehicle_name)).to_be_visible()


@pytest.mark.positive
def test_trk_map_005_006_live_route_color_and_thickness(tracking):
    """TRK-MAP-005, 006: Positive - Live route reflects the configured trail color/thickness.

    There is no accessible DOM hook for the rendered Google Maps polyline
    itself (documented limitation) -- the closest real, verifiable signal is
    that the color/thickness controls retain the chosen values once tracking
    is live, which is what the map layer is driven from.
    """
    baseline_color = tracking.read_trail_color()
    new_color = "#00ff00" if baseline_color.lower() != "#00ff00" else "#ff0000"
    tracking.set_trail_color(new_color)
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum > minimum:
        tracking.set_thickness(maximum)

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()

    assert tracking.read_trail_color().lower() == new_color
    if maximum > minimum:
        assert tracking.read_thickness_value() == maximum


@pytest.mark.positive
def test_trk_map_007_playback_route_displayed(tracking):
    """TRK-MAP-007: Positive - Playback's historical route renders for the selected vehicle/range."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.load_playback_flow()
    expect(tracking.map_region).to_be_visible()
