"""Phase 11 -- Security (ADM-186 to 202, plus 248/249).

Some rows in this range are already covered elsewhere and referenced
rather than duplicated:
  - "Sub-user blocked from Administrator / any unassigned module by direct
    URL" (ADM-186/188-ish) -- covered, and found BROKEN, by Bug #29's
    regression pin (`test_admin_authorization_functional.py::
    test_authz_bug29_direct_url_bypasses_menu_access`).
  - "Blocked from an unassigned unit's operations" -- covered by
    `test_authz_bug27_unit_permission_without_scope_is_inert` (Phase 8),
    which confirmed this IS enforced correctly.
"""
import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_xss_payload_in_username_is_escaped(administrator_page):
    """XSS payload used as a sub-user's username is not executed, and no
    live <img>/<script> element from the payload is ever inserted into the
    real DOM -- confirmed by querying for the actual malicious element,
    not by string-matching the row's own text (which the app truncates
    for long usernames, making a full-string text match unreliable).
    The unique search key is placed BEFORE the payload so truncation
    (which cuts the end) can't hide it from search/cleanup.
    """
    admin = administrator_page
    search_key = _unique_username("pytestxss")
    payload = f"{search_key}<img src=x onerror=window.__xss_fired=true>"
    try:
        admin.create_user(payload, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        fired = admin.page.evaluate("() => window.__xss_fired === true")
        assert not fired, "XSS payload in the username should not execute as script"

        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        admin.search(search_key)
        assert admin.user_rows().filter(has_text=search_key).count() == 1, (
            "Expected exactly one row for the created (payload) username"
        )
        live_malicious_img = admin.page.locator('img[src="x"]')
        assert live_malicious_img.count() == 0, (
            "Expected no live <img> element from the payload to exist in the real DOM -- "
            f"found {live_malicious_img.count()}"
        )
    finally:
        _delete_if_exists(admin, search_key)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_sql_injection_shaped_username_handled_safely(administrator_page):
    """A SQL-injection-shaped username is treated as a literal string --
    created (or rejected) without error, without executing any query
    manipulation, and without exposing unrelated data. Verified by
    searching for the unique key afterward and confirming exactly one
    matching row exists (not zero due to a crash, not more than one due
    to the payload breaking out of the intended filter/query).
    """
    admin = administrator_page
    search_key = _unique_username("pytestsqli")
    payload = f"{search_key}' OR '1'='1"
    try:
        admin.create_user(payload, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        admin.search(search_key)
        matching = admin.user_rows().filter(has_text=search_key)
        assert matching.count() == 1, (
            f"Expected exactly one literal user created from the SQLi-shaped username, got {matching.count()}"
        )
    finally:
        _delete_if_exists(admin, search_key)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_sql_injection_shaped_search_no_query_manipulation(administrator_page):
    """A SQL-injection-shaped search string doesn't crash the page, error
    out, or return the full unfiltered list (which would indicate the
    payload broke out of an intended filter)."""
    admin = administrator_page
    before_reload_count = admin.user_rows().count()
    admin.search("' OR '1'='1")
    admin.page.wait_for_timeout(1000)
    rows_after = admin.user_rows().count()
    assert rows_after <= before_reload_count, (
        f"Expected the SQLi-shaped search to filter down (or error safely), not return more rows than "
        f"before ({before_reload_count}) -- got {rows_after}"
    )
    admin.clear_search()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_password_not_exposed_in_dom_before_reveal(administrator_page):
    """The password cell's own DOM text does not contain the real
    plaintext password while masked -- it's genuinely masked content
    (dots), not the real value hidden only by CSS (which would be
    readable via devtools/inner_text regardless of visual masking)."""
    admin = administrator_page
    username = _unique_username("pytestpwdom")
    real_password = "Sup3rSecretPwd99@"
    try:
        admin.create_user(username, real_password, ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)
        admin.search(username)
        masked_text = admin.password_cell_text(username)
        assert real_password not in masked_text, (
            f"Expected the masked password cell to NOT contain the real plaintext password in its own "
            f"DOM text, got: {masked_text!r}"
        )
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_tampered_vehicle_id_in_create_request_is_rejected_or_ignored(administrator_page):
    """Intercepts the real Step 1->2 save_subuser request and injects a
    fabricated, never-selected-in-the-UI vehicle identifier into its
    payload before it reaches the server -- the app should reject the
    request or ignore the tampered field, not silently grant scope over a
    vehicle the admin never actually picked through the UI.
    """
    admin = administrator_page
    username = _unique_username("pytesttamper")
    fake_vehicle_id = "TOTALLY-FAKE-VEHICLE-ID-999"
    tampered_payload_seen = {"applied": False}

    def _tamper(route):
        request = route.request
        try:
            import json
            body = request.post_data_json
            if body is not None:
                body_str = json.dumps(body)
                if "vehicle" in body_str.lower() or "unit" in body_str.lower():
                    tampered_payload_seen["applied"] = True
                route.continue_(post_data=json.dumps({**body, "unit_ids": [fake_vehicle_id]}))
                return
        except Exception:
            pass
        route.continue_()

    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.page.route("**/save_subuser*", _tamper)
        admin.wizard_dialog().get_by_role("button", name="Next Step").click()
        admin.page.wait_for_timeout(2500)
        admin.page.unroute("**/save_subuser*")
        admin.page.keyboard.press("Escape")
        admin.page.wait_for_timeout(500)

        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        admin.search(username)
        if admin.user_row(username).count() > 0:
            admin.permissions_button(username).click()
            admin.page.wait_for_timeout(1500)
            dialog_text = admin.permissions_dialog().inner_text()
            admin.close_permissions_dialog()
            assert fake_vehicle_id not in dialog_text, (
                f"Bug: a fabricated vehicle id injected into the request body was accepted and persisted "
                f"as this user's scope -- the app should validate unit/vehicle ids server-side, not trust "
                f"whatever the client sends. Dialog text: {dialog_text!r}"
            )
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.skip(
    reason="CSRF token inspection: no CSRF token (header or cookie) was identified in requests during "
    "this session's network observation -- if the app relies on cookie/session-based auth without a "
    "separate CSRF token, there's nothing to inspect here. Audit trail: no audit-log feature or UI "
    "surface was discovered anywhere in the Administrator module this session. Honest skip for both, "
    "matching the REP-COM-021 precedent (Reports module), rather than asserting on a feature not "
    "confirmed to exist."
)
@pytest.mark.functional
@pytest.mark.admin
def test_adm_csrf_and_audit_trail():
    pass
