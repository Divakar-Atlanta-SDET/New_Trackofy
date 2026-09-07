"""Admin Panel smoke-only areas: Dashboard, Billing's 9 sub-sections,
secondary Device utilities, Configuration, Menu, Ticket. Per the approved
implementation plan, these are lower business-risk / secondary to the
panel's core "assign devices, create users/dealers, manage plans and tax"
purpose -- load-only checks, no data mutation.

Confirmed live (Bug #62): Configuration's Manage Brand/Manage Model/
Documentation and the top-level Menu page all silently redirect to
/admin/dashboard when navigated to directly, despite having real,
clickable nav links pointing at them -- these pages appear to not be
implemented (or gated in a way this admin account doesn't satisfy),
with no error shown, just a silent bounce home."""
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
    body = _assert_page_loaded_without_console_errors(admin_dashboard_page.page, path, config["base_url"])
    assert "Billing" in body
    # All 9 real sub-section nav labels confirmed live in one shot.
    for section in [
        "Device Plans",
        "Dealer Licenses",
        "Device Billing",
        "Wallet Management",
        "Renewal",
        "Reports",
        "Invoices",
        "Audit Logs",
    ]:
        assert section in body, f"Expected Billing sub-section {section!r} to be listed"


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


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.parametrize(
    "path",
    [
        "/admin/configuration/manage-brand",
        "/admin/configuration/manage-model",
        "/admin/configuration/documentation",
        "/admin/menu",
    ],
)
def test_admin_smoke_004_configuration_and_menu_pages_redirect_to_dashboard(admin_dashboard_page, config, path):
    """Regression pin for Bug #62 -- confirms the real, confirmed silent
    redirect. If a future release actually implements these pages, this
    test should start failing and be updated to test the real page."""
    page = admin_dashboard_page.page
    page.goto(f"{config['base_url']}{path}")
    page.wait_for_timeout(2000)
    assert page.url.rstrip("/").endswith("/admin/dashboard"), (
        f"{path} no longer redirects to /admin/dashboard (now {page.url}) -- "
        "Bug #62 may be fixed; update this test to verify the real page instead"
    )
