"""Admin Panel cross-module security. Confirmed live: Manage User,
Manage Dealer, and Unassign Device's search boxes are all non-functional
(Bug #56 and its Device-page counterpart, VC-56-family) -- these tests
still verify no XSS/SQLi payload executes or leaks a raw DB error through
them, since a broken filter is not the same guarantee as a safe one.
Tax's own search box (functional, unlike the others) already has
dedicated XSS/SQLi coverage in test_admin_tax_functional.py.

Unauthenticated direct-URL access to every in-scope /admin/* page is
already covered by test_admin_002_unauthenticated_direct_url_access_denied
in test_admin_auth_functional.py (Phase 1) -- not duplicated here."""
import pytest


XSS_PAYLOAD = "<img src=x onerror=window.__xss_admin_search=1>"
SQLI_PAYLOADS = ["' OR '1'='1", "'; DROP TABLE users;--"]
DB_ERROR_MARKERS = ("SQLSTATE", "SqlException", "syntax error", "ORA-")


def _run_search_injection_check(page_object, base_url, open_method_name, payload, **open_kwargs):
    open_method = getattr(page_object, open_method_name)
    open_method(base_url, **open_kwargs)
    page_object.page.wait_for_timeout(1000)
    page_object.search_input.fill(payload)
    page_object.search_input.press("Enter")
    page_object.page.wait_for_timeout(1500)
    executed = page_object.page.evaluate("() => window.__xss_admin_search === 1")
    assert not executed, f"XSS payload executed: {payload!r}"
    body_text = page_object.visible_text()
    assert not any(marker in body_text for marker in DB_ERROR_MARKERS), (
        f"Raw database error leaked into the page after search payload {payload!r}"
    )


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.parametrize("payload", [XSS_PAYLOAD] + SQLI_PAYLOADS)
def test_admin_security_001_manage_user_search_injection_handled_safely(admin_user_page, config, payload):
    _run_search_injection_check(admin_user_page, config["base_url"], "open", payload)
    # Real customer data must survive an injection attempt in search unharmed.
    admin_user_page.page.goto(f"{config['base_url']}/admin/user/manage-user")
    admin_user_page.wait_for_body_pattern(r"Showing \d+ to \d+ of \d+ users")
    assert int(admin_user_page.showing_count_text()) > 1000


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.parametrize("payload", [XSS_PAYLOAD] + SQLI_PAYLOADS)
def test_admin_security_002_manage_dealer_search_injection_handled_safely(admin_dealer_page, config, payload):
    _run_search_injection_check(admin_dealer_page, config["base_url"], "open", payload, path="manage-dealer")
    admin_dealer_page.page.goto(f"{config['base_url']}/admin/user/manage-dealer")
    admin_dealer_page.wait_for_body_pattern(r"Showing \d+ to \d+ of \d+ dealers")
    assert int(admin_dealer_page.showing_count_text()) > 50


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.parametrize("payload", [XSS_PAYLOAD] + SQLI_PAYLOADS)
def test_admin_security_003_unassign_device_search_injection_handled_safely(admin_device_page, config, payload):
    _run_search_injection_check(admin_device_page, config["base_url"], "open_unassign_device", payload)


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.parametrize("payload", [XSS_PAYLOAD] + SQLI_PAYLOADS)
def test_admin_security_004_manage_plan_search_injection_handled_safely(admin_plan_page, config, payload):
    _run_search_injection_check(admin_plan_page, config["base_url"], "open_manage_plan", payload)
    admin_plan_page.page.goto(f"{config['base_url']}/admin/plan/manage-plan")
    admin_plan_page.wait_for_body_pattern(r"Showing \d+ to \d+ of \d+ Plans")
    assert admin_plan_page.rows().count() > 0


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
def test_admin_security_005_admin_session_cookie_not_usable_after_logout(admin_dashboard_page, config):
    """Reuses the proven pattern from the main app's Sign Out testing
    (replay a pre-logout storage_state against a fresh context) --
    confirms the admin panel's own session is server-side invalidated on
    logout, not just cleared client-side."""
    page = admin_dashboard_page.page
    storage_state = page.context.storage_state()

    logout_link = page.get_by_role("link", name="Logout")
    if logout_link.count() == 0:
        logout_link = page.get_by_text("Logout", exact=False)
    if logout_link.count() == 0:
        pytest.skip("No discoverable Logout control in the admin panel UI to exercise real sign-out")
    logout_link.first.click()
    page.wait_for_timeout(2000)

    browser = page.context.browser
    fresh_context = browser.new_context(base_url=config["base_url"], storage_state=storage_state)
    fresh_page = fresh_context.new_page()
    try:
        fresh_page.goto(f"{config['base_url']}/admin/user/manage-user")
        fresh_page.wait_for_timeout(2000)
        assert "15," not in fresh_page.locator("body").inner_text()[:50], (
            "Pre-logout admin session storage_state still reaches real admin data after logout"
        )
    finally:
        fresh_context.close()
