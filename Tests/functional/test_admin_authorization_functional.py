"""Phase 8 -- Effective authorization deep-dive.

Per the design doc's own stated thesis, a permission checkbox saving
successfully is not the same as the resulting sub-user actually being
granted (or denied) exactly that access. Every test here creates a real
sub-user, logs in as them in a genuinely fresh browser context (not the
admin's own session), and asserts on the real, observable effect --
not on the wizard's own state.

Covers ADM-043/044 (Arm/Disarm -- honest skip, see below), ADM-068/069
(menu access + direct URL), the "Enforce X permission" rows (via Driver
as a representative, fully-verified example), ADM-146-149 (unit scope vs
unit permission), and doubles as the live verification promised in
Bug_Report.md #27 and #29.
"""
import time

import pytest

from Pages.driver_page import DriverPage
from Pages.home_page import HomePage
from Pages.login_page import LoginPage


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


def _login_fresh(browser, config, username: str, password: str):
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    login = LoginPage(page, config)
    login.open()
    login.login(username, password)
    page.wait_for_timeout(2000)
    return ctx, page


@pytest.mark.functional
@pytest.mark.admin
def test_authz_menu_access_matches_granted_group(administrator_page, browser, config):
    """ADM-068: A sub-user's visible top-nav modules match their assigned
    menu group -- "Full control" shows every module, "example21" (which
    the design doc / Phase 4 tests confirm grants only 'Home') shows a
    strictly smaller set with Settings/Administrator/Unit/Reports/Video
    Telematics absent."""
    admin = administrator_page
    full_user = _unique_username("pytestauthzfull")
    limited_user = _unique_username("pytestauthzlim")
    password = "ValidPassword123@"
    try:
        admin.create_user(full_user, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control")
        admin.page.wait_for_timeout(1500)
        admin.create_user(limited_user, password, ["HP12G9691"], arm_disarm="No", menu_group="example21")
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, full_user, password)
        try:
            full_nav = page.locator("body").inner_text()
        finally:
            ctx.close()

        ctx2, page2 = _login_fresh(browser, config, limited_user, password)
        try:
            limited_nav = page2.locator("body").inner_text()
        finally:
            ctx2.close()

        for module in ["Settings", "Administrator", "Reports", "Video Telematics"]:
            assert module in full_nav, f"Expected '{module}' visible for the Full control user"
            assert module not in limited_nav, (
                f"Expected '{module}' NOT visible for the example21 (Home-only) user, but it was"
            )
    finally:
        _delete_if_exists(admin, full_user)
        _delete_if_exists(admin, limited_user)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_authz_bug29_direct_url_bypasses_menu_access(administrator_page, browser, config):
    """Regression pin for Bug #29 (Bug_Report.md, Administrator Module):
    a sub-user whose menu group never includes Administrator can still
    reach /administrator directly by URL and load a real, functional page
    (not blocked/redirected). This asserts the confirmed-broken behavior;
    it should start failing -- and be flipped to assert a redirect/access-
    denied state -- once route-level enforcement is added.
    """
    admin = administrator_page
    username = _unique_username("pytestauthzbug29")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No", menu_group="example21")
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, username, password)
        try:
            nav_text = page.locator("body").inner_text()
            assert "Administrator" not in nav_text, "Expected Administrator absent from nav for this menu group"

            page.goto(f"{config['base_url']}/administrator")
            page.wait_for_timeout(2000)
            body_text = page.locator("body").inner_text()
            assert "/administrator" in page.url and "User Management" in body_text, (
                "Bug #29: direct navigation to /administrator should currently (still) succeed and render "
                "the real User Management page shell despite Administrator not being in this user's menu "
                f"group. If it's now blocked/redirected, the app has been fixed. Got url={page.url!r}, "
                f"body snippet={body_text[:200]!r}"
            )
        finally:
            ctx.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_authz_general_permission_create_driver_enforced(administrator_page, browser, config):
    """Enforce 'Create Driver' (General Permission, Driver category): with
    the SAME menu group (Full control, so Settings is in nav either way),
    a user with Driver granted sees a real, enabled 'Add Driver' button on
    /settings/driver; a user without it (default denied) does not see the
    button at all. Isolates General Permission's own effect from Menu
    Access by holding the menu group constant."""
    admin = administrator_page
    granted_user = _unique_username("pytestdrvg")
    denied_user = _unique_username("pytestdrvd")
    password = "ValidPassword123@"
    try:
        admin.create_user(
            granted_user, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control",
            toggle_general_permissions=["Driver"],
        )
        admin.page.wait_for_timeout(1500)
        admin.create_user(
            denied_user, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control",
        )
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, granted_user, password)
        try:
            page.goto(f"{config['base_url']}/settings/driver")
            page.wait_for_timeout(2000)
            driver_page = DriverPage(page)
            assert driver_page.add_btn.count() > 0 and driver_page.add_btn.is_visible(), (
                "Expected 'Add Driver' visible when Driver permission is granted"
            )
        finally:
            ctx.close()

        ctx2, page2 = _login_fresh(browser, config, denied_user, password)
        try:
            page2.goto(f"{config['base_url']}/settings/driver")
            page2.wait_for_timeout(2000)
            driver_page2 = DriverPage(page2)
            assert driver_page2.add_btn.count() == 0, (
                "Expected 'Add Driver' absent when Driver permission is denied (default), but it was present"
            )
        finally:
            ctx2.close()
    finally:
        _delete_if_exists(admin, granted_user)
        _delete_if_exists(admin, denied_user)


@pytest.mark.functional
@pytest.mark.admin
def test_authz_unit_scope_limits_visible_fleet(administrator_page, browser, config):
    """ADM critical security scenario (design doc section 13): a sub-user
    assigned only Vehicle A in Step 1 must not see Vehicle B anywhere,
    merely because Vehicle B exists in the administrator's account. Uses
    the Home fleet list as the observable surface."""
    admin = administrator_page
    username = _unique_username("pytestscope")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control")
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, username, password)
        try:
            home = HomePage(page)
            page.wait_for_timeout(1500)
            visible_ids = home.visible_vehicle_ids()
            assert visible_ids == ["HP12G9691"], (
                f"Expected the fleet list scoped to exactly the assigned vehicle ['HP12G9691'], got {visible_ids}"
            )
        finally:
            ctx.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_authz_bug27_unit_permission_without_scope_is_inert(administrator_page, browser, config):
    """Resolves the open question in Bug #27 (Bug_Report.md, Administrator
    Module): a sub-user is scoped to Vehicle A only in Step 1 (Unit Scope),
    but is given a Step 4 Unit Permission (Manage Services) for a SECOND
    vehicle that was never assigned in Step 1. Per the design doc's own
    model, this configuration should be inert -- the un-scoped vehicle
    must not become visible/accessible just because it has a Step 4
    permission on file.
    """
    admin = administrator_page
    username = _unique_username("pytestscopeperm")
    password = "ValidPassword123@"
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, password, ["HP12G9691"], "No")  # scope: HP12G9691 ONLY
        admin.click_next_step()
        admin.select_menu_group("Full control")
        admin.click_next_step()
        admin.click_next_step()
        admin.page.wait_for_timeout(1000)

        # Step 4: grant a Unit Permission for a DIFFERENT, unscoped vehicle
        admin.open_units_dropdown()
        options = admin.page.get_by_role("option")
        second_vehicle_id = None
        for i in range(options.count()):
            text = options.nth(i).inner_text()
            if text != "HP12G9691":
                second_vehicle_id = text
                break
        assert second_vehicle_id, "Expected at least one other vehicle in the account to use as the unscoped one"
        admin.select_unit(second_vehicle_id)
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()
        admin.expand_permission_category("Unit")
        admin.unit_permission_checkbox("Manage Services").click()
        admin.page.wait_for_timeout(400)
        admin.click_submit()
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, username, password)
        try:
            home = HomePage(page)
            page.wait_for_timeout(1500)
            visible_ids = home.visible_vehicle_ids()
            assert second_vehicle_id not in visible_ids, (
                f"Vehicle '{second_vehicle_id}' has a Step 4 Unit Permission but was never assigned in "
                f"Step 1 scope -- it must not be visible/accessible. Visible fleet: {visible_ids}"
            )
            assert visible_ids == ["HP12G9691"], (
                f"Expected only the Step-1-scoped vehicle visible, got {visible_ids}"
            )
        finally:
            ctx.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.skip(
    reason="Arm/Disarm's actual command control was not locatable in this pass -- checked the vehicle "
    "card's overflow ('more_vert') menu on Home (opened but produced no visible menu items in a "
    "fresh sub-user session) and the Home page body text (no Arm/Disarm control text found anywhere). "
    "It's likely inside a vehicle detail panel or Unit-module surface not yet explored/built as a Page "
    "Object in this suite. Honest skip rather than a guess; revisit with dedicated exploration."
)
@pytest.mark.functional
@pytest.mark.admin
def test_authz_arm_disarm_control_presence():
    pass
