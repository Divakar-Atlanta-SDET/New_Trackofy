"""Login Page Phase 5 -- Session & Authentication Security, Brute
Force, Input Security, Transport Security, Error Message Security
(LOGIN-064 to LOGIN-074), plus gap-fill tests for security scenarios
the design doc names in its own "Session & Authentication Security"
(SS17) and "Transport Security" (SS20) sections that the CSV never
operationalizes -- token tampering, a fully garbage/malformed token,
token exposure in the URL, and multi-tab session behavior. These were
identified as gaps during live analysis and are exactly what the user
asked to be checked ("try to abuse a token", "check if some security
tests are missing").

Confirmed live (this session's own investigation, ahead of writing
these tests): logging out invalidates the session server-side, not
just client-side -- replaying a pre-logout storage_state (old token
included) in a brand-new browser context gets a real 401, mirroring
the already-proven MISC-175 pattern for the main app. A TAMPERED token
(one real character flipped inside the JWT) is also correctly
rejected with a 401. Session expiry (LOGIN-066) is honestly skipped --
the real JWT `exp` claim is ~48 hours out, far too long to wait out in
a test. LOGIN-068 (repeated failed logins) is tested lightly (a
handful of attempts, not a real brute-force run) since hammering a
shared login endpoint isn't something to do aggressively against this
environment.
"""
import re

import pytest

from Pages.login_page import LoginPage
from Pages.account_menu_page import AccountMenuPage


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.negative
def test_login_064_block_protected_page_logged_out(browser, config):
    """LOGIN-064 [Critical]: Opening a protected URL directly while
    logged out is denied/redirected."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/administrator")
        page.wait_for_timeout(2000)
        assert "/administrator" not in page.url
        assert "User Management" not in page.locator("body").inner_text()
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.negative
def test_login_065_logout_invalidates_session(browser, config, credentials):
    """LOGIN-065 [Critical]: Logging out invalidates the session --
    replaying the pre-logout token in a fresh context is rejected with
    a real 401 from the backend, not silently accepted."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    pre_logout_state = None
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        pre_logout_state = ctx.storage_state()

        AccountMenuPage(page).sign_out()
        page.wait_for_timeout(1500)
    finally:
        ctx.close()

    replay_ctx = browser.new_context(base_url=config["base_url"], storage_state=pre_logout_state)
    replay_page = replay_ctx.new_page()
    unauthorized_seen = []
    replay_page.on("response", lambda r: unauthorized_seen.append(r.url) if r.status == 401 else None)
    try:
        replay_page.goto(f"{config['base_url']}/home")
        replay_page.wait_for_timeout(2500)
        assert unauthorized_seen, "Expected the replayed pre-logout token to be rejected with a 401"
    finally:
        replay_ctx.close()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.skip(reason="LOGIN-066: the real JWT exp claim is ~48 hours out (confirmed live by decoding a real token) -- far too long to wait out in a test, and no other non-destructive way exists to force expiry in this environment")
def test_login_066_expired_session():
    pass


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.negative
def test_login_067_back_after_logout(browser, config, credentials):
    """LOGIN-067 [Critical]: Browser Back after logout does not expose
    previously-viewed protected content."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        page.goto(f"{config['base_url']}/home")
        page.wait_for_timeout(1000)

        AccountMenuPage(page).sign_out()
        page.wait_for_timeout(1500)

        page.go_back()
        page.wait_for_timeout(1500)
        assert "/home" not in page.url or "Sign in" in page.locator("body").inner_text()
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_068_repeated_failed_login_attempts(login_page, credentials):
    """LOGIN-068 [Critical]: A handful of rapid, consecutive failed
    login attempts are checked for any configured protection (rate
    limit/lockout/challenge). This is a light check (a few attempts,
    not a real brute-force run) -- deliberately triggering a full
    lockout repeatedly against a shared login endpoint isn't safe to
    do here. Reports what protection (if any) is observed rather than
    asserting a specific mechanism the app may not implement."""
    responses = []
    login_page.page.on("response", lambda r: responses.append(r.status) if "token.php" in r.url else None)
    for _ in range(5):
        login_page.username_input.fill(credentials["username"])
        login_page.password_input.fill("WrongPassword!" + str(_))
        if login_page.login_btn.is_enabled():
            login_page.login_btn.click()
        login_page.page.wait_for_timeout(800)
    assert login_page.heading.is_visible(), "Expected the login page to remain functional after repeated failed attempts"
    # Informational: whether a 429 (rate limited) or similar appeared.
    print(f"LOGIN-068: response statuses observed across attempts: {responses}")


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_069_xss_in_identifier(login_page):
    """LOGIN-069 [Critical]: A script-injection payload in the
    username/email field never executes."""
    dialogs = []
    login_page.page.on("dialog", lambda d: (dialogs.append(d), d.dismiss()))
    login_page.login("<script>alert(1)</script>", "SomePass123!")
    login_page.page.wait_for_timeout(2000)
    assert not dialogs, "Expected no JS dialog to fire -- the XSS payload must not execute"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_070_sql_injection_in_identifier(login_page):
    """LOGIN-070 [Critical]: A SQL-injection-style payload doesn't
    manipulate the login query or crash the app."""
    login_page.login("' OR 1=1 --", "anything")
    login_page.page.wait_for_timeout(2000)
    assert "/home" not in login_page.page.url, "Expected the payload treated as a literal (failed) credential, not a query bypass"
    assert login_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_071_oversized_input(login_page):
    """LOGIN-071: Extremely large username/password values are handled
    safely -- no crash."""
    login_page.login("a" * 10000, "b" * 10000)
    login_page.page.wait_for_timeout(2000)
    assert login_page.heading.is_visible() or "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_072_https_authentication(login_page, config):
    """LOGIN-072 [Critical]: The login page and its auth traffic use
    HTTPS."""
    assert login_page.page.url.startswith("https://")
    requests = []
    login_page.page.on("request", lambda r: requests.append(r.url) if "token.php" in r.url else None)
    login_page.username_input.fill("probeuser")
    login_page.password_input.fill("probepass")
    login_page.login_btn.click()
    login_page.page.wait_for_timeout(2000)
    assert requests, "Expected a real auth request to inspect"
    assert all(u.startswith("https://") for u in requests), "Expected every auth request over HTTPS"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_073_no_credentials_in_url(login_page, credentials):
    """LOGIN-073 [Critical]: Credentials are never exposed in the URL
    during or after login."""
    login_page.login(credentials["username"], credentials["password"])
    login_page.page.wait_for_timeout(2000)
    assert credentials["password"] not in login_page.page.url
    assert "password=" not in login_page.page.url.lower()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_074_safe_auth_errors(login_page, credentials):
    """LOGIN-074: cross-reference to Bug #50 (Bug_Report.md) -- a
    nonexistent username and a real username with the wrong password
    produce the IDENTICAL error text, so this specific defect does not
    itself enable username enumeration (even though the message text
    is otherwise unsafe -- see Bug #50)."""
    from components.toast_notifcations import ToastNotifications

    def _get_error(username, password):
        ctx_page = login_page.page
        ctx_page.goto(login_page.config["base_url"])
        ctx_page.wait_for_timeout(1500)
        LoginPage(ctx_page, login_page.config).login(username, password)
        ctx_page.wait_for_timeout(2000)
        toast = ToastNotifications(ctx_page)
        return toast.error_toast.inner_text() if toast.error_toast.count() else ""

    error_nonexistent = _get_error("totally_fake_user_abc123", "WrongPass1!")
    error_wrong_pw = _get_error(credentials["username"], "TotallyWrongPassword999!")
    assert error_nonexistent == error_wrong_pw, (
        "Expected identical error text for a nonexistent user vs. a real user with the wrong password "
        "(prevents username enumeration via error-message differences)"
    )


# ---------------------------------------------------------------------------
# Gap-fill: token-level security tests named in the design doc's own
# "Session & Authentication Security" section but never operationalized
# in the CSV.
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.negative
def test_login_gap_tampered_token_rejected(browser, config, credentials):
    """Gap-fill (design doc SS17: "Tampered tokens are rejected", not
    in the CSV): flipping one character inside a real, valid JWT and
    replaying it in a fresh context is rejected with a real 401."""
    import copy

    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    login = LoginPage(page, config)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)
    state = ctx.storage_state()
    ctx.close()

    tampered_state = copy.deepcopy(state)
    tampered = False
    for origin in tampered_state["origins"]:
        for item in origin["localStorage"]:
            if item["name"] == "token" and len(item["value"]) > 20:
                original = item["value"]
                mid = len(original) // 2
                item["value"] = original[:mid] + ("X" if original[mid] != "X" else "Y") + original[mid + 1:]
                tampered = True
    assert tampered, "Expected to find and tamper the real 'token' localStorage value"

    replay_ctx = browser.new_context(base_url=config["base_url"], storage_state=tampered_state)
    replay_page = replay_ctx.new_page()
    unauthorized_seen = []
    replay_page.on("response", lambda r: unauthorized_seen.append(r.url) if r.status == 401 else None)
    try:
        replay_page.goto(f"{config['base_url']}/home")
        replay_page.wait_for_timeout(2500)
        assert unauthorized_seen, "Expected the tampered token to be rejected with a 401"
    finally:
        replay_ctx.close()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
@pytest.mark.negative
def test_login_gap_malformed_token_rejected(browser, config, credentials):
    """Gap-fill (design doc SS17: "Invalid tokens are rejected", not in
    the CSV): replacing the real token with a completely non-JWT
    garbage string is rejected, not silently treated as authenticated."""
    import copy

    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    login = LoginPage(page, config)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)
    state = ctx.storage_state()
    ctx.close()

    garbage_state = copy.deepcopy(state)
    for origin in garbage_state["origins"]:
        for item in origin["localStorage"]:
            if item["name"] == "token":
                item["value"] = "not-a-real-token-at-all-12345"

    replay_ctx = browser.new_context(base_url=config["base_url"], storage_state=garbage_state)
    replay_page = replay_ctx.new_page()
    try:
        replay_page.goto(f"{config['base_url']}/home")
        replay_page.wait_for_timeout(2500)
        assert "/home" not in replay_page.url, "Expected a malformed token to be denied access, not silently accepted"
    finally:
        replay_ctx.close()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_gap_token_not_in_url(login_page, credentials):
    """Gap-fill (design doc SS17: "Sensitive tokens are not
    unnecessarily exposed in URLs or logs", not in the CSV): the real
    JWT never appears as a URL parameter during or after login."""
    login_page.login(credentials["username"], credentials["password"])
    login_page.page.wait_for_timeout(2000)
    token = login_page.page.evaluate("() => localStorage.getItem('token')")
    assert token, "Expected a real token to check for"
    assert token not in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.security
def test_login_gap_multi_tab_logout(browser, config, credentials):
    """Gap-fill (design doc SS17: "Multiple tabs follow the intended
    session behavior", not in the CSV): signing out in one tab (same
    browser context) also invalidates a second tab once it revalidates."""
    ctx = browser.new_context(base_url=config["base_url"])
    tab1 = ctx.new_page()
    login = LoginPage(tab1, config)
    login.open()
    login.login(credentials["username"], credentials["password"])
    tab1.wait_for_timeout(2000)

    tab2 = ctx.new_page()
    tab2.goto(f"{config['base_url']}/home")
    tab2.wait_for_timeout(1500)
    assert "/home" in tab2.url, "Expected tab 2 to share the authenticated session"

    AccountMenuPage(tab1).sign_out()
    tab1.wait_for_timeout(1500)

    tab2.reload()
    tab2.wait_for_timeout(2000)
    assert "/home" not in tab2.url, "Expected tab 2 to lose access once tab 1 signed out (shared localStorage)"
    ctx.close()
