import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_trk_nav_010_viewport_resize(tracking):
    """TRK-NAV-010: Edge Case - Change browser viewport after opening Tracking; controls stay usable."""
    tracking.page.set_viewport_size({"width": 1024, "height": 768})
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_visible()
    expect(tracking.start_tracking_btn).to_be_visible()

    tracking.page.set_viewport_size({"width": 390, "height": 844})
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_visible()
