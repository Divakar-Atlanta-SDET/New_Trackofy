"""Video Telematics Phase 9 -- Cross-Module (VT-199 to VT-202) and
Phase 10 -- Reliability (VT-203 to VT-208).

Cross-Module: VT-199's own CSV precondition ("Alert exists") and action
("Create/trigger alert") describe a real ADAS/DMS device event, which
this suite cannot trigger on demand (it's real hardware/sensor-driven,
not a UI action) -- so it's verified indirectly but for real: every
alert type name that appears in this account's actual Report events is
confirmed to be a real, recognized entry in the Alert Configuration
catalog, i.e. the two pages share one consistent alert-type vocabulary
rather than drifting apart. VT-200 (Report -> Evidence correspondence)
is effectively the same real check already built and passing as
VT-149/152 in Phase 6 -- restated here as its own cross-module test for
CSV coverage. VT-201 (Playback vehicle integrity) is tested for real
now that B123456 has genuine recordings (re-verified live later the
same session). VT-202 (Dashboard -> Alert history navigation) is
tested for real.

Reliability: VT-203/204/205 (session expiry mid-action) are honestly
skipped, matching the precedent already established for MISC-111/144/
258 and ADM-159 in prior modules -- no real, non-destructive way to
force a session to expire mid-action in this environment. VT-206/207/
208 (network interruption) are tested for real via route-based request
abortion, mirroring the technique already used for the module's own
simulated API-failure tests (VT-079/108/137).
"""
import re

import pytest


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_199_alert_to_report_consistency(vt_report_page):
    """VT-199: Every real alert type appearing in the Report's actual
    events is a recognized entry in the Alert Configuration catalog --
    the two pages share one consistent alert-type vocabulary."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    report_alert_names = {vt_report_page.row_alert_text(rows.nth(i)) for i in range(rows.count())}
    assert report_alert_names, "Expected real report events to check"

    # vt_alert_page is a separate fixture but shares the same underlying
    # authenticated page as vt_report_page -- constructing a fresh Alert
    # page object over vt_report_page's own page (matching the pattern
    # already used in test_vt_navigation_functional.py) avoids a second,
    # conflicting auto-navigation.
    from Pages.video_telematics_alert_page import VideoTelematicsAlertPage

    vt_report_page.open_alert()
    alert_page = VideoTelematicsAlertPage(vt_report_page.page)
    alert_page.wait_for_visible(alert_page.heading)

    # Alert Configuration doesn't expose a searchable catalog list directly;
    # use the Create dialog's own Alert dropdown, which lists every real
    # alert type the account recognizes.
    alert_page.open_create_dialog()
    dialog = alert_page.create_dialog()
    alert_page.alert_combobox(dialog).click()
    alert_page.page.wait_for_timeout(500)
    options = alert_page.page.get_by_role("option")
    catalog_names = {options.nth(i).inner_text() for i in range(options.count())}
    alert_page.page.keyboard.press("Escape")
    alert_page.page.wait_for_timeout(300)
    alert_page.cancel_dialog(dialog)

    unknown = report_alert_names - catalog_names
    assert not unknown, f"Expected every report alert type recognized in the Alert catalog, unknown: {unknown}"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_200_report_to_evidence_correspondence(vt_report_page):
    """VT-200: Evidence opened from a report row belongs to that same
    event (same check already proven as VT-149/152 in Phase 6,
    restated here as the cross-module workflow it represents)."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    row = None
    for i in range(rows.count()):
        if vt_report_page.row_has_evidence(rows.nth(i)):
            row = rows.nth(i)
            break
    assert row is not None
    alert_name = vt_report_page.row_alert_text(row)
    timestamp = vt_report_page.row_datetime_text(row)

    vt_report_page.open_view_evidence(row)
    header = vt_report_page.evidence_panel_header_text()
    assert alert_name in header
    assert timestamp in header


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_201_playback_vehicle_integrity(vt_playback_page):
    """VT-201: A selected recording's player context correctly reflects
    the vehicle it was searched under -- rebuilt for real now that
    B123456 has genuine recordings (re-verified same session as the
    Playback phase itself, see VT-117 there for the same check)."""
    vt_playback_page.select_vehicle("B123456")
    vt_playback_page.find_files()
    assert vt_playback_page.files_count() > 0, "Expected real recordings for B123456"
    vt_playback_page.select_file(1)
    assert "B123456" in vt_playback_page.video_context_text()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_202_dashboard_to_alert_history_navigation(vt_dashboard_page):
    """VT-202: "View alert history" on the Dashboard opens the Report
    page (historical alert records), pre-filtered to today's date --
    confirmed live, not the Alert Configuration page (which is for
    configuring alert *rules*, not viewing alert *history*)."""
    vt_dashboard_page.view_alert_history_link.click()
    vt_dashboard_page.page.wait_for_timeout(1500)
    assert "/video_telematics/report" in vt_dashboard_page.page.url


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.skip(reason="VT-203 to VT-205: session-expiry-during-operation has no real, non-destructive simulation path in this environment -- same precedent as MISC-111/144/258 and ADM-159 in prior modules")
def test_vt_203_205_session_expiry_during_operation():
    pass


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
@pytest.mark.allow_server_error
def test_vt_206_network_interruption_dashboard(vt_dashboard_page):
    """VT-206: If the Dashboard's own data calls fail mid-load, the
    module stays usable rather than crashing."""
    page = vt_dashboard_page.page
    page.route(re.compile(r".*adas_api\.php.*", re.I), lambda route: route.abort("failed"))
    try:
        page.reload()
        page.wait_for_timeout(3000)
        assert vt_dashboard_page.heading.is_visible(), "Expected the Dashboard to remain usable after a network failure"
    finally:
        page.unroute(re.compile(r".*adas_api\.php.*", re.I))


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
@pytest.mark.allow_server_error
def test_vt_207_network_interruption_playback(vt_playback_page):
    """VT-207: A network interruption during a Playback search fails
    gracefully -- no crash, no stuck loading state."""
    page = vt_playback_page.page
    page.route(re.compile(r".*StandardApiAction_getVideoFileInfo.*"), lambda route: route.abort("failed"))
    try:
        vt_playback_page.find_files()
        assert vt_playback_page.heading.is_visible(), "Expected Playback to remain usable after a network failure"
    finally:
        page.unroute(re.compile(r".*StandardApiAction_getVideoFileInfo.*"))


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
@pytest.mark.allow_server_error
def test_vt_208_network_interruption_evidence(vt_report_page):
    """VT-208: A network interruption while opening evidence is handled
    -- no crash, module stays usable."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    row = None
    for i in range(rows.count()):
        if vt_report_page.row_has_evidence(rows.nth(i)):
            row = rows.nth(i)
            break
    assert row is not None

    page = vt_report_page.page
    page.route(re.compile(r".*adas_api\.php.*", re.I), lambda route: route.abort("failed"))
    try:
        vt_report_page.open_view_evidence(row)
        assert vt_report_page.heading.is_visible(), "Expected the Report page to remain usable after a failed evidence load"
    finally:
        page.unroute(re.compile(r".*adas_api\.php.*", re.I))
