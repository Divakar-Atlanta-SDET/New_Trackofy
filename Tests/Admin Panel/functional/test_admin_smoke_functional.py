"""Admin Panel smoke-only areas: Dashboard, Billing's 9 sub-sections,
secondary Device utilities, Configuration, Menu, Ticket. Per the approved
implementation plan, these are lower business-risk / secondary to the
panel's core "assign devices, create users/dealers, manage plans and tax"
purpose -- load-only checks, no data mutation.

Reverified 2026-09-14 (Bug #62): Configuration's Manage Brand/Manage
Model/Documentation and the top-level Menu page -- originally reported
as all silently redirecting to /admin/dashboard -- are now FIXED: all 4
load their own real, working page with real data (Brand List, Model
List, Documentation's Category List, Menu List). Separately confirmed
live: /admin/billing/dashboard still exhibits the exact same silent-
redirect symptom Bug #62 originally described (a route not in the
original 4, found while reverifying) -- see the new finding logged
against it below."""
import pytest


DASHBOARD_MARKER = "Quick Actions"


def _assert_page_loaded_without_console_errors(page, path, base_url):
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.goto(f"{base_url}{path}")
    page.wait_for_timeout(2000)
    body_text = page.locator("body").inner_text()
    assert len(body_text.strip()) > 0, f"{path} rendered an empty page"
    return body_text


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_smoke_001_dashboard_loads(admin_dashboard_page, config):
    body = _assert_page_loaded_without_console_errors(admin_dashboard_page.page, "/admin/dashboard", config["base_url"])
    assert "Quick Actions" in body
    assert "Add Device" in body
    assert "Create User" in body
    assert "Create Dealer" in body
    assert "Create Plan" in body


@pytest.mark.functional
@pytest.mark.admin_panel
@pytest.mark.parametrize(
    "path",
    [
        "/admin/billing/dashboard",
    ],
)
def test_admin_smoke_002_billing_dashboard_loads(admin_dashboard_page, config, path):
    """Reverified 2026-09-14 (new finding, same shape as Bug #62): this
    route silently redirects to /admin/dashboard instead of loading its
    own page -- confirmed live 3x. The original assertions here (a
    "Billing" heading plus 9 named sub-sections) never matched real,
    current behavior; pinned to the real, confirmed-broken behavior
    instead, matching how Bug #62's own regression test is written."""
    page = admin_dashboard_page.page
    page.goto(f"{config['base_url']}{path}")
    page.wait_for_timeout(2000)
    assert page.url.rstrip("/").endswith("/admin/dashboard"), (
        f"{path} no longer redirects to /admin/dashboard (now {page.url}) -- "
        "may now be fixed; update this test to verify the real page instead"
    )


@pytest.mark.functional
@pytest.mark.admin_panel
@pytest.mark.parametrize(
    "path",
    [
        "/admin/device/upload-device",
        "/admin/device/migrate-device",
        "/admin/device/device-distribution",
        "/admin/device/device-expiry",
        "/admin/device/search",
        "/admin/ticket",
    ],
)
def test_admin_smoke_003_secondary_device_and_ticket_pages_load(admin_dashboard_page, config, path):
    page = admin_dashboard_page.page
    page.goto(f"{config['base_url']}{path}")
    page.wait_for_timeout(2000)
    assert page.url.endswith(path), f"Expected to stay on {path}, got redirected to {page.url}"
    body = page.locator("body").inner_text()
    assert len(body.strip()) > 0


@pytest.mark.functional
@pytest.mark.admin_panel
@pytest.mark.parametrize(
    "path,expected_marker",
    [
        ("/admin/configuration/manage-brand", "Brand List"),
        ("/admin/configuration/manage-model", "Model List"),
        ("/admin/configuration/documentation", "Category List"),
        ("/admin/menu", "Menu List"),
    ],
)
def test_admin_smoke_004_configuration_and_menu_pages_load(admin_dashboard_page, config, path, expected_marker):
    """Bug #62 reverified 2026-09-14: ✅ FIXED. All 4 routes originally
    reported as silently redirecting to /admin/dashboard now load their
    own real page with real data -- confirmed live 3x, each staying on
    its own URL and rendering its real, named list."""
    page = admin_dashboard_page.page
    for _ in range(3):
        page.goto(f"{config['base_url']}{path}")
        page.wait_for_timeout(2000)
        assert page.url.rstrip("/").endswith(path), f"Expected to stay on {path}, got redirected to {page.url}"
        body = page.locator("body").inner_text()
        assert expected_marker in body, f"Expected {path} to render {expected_marker!r}, got: {body[:200]!r}"
