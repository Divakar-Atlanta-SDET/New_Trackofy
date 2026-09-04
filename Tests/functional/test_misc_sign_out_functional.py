"""Phase 8 -- Sign Out (MISC-170 to 178, Critical priority).

MISC-170/171 (successful sign-out + redirect off the protected area) are
already covered by test_misc_010_sign_out in
test_misc_account_menu_functional.py -- not duplicated here.

Confirmed live: signing out redirects to the public "/" landing page
(with a `?returnUrl=...` param when access was denied to a specific
protected path), clears the auth token from localStorage, AND invalidates
the session server-side -- replaying a pre-logout storage_state (old
token included) in a brand-new browser context gets a real 401
Unauthorized from the backend, not just a client-side redirect. Every
test here uses a fresh, isolated browser context (never the shared
cached auth session other tests depend on), matching the established
sign-out test pattern.
"""
import time

import pytest

from Pages.account_menu_page import AccountMenuPage
from Pages.home_page import HomePage
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
@pytest.mark.negative
def test_misc_172_back_button_after_logout_denied(browser, config, credentials):
    """MISC-172: Clicking browser Back after sign-out does not restore
    the protected page -- lands back on the public landing page."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        page.goto(f"{config['base_url']}/profile/downloads")
        page.wait_for_timeout(1500)

        menu = AccountMenuPage(page)
        menu.sign_out()
        page.wait_for_timeout(1500)

        page.go_back()
        page.wait_for_timeout(1500)
        assert "/profile/downloads" not in page.url, (
            f"Expected Back after logout to NOT restore the protected page, got {page.url!r}"
        )
        assert page.locator("body").get_by_text("Fleet Intelligence Platform").count() > 0 or "/profile" not in (
            page.url
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_173_refresh_protected_url_after_logout_denied(browser, config, credentials):
    """MISC-173: Refreshing a protected URL after sign-out denies/
    redirects instead of restoring it."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        page.goto(f"{config['base_url']}/profile/downloads")
        page.wait_for_timeout(1500)

        menu = AccountMenuPage(page)
        menu.sign_out()
        page.wait_for_timeout(1500)

        page.goto(f"{config['base_url']}/profile/downloads")
        page.wait_for_timeout(1500)
        assert "/profile/downloads" not in page.url, (
            f"Expected refreshing the protected URL after logout to redirect away, got {page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_174_direct_protected_module_url_after_logout_denied(browser, config, credentials):
    """MISC-174 [Critical]: Direct navigation to a protected module URL
    (Administrator) after sign-out is denied, not rendered."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)

        menu = AccountMenuPage(page)
        menu.sign_out()
        page.wait_for_timeout(1500)

        page.goto(f"{config['base_url']}/administrator")
        page.wait_for_timeout(1500)
        assert "/administrator" not in page.url, (
            f"Expected direct navigation to a protected module after logout to be denied, got {page.url!r}"
        )
        body_text = page.locator("body").inner_text()
        assert "User Management" not in body_text, "Expected the real Administrator page to NOT render"
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_175_old_session_rejected_after_logout(browser, config, credentials):
    """MISC-175 [Critical]: The session is invalidated server-side, not
    just client-side -- replaying a storage_state snapshot captured
    BEFORE logout (old token included) in a brand-new context gets a
    real 401 Unauthorized from the backend, not a silently-successful
    request."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    pre_logout_state = None
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        pre_logout_state = ctx.storage_state()

        menu = AccountMenuPage(page)
        menu.sign_out()
        page.wait_for_timeout(1500)
    finally:
        ctx.close()

    replay_ctx = browser.new_context(base_url=config["base_url"], storage_state=pre_logout_state)
    replay_page = replay_ctx.new_page()
    unauthorized_seen = []

    def _on_response(response):
        if response.status == 401:
            unauthorized_seen.append(response.url)

    replay_page.on("response", _on_response)
    try:
        replay_page.goto(f"{config['base_url']}/profile/downloads")
        replay_page.wait_for_timeout(2500)
        assert unauthorized_seen, (
            "Expected the replayed pre-logout session (old token) to be rejected with a 401 from the "
            "backend, confirming server-side session invalidation, not just a client-side token clear"
        )
    finally:
        replay_ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_176_multi_tab_logout_invalidates_other_tab(browser, config, credentials):
    """MISC-176: Signing out in one tab also invalidates a second tab in
    the same browser context (shared localStorage) once it revalidates
    (reload)."""
    ctx = browser.new_context(base_url=config["base_url"])
    tab_a = ctx.new_page()
    tab_b = ctx.new_page()
    try:
        login_a = LoginPage(tab_a, config)
        login_a.open()
        login_a.login(credentials["username"], credentials["password"])
        tab_a.wait_for_timeout(2000)

        tab_b.goto(f"{config['base_url']}/profile/downloads")
        tab_b.wait_for_timeout(1500)
        assert "/profile/downloads" in tab_b.url

        menu_a = AccountMenuPage(tab_a)
        menu_a.sign_out()
        tab_a.wait_for_timeout(1500)

        tab_b.reload()
        tab_b.wait_for_timeout(2000)
        assert "/profile/downloads" not in tab_b.url, (
            f"Expected tab B to also lose access after tab A signed out, got {tab_b.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_177_login_another_user_after_logout_sees_only_own_data(
    administrator_page, browser, config, credentials
):
    """MISC-177: After signing out, logging in as a different (disposable
    sub-) user shows only that user's own scoped data (their assigned
    vehicle), not the previous account's."""
    admin = administrator_page
    username = _unique_username("pytestlogoutb")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control")
        admin.page.wait_for_timeout(1500)

        ctx_a = browser.new_context(base_url=config["base_url"])
        page_a = ctx_a.new_page()
        try:
            login_a = LoginPage(page_a, config)
            login_a.open()
            login_a.login(credentials["username"], credentials["password"])
            page_a.wait_for_timeout(2000)
            menu_a = AccountMenuPage(page_a)
            menu_a.sign_out()
            page_a.wait_for_timeout(1000)
        finally:
            ctx_a.close()

        ctx_b, page_b = _login_fresh(browser, config, username, password)
        try:
            home_b = HomePage(page_b)
            page_b.wait_for_timeout(1500)
            visible_ids = home_b.visible_vehicle_ids()
            assert visible_ids == ["HP12G9691"], (
                f"Expected User B's own scoped fleet (['HP12G9691']), got {visible_ids}"
            )
        finally:
            ctx_b.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_178_sign_out_keyboard_reachable_and_operable(account_menu):
    """MISC-178: Sign Out is reachable via Tab and operable via Enter,
    not mouse-only."""
    account_menu.menu_trigger.focus()
    account_menu.page.keyboard.press("Enter")
    account_menu.page.wait_for_timeout(500)
    assert account_menu.is_open()

    focused_text = ""
    for _ in range(10):
        account_menu.page.keyboard.press("Tab")
        account_menu.page.wait_for_timeout(150)
        focused_text = account_menu.page.evaluate(
            "() => document.activeElement && document.activeElement.innerText"
        ) or ""
        if "Sign Out" in focused_text:
            break
    assert "Sign Out" in focused_text, f"Expected to reach 'Sign Out' via Tab, last focused: {focused_text!r}"

    account_menu.page.keyboard.press("Enter")
    account_menu.wait_for_visible(account_menu.sign_out_confirm_dialog())
    # Dialog is already open -- dismiss it directly rather than routing
    # through cancel_sign_out(), which would try to re-open the Account
    # menu while this dialog's own backdrop is still up.
    account_menu.sign_out_confirm_dialog().get_by_role("button", name="Cancel", exact=True).click()
    account_menu.page.wait_for_timeout(500)
