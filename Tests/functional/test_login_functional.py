"""Login Page Phase 1 -- Page load, fields, Sign In, Password,
Terms & Privacy (LOGIN-001 to LOGIN-028).

Confirmed live: the heading reads "Sign in to you account" (a real
typo, Bug #48, Bug_Report.md) -- LoginPage.heading matches this exact
live text rather than the correct "your account", since that's what
actually renders. The Terms & Privacy checkbox is CHECKED by default;
unchecking it disables the real Sign in button (a genuine `disabled`
attribute), confirmed live. Every failed-login scenario (invalid
username, wrong password) surfaces the same raw technical error --
"Http failure response for https://beta2.trackofy.com/trackofy_api_new/
token.php: 401 Unauthorized" -- not a safe message (Bug #50,
Bug_Report.md); tests here pin this as the current real (broken)
behavior rather than asserting a safe message that doesn't exist. The
message IS at least identical for a nonexistent username vs. a real
username with the wrong password, so it doesn't by itself enable
username enumeration.
"""
import re

import pytest

from components.toast_notifcations import ToastNotifications


def _error_text(page) -> str:
    toast = ToastNotifications(page)
    return toast.error_toast.inner_text() if toast.error_toast.count() else ""


@pytest.mark.functional
@pytest.mark.login
def test_login_001_page_loads(login_page):
    """LOGIN-001: The login page loads with its core controls, no
    broken layout."""
    assert login_page.heading.is_visible()
    assert login_page.username_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.login_btn.is_visible()


@pytest.mark.functional
@pytest.mark.login
def test_login_002_branding_and_feature_cards(login_page):
    """LOGIN-002: The promotional left section shows the branding and
    all 5 feature cards."""
    body = login_page.visible_text()
    for text in [
        "Fleet Intelligence Platform", "Control every mile.", "Optimize every move.",
        "Tracking", "Smart Alerts", "Video Telematics", "Asset Health", "Reports & Insights",
    ]:
        assert text in body, f"Expected {text!r} in the promotional section"


@pytest.mark.functional
@pytest.mark.login
def test_login_003_username_field(login_page):
    """LOGIN-003: Username or Email field and its placeholder are shown."""
    assert login_page.username_input.is_visible()
    assert login_page.username_input.get_attribute("placeholder") == "Enter username or email"


@pytest.mark.functional
@pytest.mark.login
def test_login_004_password_field(login_page):
    """LOGIN-004: Password field and its placeholder are shown."""
    assert login_page.password_input.is_visible()
    assert login_page.password_input.get_attribute("placeholder") == "Enter password"


@pytest.mark.functional
@pytest.mark.login
def test_login_005_valid_login(login_page, credentials, config):
    """LOGIN-005: Valid username + password authenticates and redirects
    to the authenticated landing page."""
    login_page.login(credentials["username"], credentials["password"])
    login_page.page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    assert "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.skip(reason="LOGIN-006: no known valid email address for the test account (TEST_USERNAME is a username, e.g. tarun_01, not an email) -- cannot exercise email-based login without one")
def test_login_006_valid_email_login():
    pass


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_007_invalid_username_safe_error(login_page):
    """LOGIN-007 (Bug #50, Bug_Report.md): authentication fails for an
    invalid username -- pinned here as the current real error text,
    not the safe message the CSV expects."""
    login_page.login("totally_invalid_user_xyz", "SomePass123!")
    login_page.page.wait_for_timeout(2000)
    assert "/home" not in login_page.page.url
    assert "401 Unauthorized" in _error_text(login_page.page), (
        "Bug #50: expected the raw technical error (if this now fails with a safe message, the app has been fixed)"
    )


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_008_invalid_email_format(login_page):
    """LOGIN-008: A malformed email is rejected or authentication fails
    safely -- no crash."""
    login_page.login("not-an-email@@bad", "SomePass123!")
    login_page.page.wait_for_timeout(2000)
    assert "/home" not in login_page.page.url
    assert login_page.heading.is_visible(), "Expected the login page to remain functional"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_009_incorrect_password_safe_error(login_page, credentials):
    """LOGIN-009 (Bug #50, Bug_Report.md): a real username with the
    wrong password fails to authenticate -- same raw error as an
    invalid username (at least not a username-enumeration vector)."""
    login_page.login(credentials["username"], "TotallyWrongPassword999!")
    login_page.page.wait_for_timeout(2000)
    assert "/home" not in login_page.page.url
    assert "401 Unauthorized" in _error_text(login_page.page)


@pytest.mark.functional
@pytest.mark.login
def test_login_010_both_fields_empty(login_page):
    """LOGIN-010: Sign in stays disabled with both fields empty -- no
    request is submitted."""
    assert not login_page.login_btn.is_enabled()


@pytest.mark.functional
@pytest.mark.login
def test_login_011_username_empty(login_page):
    """LOGIN-011: Sign in stays disabled with only password filled."""
    login_page.password_input.fill("SomePass123!")
    assert not login_page.login_btn.is_enabled()


@pytest.mark.functional
@pytest.mark.login
def test_login_012_password_empty(login_page, credentials):
    """LOGIN-012: Sign in stays disabled with only username filled."""
    login_page.username_input.fill(credentials["username"])
    assert not login_page.login_btn.is_enabled()


@pytest.mark.functional
@pytest.mark.login
def test_login_013_leading_trailing_spaces(login_page, credentials):
    """LOGIN-013: An identifier with leading/trailing spaces still
    authenticates (normalized) or fails safely -- no crash either way."""
    login_page.login(f"  {credentials['username']}  ", credentials["password"])
    login_page.page.wait_for_timeout(2000)
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_014_oversized_username(login_page):
    """LOGIN-014: An extremely long identifier is handled safely --
    input is accepted by the field, and the app remains stable on
    submit (no crash)."""
    long_value = "a" * 5000
    login_page.username_input.fill(long_value)
    login_page.password_input.fill("SomePass123!")
    if login_page.login_btn.is_enabled():
        login_page.login_btn.click()
        login_page.page.wait_for_timeout(2000)
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_015_special_characters_identifier(login_page):
    """LOGIN-015: Special characters in the identifier are handled
    safely -- no crash, no script execution."""
    dialogs = []
    login_page.page.on("dialog", lambda d: (dialogs.append(d), d.dismiss()))
    login_page.login("!@#$%^&*()_+-=", "SomePass123!")
    login_page.page.wait_for_timeout(2000)
    assert not dialogs
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
def test_login_016_unicode_identifier(login_page):
    """LOGIN-016: Unicode characters in the identifier are handled
    safely -- no crash."""
    login_page.login("用户名пользователь🚀", "SomePass123!")
    login_page.page.wait_for_timeout(2000)
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
def test_login_017_password_masked_by_default(login_page):
    """LOGIN-017: The password field is masked (type=password) by
    default."""
    assert login_page.is_password_masked()


@pytest.mark.functional
@pytest.mark.login
def test_login_018_019_reveal_and_mask_password(login_page):
    """LOGIN-018/019: The visibility toggle reveals then re-masks the
    password without changing its value."""
    login_page.password_input.fill("Secret123!")
    login_page.toggle_password_visibility()
    assert not login_page.is_password_masked(), "LOGIN-018: expected the password revealed"
    assert login_page.password_input.input_value() == "Secret123!"

    login_page.toggle_password_visibility()
    assert login_page.is_password_masked(), "LOGIN-019: expected the password masked again"
    assert login_page.password_input.input_value() == "Secret123!"


@pytest.mark.functional
@pytest.mark.login
def test_login_020_visibility_toggle_does_not_submit(login_page):
    """LOGIN-020: Clicking the visibility toggle doesn't submit the
    login form."""
    login_page.password_input.fill("Secret123!")
    login_page.toggle_password_visibility()
    login_page.page.wait_for_timeout(1000)
    assert login_page.heading.is_visible(), "Expected to remain on the login page"


@pytest.mark.functional
@pytest.mark.login
def test_login_021_special_characters_password(login_page, credentials):
    """LOGIN-021: Special characters in the password are handled
    safely -- entering them doesn't crash the form."""
    login_page.login(credentials["username"], "!@#$%^&*()_+-=<>?")
    login_page.page.wait_for_timeout(2000)
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
def test_login_022_password_copy_paste(login_page):
    """LOGIN-022: Pasting into the password field inserts the value
    correctly and it remains masked."""
    login_page.password_input.evaluate(
        "(el, value) => { el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); }",
        "PastedSecret!23",
    )
    assert login_page.password_input.input_value() == "PastedSecret!23"
    assert login_page.is_password_masked()


@pytest.mark.functional
@pytest.mark.login
def test_login_023_terms_checkbox_displayed(login_page):
    """LOGIN-023: The Terms & Privacy checkbox and its text are visible."""
    assert login_page.terms_checkbox.is_visible()
    assert "I accept Terms & Privacy" in login_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_024_uncheck_acceptance(login_page):
    """LOGIN-024: The checkbox starts checked and can be unchecked."""
    assert login_page.terms_checkbox.is_checked(), "Expected checked by default"
    login_page.terms_checkbox.uncheck()
    assert not login_page.terms_checkbox.is_checked()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_025_prevent_login_without_acceptance(login_page, credentials):
    """LOGIN-025 [Critical]: Sign in is disabled when Terms & Privacy is
    unchecked, even with otherwise-valid credentials filled."""
    login_page.terms_checkbox.uncheck()
    login_page.username_input.fill(credentials["username"])
    login_page.password_input.fill(credentials["password"])
    assert not login_page.login_btn.is_enabled(), "Expected Sign in disabled without Terms acceptance"


@pytest.mark.functional
@pytest.mark.login
def test_login_026_login_with_acceptance(login_page, credentials, config):
    """LOGIN-026: With the checkbox in its default checked state, login
    proceeds successfully."""
    assert login_page.terms_checkbox.is_checked()
    login_page.login(credentials["username"], credentials["password"])
    login_page.page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    assert "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
def test_login_027_open_terms(login_page):
    """LOGIN-027: The Terms link opens the correct content."""
    href = login_page.terms_link.get_attribute("href")
    assert href == "/terms-and-conditions"


@pytest.mark.functional
@pytest.mark.login
def test_login_028_open_privacy(login_page):
    """LOGIN-028: The Privacy link opens the correct content."""
    href = login_page.privacy_link.get_attribute("href")
    assert href == "/privacy-policy"


@pytest.mark.functional
@pytest.mark.login
def test_login_bug48_heading_typo(login_page):
    """Bug #48 (Bug_Report.md, Minor): regression pin for the real
    "Sign in to you account" typo (missing "r" in "your")."""
    assert login_page.heading.is_visible(), (
        "Bug #48: expected the heading text (with its current typo) to still match "
        "(if this now fails, the typo may have been fixed -- update the locator)"
    )


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.accessibility
def test_login_bug49_password_toggle_not_keyboard_reachable(login_page):
    """Bug #49 (Bug_Report.md, Medium): regression pin -- the password
    visibility toggle has tabindex="-1" and is skipped by Tab."""
    tabindex = login_page.password_toggle_btn.get_attribute("tabindex")
    assert tabindex == "-1", (
        "Bug #49: expected tabindex=-1 on the password toggle (if this now fails, the app has been fixed)"
    )
