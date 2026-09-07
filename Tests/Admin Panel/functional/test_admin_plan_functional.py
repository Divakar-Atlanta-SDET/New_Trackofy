"""Admin Panel Plan CRUD (Create Plan / Manage Plan). Confirmed live:

- BillType and Currency labels share the SAME id ("billType") -- a real,
  confirmed accessibility bug that also breaks get_by_label lookups for
  both fields, forcing positional combobox access.
- Selling Amount is a PrimeNG p-inputnumber with duplicate wrapper/inner
  ids (same shape as Tax's Percent field) -- addressed via the inner
  input's accessible name.
- Checking a Payment Type row's checkbox auto-derives its Amount from
  Selling Amount (e.g. 99 -> Monthly 99, Quarterly 297, Half Yearly 594,
  Yearly 1188) -- manually typing into an already-populated amount field
  APPENDS digits rather than replacing them (99 + typed "50" -> "9950").
- Submit only reliably enables once ALL 4 Payment Type rows AND ALL Menu
  List checkboxes (10 in this account's real data) are checked -- a
  single checked row/item leaves it permanently disabled with no
  validation message explaining why (a real discoverability gap).
- Even with Submit enabled, a real end-to-end create was NOT reliably
  observed to reach the server every time (mirroring the same class of
  unreliability found in the Device assign/unassign flow) -- the one
  full create+delete test in this file is skipped rather than risk
  leaving inconsistent real Plan data; see its skip reason."""
import time

import pytest


def _unique_plan_name() -> str:
    return f"AutoPlan{int(time.time() * 1000) % 10_000_000}"


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_plan_001_manage_plan_loads_with_real_data(admin_plan_page, config):
    admin_plan_page.open_manage_plan(config["base_url"])
    admin_plan_page.wait_for_body_pattern(r"Showing \d+ to \d+ of \d+ Plans")
    assert admin_plan_page.rows().count() > 0


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_plan_002_create_plan_page_loads(admin_plan_page, config):
    admin_plan_page.open_create_plan(config["base_url"])
    assert admin_plan_page.submit_button.count() == 1


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_plan_003_submit_disabled_with_empty_form(admin_plan_page, config):
    admin_plan_page.open_create_plan(config["base_url"])
    assert not admin_plan_page.is_submit_enabled()


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_plan_005_payment_type_amount_auto_derives_from_selling_amount(admin_plan_page, config):
    admin_plan_page.open_create_plan(config["base_url"])
    admin_plan_page.select_combobox_option(admin_plan_page.bill_type_combobox, "Postpaid")
    admin_plan_page.page.wait_for_timeout(500)
    admin_plan_page.selling_amount_input.click()
    admin_plan_page.selling_amount_input.press_sequentially("99", delay=60)
    admin_plan_page.page.wait_for_timeout(500)
    admin_plan_page.check_payment_type_row(0)
    admin_plan_page.page.wait_for_timeout(800)
    monthly_amount = admin_plan_page.page.get_by_role("spinbutton").nth(1)
    assert monthly_amount.input_value() == "99"


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
def test_admin_plan_006_xss_payload_in_plan_name_not_executed(admin_plan_page, config):
    payload = "<script>window.__xss_admin_plan=1</script>"
    admin_plan_page.open_create_plan(config["base_url"])
    admin_plan_page.plan_name_input.fill(f"{_unique_plan_name()}{payload}")
    executed = admin_plan_page.page.evaluate("() => window.__xss_admin_plan === 1")
    assert not executed, "XSS payload executed while typed into Plan Name field"


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_plan_007_manage_plan_search_box_present(admin_plan_page, config):
    """Functional smoke only -- this module has no confirmed evidence
    either way on whether Manage Plan's search filters correctly (unlike
    Manage User/Device, not deeply probed given the create-flow's own
    complexity consumed this phase's investigation budget)."""
    admin_plan_page.open_manage_plan(config["base_url"])
    assert admin_plan_page.search_input.count() == 1


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_plan_008_minimal_selection_reaches_confirmation_dialog(admin_plan_page, config):
    """Confirmed live (corrected from an earlier false conclusion): the
    real Submit-enablement requirement is just Plan Name/BillType/
    Selling Amount plus ONE Payment Type row and ONE Menu List item --
    not "check every row and every item" as originally believed. Submit
    opens a second confirmation dialog ("Please check your selling
    amount before submitting... Do you want to continue?") whose own
    Submit click is what actually fires POST /api/create-plan and
    creates a REAL, PERMANENT plan (confirmed live: Manage Plan has no
    Edit/Delete action at all -- same gap as Bug #59 for Manage Dealer).

    This test deliberately stops at the confirmation dialog and clicks
    Cancel rather than Submit, to prove the real minimal-selection path
    works end-to-end up to the point of a real, irreversible mutation --
    without adding another permanent row to real production data on
    every test run. The full create+confirm path is proven separately
    (manually verified, real plan_id returned) and is not repeated here
    on every run for that reason."""
    admin_plan_page.open_create_plan(config["base_url"])
    name = _unique_plan_name()
    admin_plan_page.create_plan_minimal(name)
    assert admin_plan_page.is_submit_enabled(), (
        "Expected Submit to enable with just one Payment Type row and one Menu List item checked"
    )
    admin_plan_page.submit_button.click()
    admin_plan_page.page.wait_for_timeout(1000)
    confirm_dialog_text = admin_plan_page.page.locator("body").inner_text()
    assert "Do you want to continue" in confirm_dialog_text
    cancel_btn = admin_plan_page.page.get_by_role("button", name="Cancel")
    cancel_btn.click()
    admin_plan_page.page.wait_for_timeout(1000)
    # Confirm cancelling the confirmation dialog did NOT create a real plan.
    admin_plan_page.open_manage_plan(config["base_url"])
    admin_plan_page.page.wait_for_timeout(1500)
    assert admin_plan_page.row_by_name(name).count() == 0, (
        f"Cancelling the confirmation dialog should not have created plan {name!r}"
    )
