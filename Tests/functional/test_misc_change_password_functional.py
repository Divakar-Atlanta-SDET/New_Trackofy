"""Phase 6 -- Change Password (MISC-115 to 145).

Confirmed live: Change Password's Stage 1 identity check always rejects
the correct current password (Bug #37, Bug_Report.md, CRITICAL) --
reproduced on both the main test account and a freshly created,
disposable sub-user. Stage 2 (New Password / Confirm New Password) stays
genuinely `disabled` in the DOM since Stage 1 never passes, so MISC-121
through MISC-144 (everything gated behind it, including gap #2's
password-visibility cross-field check) cannot be meaningfully exercised
and are honestly skipped, referencing this bug.

Per explicit user instruction, no test in this file changes the shared
main test account's password. MISC-145 (the one scenario that needs
several wrong-password attempts, risking a lockout) uses a disposable
sub-user created and deleted via the Administrator module instead.
"""
import time

import pytest

from Pages.login_page import LoginPage


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _login_fresh(browser, config, username: str, password: str):
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    login = LoginPage(page, config)
    login.open()
    login.login(username, password)
    page.wait_for_timeout(2000)
    return ctx, page


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


@pytest.mark.functional
@pytest.mark.misc
def test_misc_115_open_change_password(change_password_page):
    """MISC-115: Change Password opens with the identity-verification
    stage visible."""
    assert change_password_page.heading.is_visible()
    assert change_password_page.current_password_input.is_visible()
    assert change_password_page.verify_button.is_visible()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_116_current_password_required(change_password_page):
    """MISC-116: Verify stays disabled with a blank current password."""
    assert not change_password_page.verify_button.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_bug37_verify_rejects_the_correct_current_password(change_password_page, credentials):
    """Regression pin for Bug #37 (Bug_Report.md, CRITICAL): entering the
    real, currently-authenticating password and clicking Verify always
    fails with "Unable to verify password" -- Stage 2 never unlocks. This
    covers MISC-117 (correct current password should verify). Asserts the
    confirmed-broken behavior; flip both assertions once the app is fixed.
    """
    change_password_page.verify_current_password(credentials["password"])
    assert change_password_page.contains_any_text(["Unable to verify password"]), (
        "Bug #37: expected the 'Unable to verify password' error even for the correct password. "
        "If this no longer appears, the app may have been fixed."
    )
    assert not change_password_page.is_stage_two_unlocked(), (
        "Bug #37: Stage 2 (New/Confirm Password) should currently (still) stay locked. If it's now "
        "unlocked, the app has been fixed -- un-skip MISC-121 through MISC-144 below."
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_118_incorrect_current_password_rejected(change_password_page):
    """MISC-118: An incorrect current password is rejected. Note: because
    of Bug #37, verification currently fails unconditionally -- but
    rejection is also the correct, expected behavior for a genuinely wrong
    password, so this remains a meaningful check either way."""
    change_password_page.verify_current_password("definitely-wrong-password-123!")
    assert not change_password_page.is_stage_two_unlocked()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_119_current_password_masking(change_password_page):
    """MISC-119: The current password field is masked by default."""
    assert change_password_page.current_password_input.get_attribute("type") == "password"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_120_current_password_visibility_toggle(change_password_page):
    """MISC-120: The visibility toggle reveals/hides the current password
    without altering its value."""
    change_password_page.type_into(change_password_page.current_password_input, "Secret123!")
    change_password_page.current_password_toggle.click()
    change_password_page.page.wait_for_timeout(300)
    assert change_password_page.current_password_input.get_attribute("type") == "text"
    assert change_password_page.current_password_input.input_value() == "Secret123!"

    change_password_page.current_password_toggle.click()
    change_password_page.page.wait_for_timeout(300)
    assert change_password_page.current_password_input.get_attribute("type") == "password"
    assert change_password_page.current_password_input.input_value() == "Secret123!"


_BLOCKED_REASON = (
    "is blocked by Bug #37 (Bug_Report.md, CRITICAL): Change Password's Stage 1 identity check always "
    "rejects the correct current password, so Stage 2 (New Password / Confirm New Password) stays "
    "genuinely disabled and can never be reached to test. Un-skip once Bug #37 is fixed -- see "
    "test_misc_bug37_verify_rejects_the_correct_current_password."
)


@pytest.mark.skip(reason=f"MISC-121 (new password required) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_121_new_password_required():
    pass


@pytest.mark.skip(reason=f"MISC-122 (confirm password required) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_122_confirm_password_required():
    pass


@pytest.mark.skip(reason=f"MISC-123 (matching new passwords accepted) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_123_matching_new_passwords():
    pass


@pytest.mark.skip(reason=f"MISC-124 (mismatched new passwords flagged) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_124_mismatched_new_passwords():
    pass


@pytest.mark.skip(reason=f"MISC-125 (8-character boundary accepted) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_125_eight_char_boundary():
    pass


@pytest.mark.skip(reason=f"MISC-126 (7-character password rejected) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_126_seven_char_rejected():
    pass


@pytest.mark.skip(reason=f"MISC-127 (missing uppercase rejected) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_127_missing_uppercase():
    pass


@pytest.mark.skip(reason=f"MISC-128 (missing lowercase rejected) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_128_missing_lowercase():
    pass


@pytest.mark.skip(reason=f"MISC-129 (missing number rejected) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_129_missing_number():
    pass


@pytest.mark.skip(reason=f"MISC-130 (missing special character rejected) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_130_missing_special_char():
    pass


@pytest.mark.skip(reason=f"MISC-131 (all password rules satisfied) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_131_all_rules_satisfied():
    pass


@pytest.mark.skip(reason=f"MISC-132 (new password masking) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_132_new_password_masking():
    pass


@pytest.mark.skip(
    reason=f"MISC-133 (new password visibility toggle -- also gap #2, the cross-field visibility-leak "
    f"check) {_BLOCKED_REASON}"
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_133_new_password_visibility_toggle():
    pass


@pytest.mark.skip(reason=f"MISC-134 (confirm password masking) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_134_confirm_password_masking():
    pass


@pytest.mark.skip(
    reason=f"MISC-135 (confirm password visibility toggle -- also gap #2, the cross-field visibility-leak "
    f"check) {_BLOCKED_REASON}"
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_135_confirm_password_visibility_toggle():
    pass


@pytest.mark.skip(reason=f"MISC-136 (old password reuse policy) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_136_old_password_reuse():
    pass


@pytest.mark.skip(reason=f"MISC-137 (very long password -- confirmed live maxlength=24) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_137_very_long_password():
    pass


@pytest.mark.skip(reason=f"MISC-138 (Unicode password handling) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_138_unicode_password():
    pass


@pytest.mark.skip(reason=f"MISC-139 (whitespace password handling) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_139_whitespace_password():
    pass


@pytest.mark.skip(reason=f"MISC-140 (successful password update) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_140_successful_update():
    pass


@pytest.mark.skip(reason=f"MISC-141 (old password rejected after update) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_141_old_password_invalid_after_update():
    pass


@pytest.mark.skip(reason=f"MISC-142 (new password authenticates after update) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_142_new_password_authenticates():
    pass


@pytest.mark.skip(reason=f"MISC-143 (simulated server failure on update) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_143_server_failure_on_update():
    pass


@pytest.mark.skip(reason=f"MISC-144 (session expiry during update) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_144_session_expiry_during_update():
    pass


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_145_repeated_wrong_current_password(administrator_page, browser, config):
    """MISC-145: Repeated wrong current-password attempts are consistently
    rejected (and any rate-limit/lockout control, if configured, would
    show up here). Uses a disposable sub-user, created and deleted via the
    Administrator module -- never the shared main test account -- so
    repeated failed attempts carry no risk to the credentials every other
    test in this suite depends on."""
    admin = administrator_page
    username = _unique_username("pytestpwlock")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control")
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, username, password)
        try:
            page.goto(f"{config['base_url']}/profile/change-password")
            page.wait_for_timeout(1500)
            current_pw = page.get_by_placeholder("Enter current password")
            verify_btn = page.get_by_role("button", name="Verify")
            new_pw = page.get_by_role("textbox", name="New Password", exact=True)

            for _ in range(5):
                current_pw.click()
                page.keyboard.press("Control+A")
                page.keyboard.type("definitely-wrong-password", delay=15)
                verify_btn.click()
                page.wait_for_timeout(1000)

            body_text = page.locator("body").inner_text()
            assert "Unable to verify password" in body_text or "locked" in body_text.lower() or (
                "too many" in body_text.lower()
            ), f"Expected rejection/lockout messaging after 5 wrong attempts, got: {body_text[:300]!r}"
            assert not new_pw.is_enabled(), "Stage 2 should still be locked after repeated wrong attempts"
        finally:
            ctx.close()
    finally:
        _delete_if_exists(admin, username)
