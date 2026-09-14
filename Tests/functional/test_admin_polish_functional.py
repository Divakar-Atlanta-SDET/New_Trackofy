"""Phase 13 -- Lower-priority polish (Medium/Low), a lighter pass matching
the Home module's Phase 8 treatment: basic smoke checks, not exhaustive
audits.
"""
import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_keyboard_can_reach_and_activate_add_user(administrator_page):
    """Basic keyboard-navigation smoke check: the 'Add User' control is
    keyboard-focusable and activates the wizard via Enter, not just mouse
    click."""
    admin = administrator_page
    admin.add_user_button.focus()
    admin.page.wait_for_timeout(300)
    focused_is_add_user = admin.page.evaluate(
        "() => document.activeElement && document.activeElement.getAttribute('aria-label') === 'Create new user'"
    )
    assert focused_is_add_user, "Expected the Add User button to be keyboard-focusable"

    admin.page.keyboard.press("Enter")
    admin.page.wait_for_timeout(1000)
    assert admin.wizard_dialog().is_visible(), "Expected Enter on the focused Add User button to open the wizard"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_responsive_mobile_viewport_still_usable(administrator_page):
    """Basic responsive smoke check: at a mobile viewport width, the User
    Management page still renders its core controls (heading, Add User)
    without erroring, rather than a full layout/functionality audit."""
    admin = administrator_page
    admin.page.set_viewport_size({"width": 390, "height": 844})
    admin.page.wait_for_timeout(1000)
    try:
        assert admin.add_user_button.count() > 0, "Expected Add User to still be present at mobile width"
        body_text = admin.page.locator("body").inner_text()
        assert "User Management" in body_text, "Expected the page heading still present at mobile width"
    finally:
        admin.page.set_viewport_size({"width": 1280, "height": 800})
        admin.page.wait_for_timeout(500)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_long_username_rejected_gracefully(administrator_page):
    """A very long (165-char) username is NOT accepted -- confirmed live
    2026-09-13: no client-side maxlength exists on the field (a 165-char
    value fills in fine), but Submit fails server-side with a generic
    'fail' toast and the wizard stays open; no user is created. This is a
    minor, low-priority finding worth noting (the error message is
    unhelpfully generic, not a proper validation message) but not a
    display/layout bug -- rewritten from the original premise (that an
    extreme-length username would be accepted and just truncated for
    display), which doesn't match the real behavior."""
    admin = administrator_page
    long_suffix = _unique_username("pytestlong")
    long_username = f"{long_suffix}{'x' * 150}"
    before_count = int(admin.user_count_text() or "0")
    try:
        admin.create_user(long_username, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)
        assert admin.wizard_dialog().is_visible(), (
            "Expected the wizard to stay open after Submit is rejected for an unreasonably long username"
        )
        assert admin.wizard_error_toast_text(), "Expected an error toast explaining the rejection"
        admin.page.keyboard.press("Escape")
        admin.page.wait_for_timeout(500)

        admin.page.reload(); admin.reopen()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        after_count = int(admin.user_count_text() or "0")
        assert after_count == before_count, (
            f"Expected no user created for the rejected long username -- count was {before_count}, "
            f"got {after_count}"
        )
        assert admin.add_user_button.is_visible(), "Expected the page to remain usable afterward"
    finally:
        _delete_if_exists(admin, long_suffix)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_slow_api_shows_loading_state_not_broken_page(administrator_page):
    """API-timeout/slow-network handling smoke check: delaying the user
    list API response doesn't crash the page or show a stale/broken
    state -- it eventually loads correctly once the (delayed) response
    arrives."""
    admin = administrator_page

    def _delay(route):
        admin.page.wait_for_timeout(3000)
        route.continue_()

    admin.page.route("**/*subuser*", _delay)
    admin.page.reload(); admin.reopen()
    admin.page.wait_for_timeout(1000)
    body_during = admin.page.locator("body").inner_text()
    assert "User Management" in body_during, "Expected the page shell to render even while data is loading"

    admin.wait_until_ready()
    admin.page.wait_for_timeout(2500)
    admin.page.unroute("**/*subuser*")
    assert admin.add_user_button.count() > 0, "Expected the page to finish loading normally after the delay"


@pytest.mark.skip(
    reason="Large-dataset rendering (hundreds/thousands of sub-users) is not attemptable in this "
    "account -- seeding that much data would itself be a large, disruptive, real-account mutation "
    "with no clean teardown path. Honest skip, matching the REP-COM-021 precedent (Reports module)."
)
@pytest.mark.functional
@pytest.mark.admin
def test_adm_large_dataset_rendering():
    pass


@pytest.mark.skip(
    reason="No defined performance SLA (page-load or action-response time target) exists anywhere in "
    "this repo or the design doc for the Administrator module -- inventing an arbitrary threshold would "
    "produce a meaningless, brittle test. Honest skip, matching the REP-COM-021 precedent."
)
@pytest.mark.functional
@pytest.mark.admin
def test_adm_performance_targets():
    pass
