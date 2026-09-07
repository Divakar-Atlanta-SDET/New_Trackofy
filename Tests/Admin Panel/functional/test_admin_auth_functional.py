"""Admin Panel auth & RBAC boundary tests. Confirmed live: the admin
account (ADMIN_TEST_USERNAME/ADMIN_TEST_PASSWORD) logs in through the same
/  login form as the main app but routes to /admin/dashboard, a distinct
back-office SaaS-admin UI (PrimeNG-based), not /home."""
import pytest


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_001_login_routes_to_admin_dashboard(admin_dashboard_page):
    assert admin_dashboard_page.is_on_path("/admin/dashboard")


@pytest.mark.functional
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.negative
@pytest.mark.parametrize(
    "path",
    [
        "/admin/dashboard",
        "/admin/user/manage-user",
        "/admin/user/manage-dealer",
        "/admin/device/add-device",
        "/admin/device/unassign-device",
        "/admin/device/manage-device",
        "/admin/plan/create-plan",
        "/admin/plan/manage-plan",
        "/admin/tax",
    ],
)
def test_admin_002_unauthenticated_direct_url_access_denied(browser, config, path):
    """Opening an /admin/* URL directly, with no session, must not show
    real admin content -- it should redirect to login."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}{path}")
        page.wait_for_timeout(2000)
        assert page.get_by_role("heading", name="Sign in to you account").count() > 0 or "/admin" not in page.url, (
            f"Expected unauthenticated access to {path!r} to redirect to login, url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_003_nav_reaches_all_in_scope_pages(admin_dashboard_page, config):
    """Sanity check: each in-scope nav link actually navigates to its real
    destination path (confirmed live via a[href*='/admin/'] extraction)."""
    admin_dashboard_page.goto_manage_user()
    assert admin_dashboard_page.is_on_path("/admin/user/manage-user")

    admin_dashboard_page.open(config["base_url"])
    admin_dashboard_page.goto_manage_dealer()
    assert admin_dashboard_page.is_on_path("/admin/user/manage-dealer")
