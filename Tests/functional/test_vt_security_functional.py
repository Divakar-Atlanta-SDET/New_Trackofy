"""Video Telematics Phase 8 -- Security (VT-180 to VT-198).

Unauthenticated direct-URL access (VT-180 to 183) uses the same
fresh-context pattern established throughout this session (e.g.
MISC-264/265). Cross-account IDOR/read/edit/delete (VT-184 to 192) are
honestly skipped -- this test environment has no genuine second/
foreign account (the ADAS account is the only Video Telematics
account available), matching the precedent already established for
every other module this session. VT-198 (Playback URL authorization)
is honestly skipped too -- real recordings now exist (Phase 5's
account has since accumulated real B123456 data), but the player loads
video through a proprietary WASM-decoded MDVR stream into a blob: URL,
which has no equivalent plain, replayable HTTP URL to test.

VT-197 (Evidence URL authorization) is NOT skipped: it uncovered a
real, CRITICAL, confirmed vulnerability (Bug #45, Bug_Report.md) --
evidence snapshot/video URLs captured from the Report page's evidence
panel are fully downloadable (200 OK, full correct file) from a
completely fresh, unauthenticated browser context with no session,
cookie, or token at all. This test pins that real (broken) behavior.
"""
import pytest


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.negative
def test_vt_180_unauthenticated_dashboard_access_denied(browser, config):
    """VT-180: Opening the Dashboard URL directly, unauthenticated, does
    not show real dashboard content."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/video_telematics/dashboard")
        page.wait_for_timeout(2000)
        assert "Video Telematics Dashboard" not in page.locator("body").inner_text(), (
            f"Expected unauthenticated access denied, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.negative
def test_vt_181_unauthenticated_alert_access_denied(browser, config):
    """VT-181: Opening the Alert Configuration URL directly,
    unauthenticated, does not show real alert data."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/video_telematics/alert")
        page.wait_for_timeout(2000)
        assert "Alert Configuration" not in page.locator("body").inner_text(), (
            f"Expected unauthenticated access denied, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.negative
def test_vt_182_unauthenticated_playback_access_denied(browser, config):
    """VT-182: Opening the Playback URL directly, unauthenticated, does
    not show real playback content."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/video_telematics/playback")
        page.wait_for_timeout(2000)
        assert "Video Playback" not in page.locator("body").inner_text(), (
            f"Expected unauthenticated access denied, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.negative
def test_vt_183_unauthenticated_report_access_denied(browser, config):
    """VT-183: Opening the Report URL directly, unauthenticated, does not
    show real report data."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/video_telematics/report")
        page.wait_for_timeout(2000)
        assert "Video Telematics Reports" not in page.locator("body").inner_text(), (
            f"Expected unauthenticated access denied, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.skip(reason="VT-184 to VT-192: no genuine second/foreign Video Telematics account exists in this test environment to exercise cross-account read/edit/delete/IDOR (same constraint noted throughout this session's other modules)")
def test_vt_184_192_cross_account_idor():
    pass


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_193_report_search_xss(vt_report_page):
    """VT-193: A script-injection payload in the Report search box is
    never executed."""
    page = vt_report_page.page
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d), d.dismiss()))
    vt_report_page.generate()
    vt_report_page.search("<script>alert(1)</script>")
    page.wait_for_timeout(1000)
    assert not dialogs, "Expected no JS dialog to fire -- the XSS payload must not execute"
    assert vt_report_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_194_alert_search_xss(vt_alert_page):
    """VT-194: A script-injection payload in the Alert search box is
    never executed."""
    page = vt_alert_page.page
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d), d.dismiss()))
    vt_alert_page.search("<script>alert(1)</script>")
    page.wait_for_timeout(1000)
    assert not dialogs, "Expected no JS dialog to fire -- the XSS payload must not execute"
    assert vt_alert_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_195_report_search_sql_injection(vt_report_page):
    """VT-195: A SQL-injection-style payload in the Report search box
    doesn't manipulate the query -- no crash, no unfiltered dump."""
    vt_report_page.generate()
    baseline = vt_report_page.rows().count()
    vt_report_page.search("' OR 1=1 --")
    page = vt_report_page.page
    page.wait_for_timeout(1000)
    assert vt_report_page.heading.is_visible(), "Expected the page to remain functional"
    assert vt_report_page.rows().count() <= baseline, (
        "Expected the payload treated as a literal search term, not a query that returns more than the real baseline"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_196_alert_search_sql_injection(vt_alert_page):
    """VT-196: A SQL-injection-style payload in the Alert search box
    doesn't manipulate the query -- no crash, no unfiltered dump."""
    baseline = vt_alert_page.alert_count()
    vt_alert_page.search("' OR 1=1 --")
    assert vt_alert_page.heading.is_visible(), "Expected the page to remain functional"
    assert vt_alert_page.rows().count() <= baseline, (
        "Expected the payload treated as a literal search term, not a query that returns more than the real baseline"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_197_evidence_url_authorization(vt_report_page):
    """VT-197 (Bug #45, Bug_Report.md -- CRITICAL): a real evidence
    snapshot/video URL, captured while authenticated, is confirmed
    fully downloadable (200 OK, correct content-type, correct full
    byte size) from a completely fresh, unauthenticated browser
    context. Pinned here as the current real (broken) behavior."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    row = None
    for i in range(rows.count()):
        if vt_report_page.row_has_evidence(rows.nth(i)):
            row = rows.nth(i)
            break
    assert row is not None, "Expected at least one real evidence-bearing row"

    vt_report_page.open_view_evidence(row)
    page = vt_report_page.page
    page.wait_for_timeout(1500)

    snapshot_url = None
    imgs = page.locator("img")
    for i in range(imgs.count()):
        src = imgs.nth(i).get_attribute("src")
        if src and "new.trackofy.com" in src:
            snapshot_url = src
            break
    assert snapshot_url is not None, "Expected a real evidence snapshot URL to be present in the DOM"

    browser = page.context.browser
    fresh_ctx = browser.new_context(ignore_https_errors=True)
    try:
        fresh_page = fresh_ctx.new_page()
        response = fresh_page.request.get(snapshot_url)
        assert response.status == 200, (
            "Bug #45: expected the evidence URL to still be reachable with zero authentication "
            "(if this now fails with a 401/403, the app has been fixed)"
        )
        assert len(response.body()) > 0, "Bug #45: expected the real file content to still be served, not an empty/blocked response"
    finally:
        fresh_ctx.close()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
@pytest.mark.skip(reason="VT-198: re-verified after real recordings appeared for B123456 -- unlike Report's evidence video (a plain fetchable HTTP URL, Bug #45), Playback loads video through a proprietary WASM-decoded MDVR player (cmsv6player.min.js + libcmsv6decode.wasm) into a blob: URL, which has no equivalent plain, replayable HTTP URL to test unauthenticated access against")
def test_vt_198_playback_url_authorization():
    pass
