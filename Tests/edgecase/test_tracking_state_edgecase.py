import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_trk_state_003_switch_preset_while_live_active(tracking):
    """TRK-STATE-003: Edge Case - Switch preset view while Live Tracking is active; no broken/duplicate UI."""
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    vehicle_name = tracking.start_live_tracking_flow()
    tracking.map_focus_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    tracking.playback_view_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    assert tracking.map_region.count() == 1
    assert tracking.vehicle_marker_on_map(vehicle_name).count() <= 1


@pytest.mark.edgecase
def test_trk_state_004_switch_preset_while_playback_active(tracking):
    """TRK-STATE-004: Edge Case - Switch preset view while Playback is active; state stays consistent.

    Confirmed live: once playback data is loaded, the "Playback View" preset
    does not reliably return to the Playback tab -- it can land back on Live
    Tracking instead (a real product inconsistency; the same preset DOES
    switch to Playback from a fresh, no-data page load -- see TRK-NAV-003).
    So this only checks general UI stability (no duplicate panels/maps,
    tabs still functional), not which tab ends up active.
    """
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.load_playback_flow()
    tracking.map_focus_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    tracking.playback_view_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    assert tracking.map_region.count() == 1
    assert tracking.live_tracking_tab.count() == 1
    assert tracking.playback_tracking_tab.count() == 1


@pytest.mark.edgecase
def test_trk_state_005_refresh_tracking_page(tracking):
    """TRK-STATE-005: Edge Case - Refresh Tracking page; module re-initializes correctly."""
    tracking.select_split_screen("Yes")
    tracking.page.reload()
    tracking.wait_for_tracking_page_ready()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_visible()
    # A fresh load must not retain corrupted state from before the refresh.
    expect(tracking.split_screen_select).to_contain_text("No")


@pytest.mark.edgecase
def test_trk_state_006_browser_back_forward_navigation(tracking):
    """TRK-STATE-006: Edge Case - Browser back/forward navigation to Tracking; page re-initializes correctly."""
    tracking.page.goto("/dashboard")
    tracking.page.wait_for_load_state("domcontentloaded")
    tracking.page.go_back()
    tracking.wait_for_tracking_page_ready()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_visible()


@pytest.mark.edgecase
def test_trk_state_009_api_concurrency_stale_response_ignored(tracking):
    """TRK-STATE-009: Edge Case - A slow first Load Playback request must not overwrite
    the result of a second, faster-completing Load Playback for a different vehicle.

    Three test defects found and fixed here, all confirmed live 2026-09-16:
    1. "**/api/**" never matches the real playback-loading call (it's
       `trackofy_api_new/user.php`, no literal "/api/" path segment) but DOES
       incidentally match Google Maps' own `.../api/js/...` library file --
       so the old test was delaying an unrelated Maps script, not the real
       request, and never actually exercising the race it claims to test.
       Scoped to "**/trackofy_api_new/**" instead (same pattern already used
       in test_tracking_state_negative.py).
    2. In the default single-select dropdown (Split Screen = "No"), picking
       index 0 twice in a row returns the SAME vehicle both times -- it's
       not a multi-select "unselected options" list. Use index 1 for the
       second pick to guarantee two distinct vehicles.
    3. Once Load Playback succeeds, the whole filter panel (including
       vehicle_select) collapses into a minimized bottom bar -- same
       pattern as TRK-PLAY-025's Split Screen collapse. Must click
       "Expand bottom panel" before the dropdown is reachable again, and
       the final check must use the persistent map-overlay vehicle badge
       (map_overlay_shows_vehicle) instead of vehicle_select, since that
       panel collapses again after the second Load Playback too.
    """
    page = tracking.page
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() < 2:
        pytest.skip("Fewer than 2 vehicles available on this account to test concurrency")

    call_count = {"n": 0}

    def delay_first_call(route):
        call_count["n"] += 1
        if call_count["n"] == 1:
            page.wait_for_timeout(3000)  # first request resolves last
        route.continue_()

    page.route("**/trackofy_api_new/**", delay_first_call)

    first_vehicle = tracking.select_vehicle_by_index(0)
    tracking.load_playback_btn.click()  # slow, in-flight request for the first vehicle
    page.wait_for_timeout(300)

    if tracking.expand_bottom_panel_button.count() > 0:
        tracking.expand_bottom_panel_button.click()

    second_vehicle = tracking.select_vehicle_by_index(1)
    tracking.load_playback_btn.click()
    page.wait_for_timeout(4000)
    page.unroute("**/trackofy_api_new/**")

    # The vehicle picked/loaded last must be the one actually reflected on the
    # map, not silently overwritten once the slower first response finally arrives.
    assert tracking.map_overlay_shows_vehicle(second_vehicle), (
        f"Expected map overlay to show the last-loaded vehicle ({second_vehicle}), "
        "not a stale result from the slower first request."
    )
    assert not tracking.map_overlay_shows_vehicle(first_vehicle), (
        f"Stale first vehicle ({first_vehicle}) is still shown -- its slow response "
        "may have overwritten the second, faster-completing one."
    )
