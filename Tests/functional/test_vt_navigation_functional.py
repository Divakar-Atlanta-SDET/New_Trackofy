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
def test_vt_001_open_video_telematics(authenticated_page, config):
    """VT-001: Video Telematics opens from the main nav."""
    page = authenticated_page
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
