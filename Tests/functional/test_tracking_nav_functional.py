import re
import pytest
from playwright.sync_api import expect

from Pages.tracking_page import TrackingPage


@pytest.mark.functional
def test_trk_nav_001_open_tracking_module(tracking):
    """TRK-NAV-001: Functional - Open Tracking module and verify map & bottom panel load."""
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_visible()
    expect(tracking.playback_tracking_tab).to_be_visible()


@pytest.mark.functional
def test_trk_nav_002_map_focus_hides_bottom_panel(tracking):
    """TRK-NAV-002: Functional - Map Focus preset hides the bottom tracking panel, map stays visible."""
    tracking.map_focus_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.live_tracking_tab).to_be_hidden()
    expect(tracking.playback_tracking_tab).to_be_hidden()


@pytest.mark.functional
def test_trk_nav_003_playback_view_shows_bottom_panel(tracking):
    """TRK-NAV-003: Functional - Playback View preset shows map + bottom panel (Playback tab active)."""
    tracking.map_focus_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    tracking.playback_view_preset_btn.click()
    tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.playback_tracking_tab).to_be_visible()


@pytest.mark.functional
def test_trk_nav_004_repeated_preset_switching_stays_stable(tracking):
    """TRK-NAV-004: Functional - Switch repeatedly between presets without broken/duplicate UI."""
    for _ in range(4):
        tracking.map_focus_preset_btn.click()
        tracking.wait_for_loading_to_finish()
        tracking.playback_view_preset_btn.click()
        tracking.wait_for_loading_to_finish()
    expect(tracking.map_region).to_be_visible()
    expect(tracking.playback_tracking_tab).to_be_visible()
    # no duplicate panels/tabs after repeated toggling
    assert tracking.page.get_by_role("button", name="Playback Tracking", exact=True).count() == 1
    assert tracking.map_region.count() == 1


@pytest.mark.functional
def test_trk_nav_005_open_live_tracking_tab(tracking):
    """TRK-NAV-005: Functional - Open Live Tracking tab and verify its form is displayed."""
    tracking.switch_to_live_tracking()
    expect(tracking.split_screen_select).to_be_visible()
    expect(tracking.start_tracking_btn).to_be_visible()


@pytest.mark.functional
def test_trk_nav_006_open_playback_tracking_tab(tracking):
    """TRK-NAV-006: Functional - Open Playback Tracking tab and verify its form is displayed."""
    tracking.switch_to_playback_tracking()
    expect(tracking.from_date_input).to_be_visible()
    expect(tracking.load_playback_btn).to_be_visible()


@pytest.mark.functional
def test_trk_nav_007_switch_live_to_playback_clears_live_form(tracking):
    """TRK-NAV-007: Functional - Switching Live -> Playback shows Playback's form, not stale Live controls."""
    tracking.switch_to_live_tracking()
    expect(tracking.start_tracking_btn).to_be_visible()
    tracking.switch_to_playback_tracking()
    expect(tracking.load_playback_btn).to_be_visible()
    expect(tracking.start_tracking_btn).to_be_hidden()


@pytest.mark.functional
def test_tracking_accessible_via_direct_url(authenticated_page, config):
    """Regression test for retest_bug_report.md NEW-1 (app-wide SPA routing
    defect, confirmed on Dashboard and Unit as of 2026-09-11): a module
    must be reachable by navigating straight to its URL, not only via an
    in-app nav-link click. Deliberately uses page.goto() directly (not
    TrackingPage.open_tracking_page(), which works around this exact bug
    by clicking the nav link instead) -- this test exists specifically to
    catch a regression on direct URL access itself.

    Expected to FAIL until the underlying app bug is fixed: as of this
    writing, a direct goto("/tracking") silently redirects to /home
    instead of loading Tracking. Once the app fix lands, this test turns
    green automatically -- no code change needed here to detect the fix.
    """
    page = authenticated_page
    page.goto(f"{config['base_url']}/tracking")
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/tracking/?$"))
    expect(TrackingPage(page).live_tracking_tab).to_be_visible()


@pytest.mark.functional
def test_trk_nav_008_switch_playback_to_live_clears_playback_form(tracking):
    """TRK-NAV-008: Functional - Switching Playback -> Live shows Live's form, not stale Playback controls."""
    tracking.switch_to_playback_tracking()
    expect(tracking.load_playback_btn).to_be_visible()
    tracking.switch_to_live_tracking()
    expect(tracking.start_tracking_btn).to_be_visible()
    expect(tracking.load_playback_btn).to_be_hidden()
    expect(tracking.from_date_input).to_be_hidden()
