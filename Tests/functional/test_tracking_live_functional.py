import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_trk_live_001_default_split_screen(tracking):
    """TRK-LIVE-001: Functional - Verify default Split Screen value."""
    expect(tracking.split_screen_select).to_be_visible()
    expect(tracking.split_screen_select).to_contain_text("No")


@pytest.mark.functional
def test_trk_live_002_004_013_open_dropdowns_and_pickers(tracking):
    """TRK-LIVE-002, 004, 013: Functional - Open Split Screen, Vehicle, and Color pickers."""
    tracking.split_screen_select.click()
    expect(tracking.page.get_by_role("option", name="Yes", exact=True)).to_be_visible()
    tracking.page.keyboard.press("Escape")

    tracking.open_vehicle_dropdown()
    expect(tracking.vehicle_options.first).to_be_visible()
    tracking.page.keyboard.press("Escape")

    # native <input type="color"> reports Playwright-hidden despite being a
    # real, interactive control (confirmed live) -- check attachment, not CSS visibility
    expect(tracking.trail_color_input).to_be_attached()


@pytest.mark.functional
def test_trk_live_016_017_adjust_trail_thickness(tracking):
    """TRK-LIVE-016, 017: Functional - Increase and decrease trail thickness via slider."""
    baseline = tracking.read_thickness_value()
    minimum, maximum = tracking.read_thickness_bounds()
    if maximum <= minimum:
        pytest.skip("Thickness slider has no adjustable range on this account")

    higher = min(baseline + 1, maximum)
    tracking.set_thickness(higher)
    assert tracking.read_thickness_value() == higher

    lower = max(higher - 1, minimum)
    tracking.set_thickness(lower)
    assert tracking.read_thickness_value() == lower


@pytest.mark.functional
def test_trk_live_020_021_reset_form(tracking):
    """TRK-LIVE-020, 021: Functional - Reset restores the pre-change baseline."""
    baseline_selected, baseline_max = tracking.read_selected_vehicles_counter()
    baseline_color = tracking.read_trail_color()

    tracking.select_vehicle_by_index(0)
    expect(tracking.start_tracking_btn).to_be_enabled()
    selected_after_pick, _ = tracking.read_selected_vehicles_counter()
    assert selected_after_pick == baseline_selected + 1

    tracking.reset_btn.click()
    tracking.wait_for_loading_to_finish()

    expect(tracking.start_tracking_btn).to_be_disabled()
    selected_after_reset, _ = tracking.read_selected_vehicles_counter()
    assert selected_after_reset == baseline_selected == 0
    assert tracking.read_trail_color() == baseline_color


@pytest.mark.functional
def test_trk_live_020b_reset_without_changes_stays_default(tracking):
    """TRK-LIVE-020: Functional - Reset with nothing changed leaves the form in its default state."""
    before_selected, before_max = tracking.read_selected_vehicles_counter()
    before_color = tracking.read_trail_color()
    tracking.reset_btn.click()
    tracking.wait_for_loading_to_finish()
    after_selected, after_max = tracking.read_selected_vehicles_counter()
    assert (after_selected, after_max) == (before_selected, before_max)
    assert tracking.read_trail_color() == before_color


@pytest.mark.functional
def test_trk_live_027_028_live_position_and_trail(tracking):
    """TRK-LIVE-027, 028: Functional - Verify live position updates and route rendering."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account for live tracking")
    vehicle_name = tracking.start_live_tracking_flow()
    expect(tracking.vehicle_marker_on_map(vehicle_name)).to_be_visible()
