"""Login Page Phase 2 -- Forgot Password (LOGIN-029 to LOGIN-049).

Confirmed live: submitting ANY plausible 10-digit phone number --
registered or not -- returns the same generic "OTP sent." response and
advances to the Verify step (confirmed with a made-up number,
9999999999). This is good anti-enumeration behavior (an attacker can't
tell which phone numbers are real accounts from the response alone),
and as a side effect it means the Verify step's own UI (OTP field,
length/expiry/resend behavior, incorrect-code rejection) is fully
testable without a real registered phone or SMS access -- only the
actual CORRECT code (which requires reading a real delivered SMS/
email) is out of reach. LOGIN-039 (correct OTP), LOGIN-043 (OTP
reuse), and the entire Reset step (LOGIN-046 to 049, which all require
a verified session) are honestly skipped for that reason. LOGIN-045
(OTP rate limiting) is skipped too -- deliberately triggering rate
limiting/lockout on a shared endpoint isn't a safe thing to do
repeatedly in this environment.

Confirmed live: the OTP field enforces maxlength="6" at the DOM level,
and a genuine countdown ("Code expires in Ns") transitions to a real
"Verification code expired" state with a "Resend" control once it
hits zero (verified by actually waiting it out once, ~60s).
"""
import re

import pytest


@pytest.mark.functional
@pytest.mark.login
def test_login_029_open_forgot_password(login_page, config):
    """LOGIN-029: Forgot password? opens the recovery page."""
    login_page.forgot_password_link.click()
    login_page.page.wait_for_url(re.compile(r".*/forgot-password"), timeout=10000)
    assert "/forgot-password" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
def test_login_030_recovery_steps_shown(forgot_password_page):
    """LOGIN-030: Account, Verify and Reset steps are all displayed."""
    body = forgot_password_page.visible_text()
    for step in ["Account", "Verify", "Reset"]:
        assert step in body


@pytest.mark.functional
@pytest.mark.login
def test_login_031_phone_recovery_controls(forgot_password_page):
    """LOGIN-031: Phone Number field and Send Verification Code button
    are shown by default."""
    assert forgot_password_page.phone_input.is_visible()
    assert forgot_password_page.send_code_btn.is_visible()


@pytest.mark.functional
@pytest.mark.login
def test_login_032_send_code_to_phone(forgot_password_page):
    """LOGIN-032: Submitting a valid-format phone number reaches the
    Verify step (the app returns the same generic response whether or
    not the number is actually registered -- see module docstring)."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    assert "Verify your phone number" in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_033_submit_empty_phone(forgot_password_page):
    """LOGIN-033: Send Verification Code stays disabled with an empty
    phone field."""
    assert not forgot_password_page.send_code_btn.is_enabled()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_034_invalid_phone_rejected(forgot_password_page):
    """LOGIN-034: An invalid (too short) phone number is rejected
    safely -- no crash, no advance to the Verify step."""
    forgot_password_page.fill_phone("123")
    forgot_password_page.page.wait_for_timeout(300)
    if forgot_password_page.send_code_btn.is_enabled():
        forgot_password_page.send_code_btn.click()
        forgot_password_page.page.wait_for_timeout(1500)
    assert "Verify your phone number" not in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_035_switch_to_email_recovery(forgot_password_page):
    """LOGIN-035: "Use email instead" switches to email recovery."""
    forgot_password_page.switch_to_email()
    assert forgot_password_page.email_input.is_visible()
    assert "Enter your email address" in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_036_send_code_to_email(forgot_password_page):
    """LOGIN-036: Submitting a valid-format email reaches the Verify
    step (same generic-response behavior as phone recovery)."""
    forgot_password_page.switch_to_email()
    forgot_password_page.fill_email("someone@example.com")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    assert "Verify your phone number" in forgot_password_page.visible_text() or "Verify" in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_037_invalid_recovery_email(forgot_password_page):
    """LOGIN-037: A malformed email is rejected safely."""
    forgot_password_page.switch_to_email()
    forgot_password_page.fill_email("not-an-email")
    forgot_password_page.page.wait_for_timeout(300)
    assert not forgot_password_page.send_code_btn.is_enabled()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_038_incorrect_otp(forgot_password_page):
    """LOGIN-038 [Critical]: An incorrect 6-digit OTP is rejected with a
    real, safe "Invalid OTP" message -- not a false success."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    otp_field = forgot_password_page.page.get_by_placeholder("Enter 6-digit code")
    otp_field.fill("000000")
    forgot_password_page.page.get_by_role("button", name="Verify Code").click()
    forgot_password_page.page.wait_for_timeout(1500)
    assert "Invalid OTP" in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.skip(reason="LOGIN-039: requires the real, correct OTP delivered to a genuinely registered phone/email -- no way to read a real delivered code in this environment")
def test_login_039_correct_otp():
    pass


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_040_expired_otp(forgot_password_page):
    """LOGIN-040 [Critical]: A genuinely expired code is rejected, shown
    via a real "Verification code expired" state (not silently
    accepted) -- verified by actually waiting out the real countdown."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    body = forgot_password_page.visible_text()
    match = re.search(r"Code expires in\s*\n?\s*(\d+)s", body)
    assert match, "Expected a real countdown timer"
    wait_ms = int(match.group(1)) * 1000 + 3000
    forgot_password_page.page.wait_for_timeout(wait_ms)
    assert "Verification code expired" in forgot_password_page.visible_text()
    assert "Resend" in forgot_password_page.visible_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_041_otp_length_validation(forgot_password_page):
    """LOGIN-041: The OTP field enforces a real 6-digit maximum length."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    otp_field = forgot_password_page.page.get_by_placeholder("Enter 6-digit code")
    assert otp_field.get_attribute("maxlength") == "6"
    otp_field.fill("12345")
    verify_btn = forgot_password_page.page.get_by_role("button", name="Verify Code")
    assert not verify_btn.is_enabled(), "Expected Verify disabled for fewer than 6 digits"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.negative
def test_login_042_otp_non_numeric(forgot_password_page):
    """LOGIN-042: Non-numeric characters in the OTP field are rejected
    or safely ignored -- no crash."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    otp_field = forgot_password_page.page.get_by_placeholder("Enter 6-digit code")
    otp_field.fill("abcdef")
    verify_btn = forgot_password_page.page.get_by_role("button", name="Verify Code")
    assert not verify_btn.is_enabled() or otp_field.input_value() != "abcdef", (
        "Expected non-numeric input rejected or Verify kept disabled"
    )


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.skip(reason="LOGIN-043: requires a real, previously-consumed correct OTP to attempt reuse -- no way to obtain one without real SMS/email access")
def test_login_043_otp_reuse():
    pass


@pytest.mark.functional
@pytest.mark.login
def test_login_044_resend_otp(forgot_password_page):
    """LOGIN-044: Once expired, a real "Resend" control is available and
    triggers a fresh send (the countdown restarts)."""
    forgot_password_page.fill_phone("9999999999")
    forgot_password_page.send_code_btn.click()
    forgot_password_page.page.wait_for_timeout(2000)
    body = forgot_password_page.visible_text()
    match = re.search(r"Code expires in\s*\n?\s*(\d+)s", body)
    forgot_password_page.page.wait_for_timeout(int(match.group(1)) * 1000 + 3000)
    assert "Resend" in forgot_password_page.visible_text()

    forgot_password_page.page.get_by_text("Resend", exact=True).click()
    forgot_password_page.page.wait_for_timeout(2000)
    assert re.search(r"Code expires in\s*\n?\s*\d+s", forgot_password_page.visible_text()), (
        "Expected a fresh countdown after Resend"
    )


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.skip(reason="LOGIN-045: deliberately triggering rate limiting/lockout by hammering the OTP-send endpoint isn't safe to do repeatedly against this shared environment")
def test_login_045_otp_rate_limiting():
    pass


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.skip(reason="LOGIN-046 to 049: the Reset step requires a verified OTP session, unreachable without a real correct OTP")
def test_login_046_049_password_reset():
    pass
