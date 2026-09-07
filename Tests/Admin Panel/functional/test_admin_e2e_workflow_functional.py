"""Admin Panel end-to-end workflow: exercises the panel transaction by
transaction, the way a real admin would actually use it in sequence --
create a Tax profile, drive Create Plan up to (but not through) its real
confirmation dialog, and create a User -- verifying each transaction's
result before moving to the next, then tearing down what can actually be
torn down in reverse order regardless of outcome.

Plan creation is deliberately NOT completed for real in this workflow:
confirmed live (see Bug_Report.md #61's correction) that Submit reliably
creates a real, PERMANENT plan (Manage Plan has no Edit/Delete action at
all, the same gap as Bug #59 for Manage Dealer) -- so Transaction 2 stops
at the real confirmation dialog ("Do you want to continue?") and clicks
Cancel, proving the flow works up to the point of a real, irreversible
mutation without adding another permanent row to production data on
every run.

Device assignment is deliberately NOT chained into this workflow:
Add Device's own dedicated end-to-end test
(test_admin_device_008_full_assign_and_unassign_cycle) is already
skipped due to a confirmed, real eventual-consistency issue in that
flow (Bug #60) -- chaining it here would only add the same known
unreliability to a longer, harder-to-debug test without proving
anything new."""
import time

import pytest


def _unique_suffix() -> str:
    return str(int(time.time() * 1000) % 10_000_000_000)


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_e2e_001_tax_then_plan_then_user_workflow(
    admin_tax_page, admin_plan_page, admin_user_page, config
):
    suffix = _unique_suffix()
    tax_name = f"AutoE2ETax{suffix[-6:]}"
    plan_name = f"AutoE2EPlan{suffix[-6:]}"
    user_email = f"autoe2euser{suffix}@example.com"
    user_mobile = "9" + suffix[-9:]

    created_tax = False
    created_user = False

    try:
        # Transaction 1: create a Tax profile.
        admin_tax_page.open(config["base_url"])
        admin_tax_page.create_tax(tax_name, "12")
        tax_row = admin_tax_page.row_by_name(tax_name)
        assert tax_row.count() == 1, f"Transaction 1 failed: tax {tax_name!r} did not appear"
        created_tax = True

        # Transaction 2: drive Create Plan to its real confirmation
        # dialog (proving the minimal-selection Submit path genuinely
        # works), then Cancel rather than completing a real, permanent
        # creation -- see module docstring.
        admin_plan_page.open_create_plan(config["base_url"])
        admin_plan_page.create_plan_minimal(plan_name)
        assert admin_plan_page.is_submit_enabled(), "Transaction 2 failed: Submit never enabled"
        admin_plan_page.submit_button.click()
        admin_plan_page.page.wait_for_timeout(1000)
        assert "Do you want to continue" in admin_plan_page.page.locator("body").inner_text(), (
            "Transaction 2 failed: expected the real confirmation dialog to appear"
        )
        admin_plan_page.page.get_by_role("button", name="Cancel").click()
        admin_plan_page.page.wait_for_timeout(1000)

        # Transaction 3: create a User (Service step assigns a real Plan
        # + Tax from this account's existing dropdown options -- doesn't
        # depend on Transaction 2 having created anything, it always
        # picks the first available real option).
        admin_user_page.open(config["base_url"], path="manage-user")
        admin_user_page.create_dummy_user("AutoE2E", user_email, user_mobile, "AutoE2E Test Co")
        last_page = admin_user_page.page.get_by_role("button", name="Last Page")
        if last_page.is_enabled():
            last_page.click()
            admin_user_page.page.wait_for_timeout(2000)
        user_row = admin_user_page.rows().filter(has_text=user_mobile)
        assert user_row.count() == 1, f"Transaction 3 failed: user (mobile {user_mobile}) did not appear"
        created_user = True
    finally:
        # Teardown in reverse order -- every transaction that actually
        # succeeded (and can be torn down at all) gets cleaned up.
        if created_user:
            last_page = admin_user_page.page.get_by_role("button", name="Last Page")
            if last_page.is_enabled():
                last_page.click()
                admin_user_page.page.wait_for_timeout(2000)
            row = admin_user_page.rows().filter(has_text=user_mobile)
            if row.count() > 0:
                admin_user_page.request_delete(row.first, reason="QA automation cleanup - E2E workflow test")

        # No Plan cleanup: Transaction 2 deliberately never creates a
        # real plan (see module docstring) -- nothing to tear down.

        if created_tax:
            admin_tax_page.open(config["base_url"])
            admin_tax_page.wait_for_table_loaded()
            admin_tax_page.page.wait_for_timeout(500)
            row = admin_tax_page.row_by_name(tax_name)
            if row.count() > 0:
                admin_tax_page.delete_icon(row).click()
                admin_tax_page.page.wait_for_timeout(500)
                admin_tax_page.confirm_delete()
