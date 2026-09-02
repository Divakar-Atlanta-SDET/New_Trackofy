import pytest
from playwright.sync_api import expect

from Utils.data_loader import load_test_data


@pytest.mark.positive
@pytest.mark.parametrize("split_data", load_test_data("tracking_positive.json", "valid_split_screens"))
def test_trk_live_003_select_available_split_screen(tracking, split_data):
    """TRK-LIVE-003: Positive - Select an available Split Screen option; layout behavior applies."""
    tracking.select_split_screen(split_data["option"])
    expect(tracking.split_screen_select).to_contain_text(split_data["option"])


@pytest.mark.positive
def test_trk_live_005_select_single_vehicle(tracking):
    """TRK-LIVE-005: Positive - Select one vehicle; counter increments and Start Tracking enables."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    before_selected, _ = tracking.read_selected_vehicles_counter()
    vehicle_name = tracking.select_vehicle_by_index(0)
    assert vehicle_name
    after_selected, _ = tracking.read_selected_vehicles_counter()
    assert after_selected == before_selected + 1
    expect(tracking.start_tracking_btn).to_be_enabled()


@pytest.mark.positive
def test_trk_live_006_select_multiple_vehicles(tracking):
    """TRK-LIVE-006: Positive - Select multiple vehicles within the supported limit; all shown, counter matches."""
    available = tracking.available_vehicle_count()
    _, max_allowed = tracking.read_selected_vehicles_counter()
    target = min(available, max_allowed or available, 3)
    if target < 2:
        pytest.skip("Fewer than 2 vehicles available on this account to test multi-select")
    tracking.select_n_vehicles(target)
    selected, _ = tracking.read_selected_vehicles_counter()
    assert selected == target
    expect(tracking.start_tracking_btn).to_be_enabled()


@pytest.mark.positive
def test_trk_live_014_015_select_valid_trail_color_and_start(tracking):
    """TRK-LIVE-014, 015: Positive - Change trail color and start tracking; trail uses the new color."""
    baseline_color = tracking.read_trail_color()
    new_color = "#ff0000" if baseline_color.lower() != "#ff0000" else "#00ff00"
    tracking.set_trail_color(new_color)
    assert tracking.read_trail_color().lower() == new_color

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account for live tracking")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()
    assert tracking.read_trail_color().lower() == new_color


@pytest.mark.positive
def test_trk_live_023_start_tracking_single_vehicle(tracking):
    """TRK-LIVE-023: Positive - Select single vehicle and start live tracking; vehicle appears on map."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.start_live_tracking_flow()
    expect(tracking.vehicle_marker_on_map(vehicle_name)).to_be_visible()


@pytest.mark.positive
def test_trk_live_024_start_tracking_multiple_vehicles(tracking):
    """TRK-LIVE-024: Positive - Select multiple vehicles and start tracking; all tracked correctly."""
    available = tracking.available_vehicle_count()
    _, max_allowed = tracking.read_selected_vehicles_counter()
    target = min(available, max_allowed or available, 3)
    if target < 2:
        pytest.skip("Fewer than 2 vehicles available on this account to test multi-vehicle tracking")
    vehicle_names = tracking.select_n_vehicles(target)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()
    for name in vehicle_names:
        expect(tracking.vehicle_marker_on_map(name)).to_be_visible()


@pytest.mark.positive
def test_trk_live_025_start_tracking_custom_split_screen(tracking):
    """TRK-LIVE-025: Positive - Start tracking with a custom Split Screen configuration."""
    tracking.select_split_screen("Yes")
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.split_screen_select).to_contain_text("Yes")


@pytest.mark.positive
def test_trk_live_026_start_tracking_custom_trail_color_thickness(tracking):
    """TRK-LIVE-026: Positive - Start tracking with custom trail color and thickness."""
    baseline_thickness = tracking.read_thickness_value()
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum <= minimum:
        pytest.skip("Thickness slider has no adjustable range on this account")
    new_thickness = maximum if baseline_thickness != maximum else minimum
    tracking.set_thickness(new_thickness)

    baseline_color = tracking.read_trail_color()
    new_color = "#ff0000" if baseline_color.lower() != "#ff0000" else "#00ff00"
    tracking.set_trail_color(new_color)

    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    tracking.wait_for_loading_to_finish()
    assert tracking.read_thickness_value() == new_thickness
    assert tracking.read_trail_color().lower() == new_color
