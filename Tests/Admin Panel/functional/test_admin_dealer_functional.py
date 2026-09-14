"""Admin Panel Manage Dealer. Confirmed live: same underlying page shape
and Create/Update wizard as Manage User (driven by the same
AdminUserPage, opened against /admin/user/manage-dealer), but with real,
confirmed differences:

- **No Delete action exists in the UI at all** -- confirmed on every
  dealer row (new and pre-existing real ones): only "Update dealer" and a
  disabled "White Labeling Details" icon are present, never a delete
  icon. A dealer this suite creates is therefore PERMANENT and cannot be
  removed -- cleanup is DISABLING it via the status toggle instead (per
  the user's explicit guidance), not deleting it. This suite creates
  exactly ONE dummy dealer for the whole file (module-scoped fixture),
  never per-test, to minimize how many permanent orphan records this
  leaves in real production data.
- The Create Dealer wizard is only 2 steps (Personal Information, then a
  combined Billing+Plan+Payment+Tax+Currency+Timezone step ending in a
  "Create Dealer" button), not User's 3 separate steps -- handled
  generically by AdminUserPage.create_dummy_user().
- Company Name/GST/PAN/City/PIN-code fields have NO `for` attribute at
  all for Dealer (get_by_label can't reach any of them, unlike User where
  Company Name at least has a real id) -- filled positionally.
- Confirmed live (Bug #58): a non-numeric filler value in a PIN-Code-
  shaped field triggers a raw SQL Server type-conversion error that leaks
  the DB host/port/database name -- this suite always uses a numeric-only
  filler for unlabeled textboxes.

See test_admin_user_functional.py's module docstring for the shared
quirks (non-functional search on this page family, cascading
Country->State)."""
import time

import pytest


def _unique_suffix() -> str:
    return str(int(time.time() * 1000) % 10_000_000_000)


def _find_row_by_mobile(admin_dealer_page, mobile: str, max_pages: int = 3):
    last_page = admin_dealer_page.page.get_by_role("button", name="Last Page")
    if last_page.is_enabled():
        last_page.click()
        admin_dealer_page.page.wait_for_timeout(2000)
    row = admin_dealer_page.rows().filter(has_text=mobile)
    tries = 0
    while row.count() == 0 and tries < max_pages:
        prev = admin_dealer_page.page.get_by_role("button", name="Previous Page")
        if not prev.is_enabled():
            break
        prev.click()
        admin_dealer_page.page.wait_for_timeout(1500)
        row = admin_dealer_page.rows().filter(has_text=mobile)
        tries += 1
    return row


@pytest.fixture(scope="module")
def dummy_dealer(browser, config, admin_credentials):
    """Creates exactly ONE real dummy dealer for this entire test file --
    Manage Dealer has no delete action, so every real dealer created here
    is permanent; module scope keeps that to a single record. Cleanup
    disables the dealer via its status toggle (the only real "undo"
    available), rather than attempting a delete that doesn't exist.

    Uses its own real login (module-scoped) rather than the function-
    scoped admin_authenticated_page fixture -- pytest doesn't allow a
    module-scoped fixture to depend on a function-scoped one."""
    import re

    from Pages.login_page import LoginPage
    from Pages.admin_user_page import AdminUserPage

    context = browser.new_context(base_url=config["base_url"])
    page = context.new_page()
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(admin_credentials["username"], admin_credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/admin/dashboard/?$"), timeout=15000)

    admin_dealer_page = AdminUserPage(page)
    admin_dealer_page.open(config["base_url"], path="manage-dealer")
    suffix = _unique_suffix()
    email = f"autoqadealer{suffix}@example.com"
    mobile = "8" + suffix[-9:]
    admin_dealer_page.create_dummy_user("AutoQA", email, mobile, "AutoQA Dealer Co")
    yield {"page": admin_dealer_page, "email": email, "mobile": mobile, "first_name": "AutoQA"}
    row = _find_row_by_mobile(admin_dealer_page, mobile)
    if row.count() > 0 and admin_dealer_page.is_status_active(row):
        admin_dealer_page.status_toggle(row).click()
        admin_dealer_page.page.wait_for_timeout(1200)
    context.close()


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_dealer_001_page_loads_with_real_data(admin_dealer_page):
    admin_dealer_page.wait_for_body_pattern(r"Showing \d+ to \d+ of \d+ dealers")
    assert int(admin_dealer_page.showing_count_text()) > 50


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_dealer_002_create_dummy_dealer_appears_in_list(dummy_dealer):
    page = dummy_dealer["page"]
    row = _find_row_by_mobile(page, dummy_dealer["mobile"])
    assert row.count() == 1, f"Expected the newly created dummy dealer (mobile {dummy_dealer['mobile']}) to appear"
    assert dummy_dealer["email"] in row.inner_text()


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_dealer_003_no_delete_action_present(dummy_dealer):
    """Regression pin: confirms the real, confirmed absence of a Delete
    action on Manage Dealer rows -- if a future release adds one, this
    test should start failing and be updated to use it for real cleanup."""
    page = dummy_dealer["page"]
    row = _find_row_by_mobile(page, dummy_dealer["mobile"])
    assert row.count() == 1
    delete_icon = row.locator('i[ptooltip="Delete dealer"]')
    assert delete_icon.count() == 0, "A Delete action now exists on Manage Dealer -- update cleanup to use it"


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_dealer_004_edit_dialog_opens_prefilled(dummy_dealer):
    page = dummy_dealer["page"]
    row = _find_row_by_mobile(page, dummy_dealer["mobile"])
    assert row.count() == 1
    page.open_edit(row)
    assert page.first_name_input().input_value() == dummy_dealer["first_name"]
    assert page.email_input().input_value() == dummy_dealer["email"]
    page.close_wizard_dialog()


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_dealer_005_create_wizard_requires_mandatory_fields(admin_dealer_page):
    admin_dealer_page.open_create()
    assert not admin_dealer_page.wizard_next_button().is_enabled()
    admin_dealer_page.close_wizard_dialog()


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
def test_admin_dealer_006_xss_payload_in_first_name_not_executed(admin_dealer_page):
    """Uses the create FORM only (never submits) -- no new permanent
    dealer record for a payload-injection check."""
    payload = "<script>window.__xss_admin_dealer=1</script>"
    admin_dealer_page.open_create()
    admin_dealer_page.fill_personal_info(f"AutoQA{payload}", "autoqaxssdealer@example.com", "7000000099")
    executed = admin_dealer_page.page.evaluate("() => window.__xss_admin_dealer === 1")
    assert not executed, "XSS payload executed while typed into dealer First Name field"
    admin_dealer_page.close_wizard_dialog()


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_dealer_007_status_toggle_reversible(dummy_dealer):
    """The status toggle is exercised for real once here (flip and flip
    back) -- separate from the module fixture's own final disable, which
    happens at file teardown regardless of this test's outcome."""
    page = dummy_dealer["page"]
    row = _find_row_by_mobile(page, dummy_dealer["mobile"])
    assert row.count() == 1
    original = page.is_status_active(row)
    page.status_toggle(row).click()
    page.page.wait_for_timeout(1200)
    row = _find_row_by_mobile(page, dummy_dealer["mobile"])
    assert page.is_status_active(row) != original
    page.status_toggle(row).click()
    page.page.wait_for_timeout(1200)


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_dealer_008_bug82_invalid_pin_code_silently_does_nothing_on_submit(admin_dealer_page):
    """Bug_Report.md #82. Reverified live 2026-09-14: with every other
    field validly filled, an invalid (non-numeric) PIN Code no longer
    triggers the originally-reported raw SQL error (Bug #58) -- but
    Submit, which still reports as enabled, fires zero network requests
    and shows zero visible feedback when clicked. Uses the create FORM
    only -- since the whole point of this bug is that nothing gets
    submitted, no new permanent dealer record is created here."""
    import re

    admin_dealer_page.open_create()
    admin_dealer_page.fill_personal_info("Bug82Regression", "bug82regression@example.com", "7000000082")
    admin_dealer_page.wizard_next_button().click()
    admin_dealer_page.page.wait_for_timeout(1000)
    admin_dealer_page.fill_billing_info_minimal("Bug82RegressionCo")

    dialog = admin_dealer_page.wizard_dialog()
    all_textboxes = dialog.get_by_role("textbox")
    for i in range(all_textboxes.count()):
        box = all_textboxes.nth(i)
        placeholder = box.get_attribute("placeholder") or ""
        if "PIN Code" in placeholder:
            box.fill("AutoQA123")
            break

    submit_btn = dialog.get_by_role("button", name=re.compile("Create Dealer", re.IGNORECASE))
    assert submit_btn.is_enabled(), "Expected Submit to (still) report as enabled with an invalid PIN Code"

    create_dealer_calls = []
    admin_dealer_page.page.on(
        "response",
        lambda resp: create_dealer_calls.append(resp.url) if "create-dealer" in resp.url.lower() else None,
    )
    submit_btn.click()
    admin_dealer_page.page.wait_for_timeout(2500)

    assert not create_dealer_calls, (
        f"Bug regression: expected an invalid PIN Code to (still) fire no create-dealer request at all -- "
        f"if one now fired, the server-side validation/error handling may have changed. Got: {create_dealer_calls}"
    )
    assert dialog.is_visible(), "Expected the dialog to (still) stay open with no visible change on this silent failure"
    admin_dealer_page.close_wizard_dialog()
