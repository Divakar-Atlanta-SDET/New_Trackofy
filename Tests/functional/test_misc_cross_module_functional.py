"""Phase 11 -- Cross-Module Regression, remaining Security, Accessibility,
Responsive, Reliability (MISC-259 to 286), plus gap #1 (account menu
access from every top-nav module, not just Home/Dashboard/Reports/
Settings).

Not duplicated here (already covered earlier in this module's phases):
- MISC-263 (unauthenticated /profile access denied) -- see
  test_misc_030_unauthenticated_profile_url_access_denied
  (test_misc_profile_functional.py).
- MISC-274 (keyboard account menu) -- see
  test_misc_011_account_menu_keyboard_navigation
  (test_misc_account_menu_functional.py).
- MISC-285 (theme persists after refresh) -- see
  test_misc_148_theme_persists_after_refresh
  (test_misc_appearance_language_functional.py).
- MISC-286 (language persists after refresh) -- see
  test_misc_159_language_persists_after_refresh
  (test_misc_appearance_language_functional.py).

MISC-266/267/268 (cross-account profile/download/ticket access) and
MISC-269/270 (path traversal on a foreign support/feedback attachment)
are honestly skipped below, extending the same established, plan-approved
conclusion as MISC-054/055 and MISC-079: a sub-user shares the owner
account's own identity/data pool rather than being a genuinely
independent second account, so there is no real foreign resource to
target for any of these.
"""
import re
import time

import pytest

from Pages.account_menu_page import AccountMenuPage
from Pages.downloads_page import DownloadsPage
from Pages.feedback_page import FeedbackPage
from Pages.home_page import HomePage
from Pages.login_page import LoginPage
from Pages.support_page import SupportPage


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


# ---------------------------------------------------------------------------
# Account menu access from every module (MISC-259 to 262, plus gap #1)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_259_account_menu_from_home(authenticated_page, config):
    """MISC-259: The Account menu opens correctly from Home."""
    authenticated_page.goto(f"{config['base_url']}/home")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_260_account_menu_from_dashboard(authenticated_page, config):
    """MISC-260: The Account menu opens correctly from Dashboard."""
    authenticated_page.goto(f"{config['base_url']}/dashboard/graphical")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_261_account_menu_from_reports(authenticated_page, config):
    """MISC-261: The Account menu opens correctly from Reports."""
    authenticated_page.goto(f"{config['base_url']}/reports/standard")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_262_account_menu_from_settings(authenticated_page, config):
    """MISC-262: The Account menu opens correctly from Settings."""
    authenticated_page.goto(f"{config['base_url']}/settings")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_gap1_account_menu_from_unit(authenticated_page, config):
    """Gap #1: The Account menu opens correctly from Unit."""
    authenticated_page.goto(f"{config['base_url']}/unit")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_gap1_account_menu_from_tracking(authenticated_page, config):
    """Gap #1: The Account menu opens correctly from Tracking."""
    authenticated_page.goto(f"{config['base_url']}/tracking")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_gap1_account_menu_from_administrator(authenticated_page, config):
    """Gap #1: The Account menu opens correctly from Administrator."""
    authenticated_page.goto(f"{config['base_url']}/administrator")
    authenticated_page.wait_for_timeout(1000)
    menu = AccountMenuPage(authenticated_page)
    menu.open()
    assert menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_gap1_account_menu_from_video_telematics(authenticated_page, config):
    """Gap #1: The Account menu opens correctly from Video Telematics."""
    page = authenticated_page
    page.goto(f"{config['base_url']}/home")
    page.wait_for_timeout(1000)
    nav_link = page.get_by_role("link", name="Video Telematics", exact=True)
    if nav_link.count() == 0:
        nav_link = page.get_by_text("Video Telematics", exact=True)
    nav_link.first.click()
    page.wait_for_timeout(1500)
    menu = AccountMenuPage(page)
    menu.open()
    assert menu.is_open()


# ---------------------------------------------------------------------------
# Unauthenticated access (MISC-264, 265)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_264_unauthenticated_downloads_access_denied(browser, config):
    """MISC-264: Opening /profile/downloads directly, unauthenticated,
    does not show real download data."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/profile/downloads")
        page.wait_for_timeout(2000)
        body_text = page.locator("body").inner_text()
        assert "Download report" not in body_text, (
            f"Expected unauthenticated access to /profile/downloads to be denied, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_265_unauthenticated_support_access_denied(browser, config):
    """MISC-265: Opening /profile/support directly, unauthenticated,
    does not show real ticket data."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/profile/support")
        page.wait_for_timeout(2000)
        body_text = page.locator("body").inner_text()
        assert "Raise Ticket" not in body_text, (
            f"Expected unauthenticated access to /profile/support to be denied, url={page.url!r}"
        )
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Cross-account access / path traversal (MISC-266 to 270) -- honest skips
# ---------------------------------------------------------------------------

_NO_FOREIGN_ACCOUNT_REASON = (
    "per the approved plan's resolved fallback (see test_misc_profile_functional.py's MISC-029 skip and "
    "test_misc_downloads_functional.py's MISC-054/055 skip), a sub-user is not a genuinely independent "
    "account -- it shares the owner's identity/data pool. Without a real second account, there is no "
    "foreign resource to target. Honest skip, matching the REP-COM-021 precedent."
)


@pytest.mark.skip(reason=f"MISC-266 (cross-account profile access) {_NO_FOREIGN_ACCOUNT_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_266_cross_account_profile_access():
    pass


@pytest.mark.skip(reason=f"MISC-267 (cross-account download access) {_NO_FOREIGN_ACCOUNT_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_267_cross_account_download_access():
    pass


@pytest.mark.skip(reason=f"MISC-268 (cross-account support ticket access) {_NO_FOREIGN_ACCOUNT_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_268_cross_account_support_access():
    pass


@pytest.mark.skip(
    reason="MISC-269 (support attachment path traversal) requires a foreign account's attachment URL to "
    f"manipulate -- {_NO_FOREIGN_ACCOUNT_REASON}"
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_269_support_attachment_path_traversal():
    pass


@pytest.mark.skip(
    reason="MISC-270 (feedback attachment path traversal) requires a foreign account's attachment "
    f"URL/filename to manipulate, and there is no feedback-submission list to source one from either -- "
    f"{_NO_FOREIGN_ACCOUNT_REASON}"
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_270_feedback_attachment_path_traversal():
    pass


# ---------------------------------------------------------------------------
# Search injection / XSS (MISC-271 to 273)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_271_search_injection_in_downloads(downloads_page):
    """MISC-271: A SQL-injection-shaped search in Downloads doesn't
    manipulate the query (no error, no unfiltered/full result dump)."""
    before_count = downloads_page.report_count()
    downloads_page.search("' OR 1=1 --")
    downloads_page.page.wait_for_timeout(1000)
    after_count = downloads_page.report_count()
    assert after_count <= before_count, (
        f"Expected the SQLi-shaped search to filter down or match nothing, not return more rows than "
        f"the unfiltered list ({before_count} -> {after_count})"
    )
    assert downloads_page.table.is_visible(), "Expected the Downloads page to remain functional"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_272_search_injection_in_support(support_page):
    """MISC-272: A SQL-injection-shaped search in Support doesn't
    manipulate the query."""
    before_count = support_page.ticket_count()
    support_page.search("' OR 1=1 --")
    support_page.page.wait_for_timeout(1000)
    after_count = support_page.ticket_count()
    assert after_count <= before_count, (
        f"Expected the SQLi-shaped search to filter down or match nothing, not return more rows than "
        f"the unfiltered list ({before_count} -> {after_count})"
    )
    assert support_page.table.is_visible(), "Expected the Support page to remain functional"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_273_xss_in_support_search(support_page):
    """MISC-273: An XSS payload in the Support search box never executes
    as script."""
    support_page.search("<script>window.__support_search_xss=true</script>")
    support_page.page.wait_for_timeout(1000)
    fired = support_page.page.evaluate("() => window.__support_search_xss === true")
    assert not fired, "Expected the XSS payload in search to never execute"


# ---------------------------------------------------------------------------
# Accessibility (MISC-275 to 279)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_275_keyboard_profile_actions(profile_page):
    """MISC-275: Profile page actions (Change Password) are keyboard
    reachable and operable. Confirmed live (Phase 2): this entry point
    opens the Change Password dialog IN PLACE -- it does not navigate to
    /profile/change-password (that's the separate Account Menu entry
    point) -- so success here is the dialog opening, not a URL change."""
    profile_page.change_password_button.focus()
    profile_page.page.keyboard.press("Enter")
    profile_page.page.wait_for_timeout(1000)
    dialog = profile_page.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(
        has_text="Verify your identity"
    )
    assert dialog.is_visible(), "Expected Enter on the focused Change Password control to open its dialog"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_276_keyboard_support_form(support_page):
    """MISC-276: The Raise Ticket form's fields/buttons are reachable via
    Tab in a logical order (smoke check -- Tab from the first field
    eventually reaches a different, real control)."""
    support_page.open_raise_ticket_dialog()
    support_page.vehicle_combobox().focus()
    focused_before = support_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    support_page.page.keyboard.press("Tab")
    support_page.page.wait_for_timeout(200)
    focused_after = support_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert focused_after and focused_after != focused_before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_277_keyboard_feedback_form(feedback_form):
    """MISC-277: The Feedback form's controls are reachable via Tab."""
    feedback_form.version_button("New").focus()
    focused_before = feedback_form.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    feedback_form.page.keyboard.press("Tab")
    feedback_form.page.wait_for_timeout(200)
    focused_after = feedback_form.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert focused_after and focused_after != focused_before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_278_visible_focus(account_menu):
    """MISC-278: A focused control shows a visible focus indicator (not
    outline: none with no other visible focus styling)."""
    account_menu.menu_trigger.focus()
    outline = account_menu.page.evaluate(
        "() => { const cs = getComputedStyle(document.activeElement); "
        "return {outline: cs.outlineStyle, boxShadow: cs.boxShadow, outlineWidth: cs.outlineWidth}; }"
    )
    has_visible_focus = outline["outline"] != "none" or outline["boxShadow"] != "none"
    assert has_visible_focus, f"Expected a visible focus indicator on the focused control, got {outline}"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_279_dialog_escape_closes(support_page):
    """MISC-279: Escape closes the Raise Ticket dialog."""
    support_page.open_raise_ticket_dialog()
    assert support_page.raise_ticket_dialog().is_visible()
    support_page.page.keyboard.press("Escape")
    support_page.page.wait_for_timeout(500)
    assert not support_page.raise_ticket_dialog().is_visible(), "Expected Escape to close the dialog"


# ---------------------------------------------------------------------------
# Responsive (MISC-280 to 282)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_280_account_menu_responsive_tablet(account_menu):
    """MISC-280: The Account menu has no critical overflow at a tablet
    viewport. (Mobile is covered by Bug #34's regression pin --
    test_misc_012b_bug34_account_menu_unreachable_at_mobile_width.)"""
    account_menu.page.set_viewport_size({"width": 768, "height": 1024})
    account_menu.page.wait_for_timeout(500)
    account_menu.open()
    assert account_menu.is_open()
    overflow = account_menu.page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 20, f"Expected no significant horizontal overflow, got {overflow}px"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_281_support_dialog_responsive(support_page):
    """MISC-281: The Raise Ticket dialog remains usable at tablet and
    mobile viewports."""
    for width, height in [(768, 1024), (390, 844)]:
        support_page.page.set_viewport_size({"width": width, "height": height})
        support_page.page.wait_for_timeout(500)
        support_page.open_raise_ticket_dialog()
        assert support_page.raise_ticket_dialog().is_visible(), f"Expected the dialog usable at {width}x{height}"
        support_page.close_ticket_dialog()
        support_page.page.wait_for_timeout(300)


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_282_feedback_dialog_responsive(config, browser, credentials):
    """MISC-282: The Feedback form remains usable at tablet and mobile
    viewports."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        for width, height in [(768, 1024), (390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(f"{config['base_url']}/profile/change-password")
            page.wait_for_timeout(1000)
            fb = FeedbackPage(page)
            fb.open_form()
            assert fb.form().is_visible(), f"Expected the Feedback form usable at {width}x{height}"
            fb.close_form_via_x()
            page.wait_for_timeout(300)
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Reliability (MISC-283, 284)
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason="MISC-283 (a newly-created support ticket survives a refresh) is blocked by Bug #35 "
    "(Bug_Report.md, CRITICAL): Submit Ticket never enables, so there is no way to create a genuinely "
    "new ticket to verify persistence for. Un-skip once Bug #35 is fixed."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_283_refresh_after_new_support_ticket():
    pass


@pytest.mark.skip(
    reason="MISC-284 (authentication follows expected policy after a password change) is blocked by "
    "Bug #37 (Bug_Report.md, CRITICAL): Change Password's Stage 1 identity check always rejects the "
    "correct current password, so no password change can ever be completed to test post-change "
    "authentication behavior against. Un-skip once Bug #37 is fixed."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_284_refresh_after_password_change():
    pass
