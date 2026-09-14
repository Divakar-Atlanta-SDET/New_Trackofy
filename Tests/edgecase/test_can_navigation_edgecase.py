"""Regression test for Bug_Report.md #74 (Live Fleet Map overlay
click-interception). Originally filed as: the
".can-map-viewport-boundary" full-viewport wrapper is itself
pointer-events:none, but an unstyled child <div> inside it
(pointer-events:auto) sits on top of the CAN sub-menu and intercepts a
plain, unforced click on the "Unit" nav link -- reproduced 3/3 at the
time.

Reverified live 2026-09-13 (4 independent checks: 3 fresh manual
sessions plus this test): the bug no longer reproduces. The overlay's
only child (<app-can-map-window>) now computes pointer-events:none
(inherited, not "auto") and has a collapsed 0x0 bounding rect, so it
cannot intercept anything. A plain, unforced click on Unit -- and on
every other CAN sub-nav link (Trends/Reports/Alerts/Settings/Dashboard)
-- now succeeds and navigates correctly. Bug #74 is FIXED; this test
now pins that fixed state instead of the old broken one.
"""
import pytest


@pytest.mark.edgecase
@pytest.mark.can
def test_can_nav_edge_001_unforced_click_on_unit_nav_is_blocked_by_map_overlay(can_dashboard_page):
    page = can_dashboard_page.page
    overlay = page.locator(".can-map-viewport-boundary")
    assert overlay.count() > 0, "Expected the Live Fleet Map viewport-boundary overlay to be present"

    try:
        can_dashboard_page.nav_unit.click(timeout=8000)
        navigated = True
    except Exception:
        navigated = False

    assert navigated, (
        "Expected Bug #74 to be fixed: a plain, unforced click on the Unit nav link should reach it "
        "and navigate successfully. If this fails, the map-overlay click-interception bug is back -- "
        "re-add the force=True workaround in CanBasePage.safe_click if it was removed."
    )
    page.wait_for_url("**/can/units", timeout=5000)
