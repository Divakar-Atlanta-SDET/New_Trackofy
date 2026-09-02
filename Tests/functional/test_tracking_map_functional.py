import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_trk_map_001_verify_map_renders(tracking):
    """TRK-MAP-001: Functional - Verify map renders on Tracking page load."""
    expect(tracking.map_region).to_be_visible()
    expect(tracking.map_tile_btn).to_be_visible()


@pytest.mark.functional
def test_trk_map_002_zoom_in_out(tracking):
    """TRK-MAP-002: Functional - Zoom in/out on the map."""
    box = tracking.map_region.bounding_box()
    center_x, center_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    tracking.page.mouse.move(center_x, center_y)
    tracking.page.mouse.wheel(0, -300)  # zoom in
    tracking.page.wait_for_timeout(800)
    tracking.page.mouse.wheel(0, 300)  # zoom out
    tracking.page.wait_for_timeout(800)
    expect(tracking.map_region).to_be_visible()  # map stays intact through zoom


@pytest.mark.functional
def test_trk_map_003_pan_map_preserves_form_state(tracking):
    """TRK-MAP-003: Functional - Pan the map without corrupting the tracking form state."""
    tracking.select_split_screen("Yes")
    box = tracking.map_region.bounding_box()
    start_x, start_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    tracking.page.mouse.move(start_x, start_y)
    tracking.page.mouse.down()
    tracking.page.mouse.move(start_x - 150, start_y - 100, steps=10)
    tracking.page.mouse.up()
    tracking.page.wait_for_timeout(500)
    expect(tracking.split_screen_select).to_contain_text("Yes")
    expect(tracking.map_region).to_be_visible()


@pytest.mark.functional
def test_trk_map_map_hybrid_tile_toggle(tracking):
    """TRK-MAP: Functional - Toggle between Map and Hybrid tile layers."""
    tracking.hybrid_tile_btn.click()
    tracking.page.wait_for_timeout(500)
    expect(tracking.map_region).to_be_visible()
    tracking.map_tile_btn.click()
    tracking.page.wait_for_timeout(500)
    expect(tracking.map_region).to_be_visible()
