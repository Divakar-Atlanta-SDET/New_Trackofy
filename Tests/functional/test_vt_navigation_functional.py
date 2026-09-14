"""Video Telematics Phase 1 -- Navigation (VT-001 to VT-006).

Confirmed live: the module has its own left-nav (Dashboard/Alert/
Playback/Report) at /video_telematics/{dashboard,alert,playback,report},
plus a persistent Live Fleet Map widget on every sub-page. The module's
own "Dashboard" nav link shares its accessible name with the main app's
global nav Dashboard link -- disambiguated by href in
VideoTelematicsBasePage.
"""
import pytest

from Pages.video_telematics_alert_page import VideoTelematicsAlertPage


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_001_open_video_telematics(vt_authenticated_page, config):
    """VT-001: Video Telematics opens from the main nav.

    Fixed 2026-09-14: previously used `authenticated_page` (the main
    TEST_USERNAME account), which has no Video Telematics entitlement at
    all (confirmed absent from its nav this session) -- the nav_link
    lookup always timed out at 0 matches. Uses the ADAS account (the
    entitled one every other VT fixture uses) instead."""
    page = vt_authenticated_page
    page.goto(f"{config['base_url']}/home")
    page.wait_for_timeout(1000)
    nav_link = page.get_by_role("link", name="Video Telematics", exact=True)
    if nav_link.count() == 0:
        nav_link = page.get_by_text("Video Telematics", exact=True)
    nav_link.first.click()
    page.wait_for_timeout(1500)
    assert "/video_telematics" in page.url


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_accessible_via_direct_url(vt_authenticated_page, config):
    """Regression test for retest_bug_report.md NEW-1 (app-wide SPA
    routing defect), confirmed live 2026-09-14 to also affect Video
    Telematics: a raw page.goto() to any /video_telematics/* route
    silently bounces to /home instead of loading the real page (all 4
    page objects' open() methods were fixed to route through the nav bar
    instead -- see video_telematics_*_page.py). Deliberately uses
    page.goto() directly here, not the fixed page objects, so this test
    exists specifically to catch a regression -- or a real upstream fix
    -- on direct URL access itself.

    Expected to FAIL until the underlying app bug is fixed: as of this
    writing, a direct goto("/video_telematics/dashboard") silently
    redirects to /home instead of loading the Dashboard. Once the app
    fix lands, this test turns green automatically -- no code change
    needed here to detect it.
    """
    page = vt_authenticated_page
    page.goto(f"{config['base_url']}/video_telematics/dashboard")
    page.wait_for_timeout(2000)
    assert page.url.rstrip("/").endswith("/video_telematics/dashboard"), (
        f"NEW-1 regression pin: expected direct URL access to bounce to /home (current confirmed-broken "
        f"behavior); got {page.url!r} instead -- if this is now the real dashboard URL, NEW-1 may be fixed "
        f"for Video Telematics, update this test to assert the real page loaded."
    )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_002_dashboard_navigation(vt_dashboard_page):
    """VT-002: Dashboard opens and is highlighted."""
    assert "/video_telematics/dashboard" in vt_dashboard_page.page.url
    assert vt_dashboard_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_003_alert_navigation(vt_dashboard_page):
    """VT-003: Alert Configuration opens and is highlighted."""
    vt_dashboard_page.open_alert()
    alert_page = VideoTelematicsAlertPage(vt_dashboard_page.page)
    assert alert_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_004_playback_navigation(vt_dashboard_page):
    """VT-004: Video Playback opens and is highlighted."""
    vt_dashboard_page.open_playback()
    assert vt_dashboard_page.contains_texts(["Video Playback"])


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_005_report_navigation(vt_dashboard_page):
    """VT-005: Video Telematics Reports opens and is highlighted."""
    vt_dashboard_page.open_report()
    assert vt_dashboard_page.contains_texts(["Video Telematics Reports"])


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_006_switch_modules_repeatedly(vt_dashboard_page):
    """VT-006: Repeatedly switching Dashboard -> Alert -> Playback ->
    Report -> Dashboard loads each page without state corruption."""
    page = vt_dashboard_page.page
    vt_dashboard_page.open_alert()
    assert VideoTelematicsAlertPage(page).heading.is_visible()

    vt_dashboard_page.open_playback()
    assert vt_dashboard_page.contains_texts(["Video Playback"])

    vt_dashboard_page.open_report()
    assert vt_dashboard_page.contains_texts(["Video Telematics Reports"])

    vt_dashboard_page.open_dashboard()
    assert vt_dashboard_page.heading.is_visible()
    # KPI strip should still render correctly after the round trip
    assert vt_dashboard_page.contains_texts(["Total Vehicles", "Online", "Offline"])
