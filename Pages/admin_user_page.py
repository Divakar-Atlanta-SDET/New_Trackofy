import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from Pages.base_page import BasePage


class AdminUserPage(BasePage):
    """Manage User (/admin/user/manage-user) and Manage Dealer
    (/admin/user/manage-dealer) -- near-identical table shape, both driven
    by this one page object (pass path="manage-user" or "manage-dealer").

    Confirmed live, a REAL structural difference between the two: Manage
    User rows have a real Delete action (request-based, see
    request_delete() below); Manage Dealer rows have NO delete action at
    all, ever (confirmed on new and pre-existing real dealers alike) --
    a dealer created through this page is permanent, and the only
    available "undo" is disabling it via status_toggle()."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: this control's real accessible role is "textbox",
        # not "searchbox" (get_by_role("searchbox") matches 0) -- its only
        # identifying attribute is a placeholder (with a leading double
        # space, "  Search"), so get_by_placeholder is the closest
        # role/label-based locator available; not a raw CSS selector.
        self.search_input = page.get_by_placeholder("Search")

    def open(self, base_url: str, path: str = "manage-user"):
        self.page.goto(f"{base_url}/admin/user/{path}")
        self.expect_path(f"/admin/user/{path}")

    def search(self, query: str):
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def clear_search(self):
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    def row_by_name(self, name: str) -> Locator:
        return self.rows().filter(has_text=name).first

    def showing_count_text(self) -> str:
        match = re.search(r"Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)", self.visible_text())
        return match.group(1) if match else ""

    # ------------------------------------------------------------- row actions
    # Confirmed live: these row-action icons are bare <i ptooltip="..."> with
    # no aria-label/role -- get_by_role can't reach them (logged as a
    # candidate accessibility bug). The ptooltip attribute is the only
    # reliable identifier, so this is a documented, unavoidable CSS-selector
    # exception to the get_by_role/label/text-first convention.
    def edit_icon(self, row: Locator) -> Locator:
        return row.locator('i[ptooltip="Update user"], i[ptooltip="Update dealer"]')

    def delete_icon(self, row: Locator) -> Locator:
        return row.locator('i[ptooltip="Delete user"], i[ptooltip="Delete dealer"]')

    def view_subusers_icon(self, row: Locator) -> Locator:
        return row.locator('i[ptooltip="View Subusers"]')

    def status_toggle(self, row: Locator) -> Locator:
        return row.get_by_role("switch")

    def is_status_active(self, row: Locator) -> bool:
        return self.status_toggle(row).get_attribute("aria-checked") == "true"

    # ------------------------------------------------------------- create/edit wizard dialog
    # Confirmed live: Create ("+User"/"+Dealer" button, class ".user-btn--
    # primary" -- shared across both User and Dealer, containing a
    # .pi-plus icon; get_by_role couldn't reach it, so this is a
    # documented CSS exception) and Update (row edit icon) both open the
    # SAME 3-step wizard (Personal Information / Billing Information /
    # Service), just pre-filled in the Update case -- one set of field
    # locators, scoped to whichever dialog is currently open, serves both.
    def wizard_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container, .p-dialog").filter(has_text="Personal Information")

    def open_create(self):
        # Confirmed live: this click occasionally doesn't register on the
        # first attempt right after the table finishes its own async load
        # (same "occasionally stalls, reason not fully isolated" shape as
        # administrator_page.py's toggle_password_visibility) -- one retry
        # after a fixed wait reliably recovers it.
        self.page.wait_for_timeout(1000)
        self.page.locator("button:has(.pi-plus)").first.click()
        try:
            self.wait_for_visible(self.wizard_dialog().first, timeout=8000)
            return
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(1000)
        self.page.locator("button:has(.pi-plus)").first.click()
        self.wait_for_visible(self.wizard_dialog().first)

    def open_edit(self, row: Locator):
        self.edit_icon(row).click()
        self.wait_for_visible(self.wizard_dialog().first)

    # Alias kept for the pre-existing name used elsewhere in this file.
    edit_dialog = wizard_dialog

    def first_name_input(self) -> Locator:
        # Confirmed live: label text is literally "First Name *" (asterisk
        # baked into the label, not a separate required-marker element) --
        # get_by_label matches on substring by default so "First Name" works,
        # but exact=True would fail against the real DOM.
        return self.wizard_dialog().get_by_label("First Name", exact=False)

    def last_name_input(self) -> Locator:
        return self.wizard_dialog().get_by_label("Last Name", exact=False)

    def email_input(self) -> Locator:
        return self.wizard_dialog().get_by_label("Email", exact=False)

    def mobile_input(self) -> Locator:
        return self.wizard_dialog().get_by_label("Mobile", exact=False)

    def whatsapp_radio(self, value: str) -> Locator:
        # value: "Yes" or "No"
        return self.wizard_dialog().get_by_role("radio", name=value, exact=True)

    def wizard_next_button(self) -> Locator:
        return self.wizard_dialog().get_by_role("button", name="Next")

    # Kept for backward compatibility with the earlier method name.
    edit_next_button = wizard_next_button

    def edit_save_button(self) -> Locator:
        return self.wizard_dialog().get_by_role("button", name=re.compile("Save|Submit|Update"))

    def close_wizard_dialog(self):
        # Confirmed live: Escape alone occasionally leaves the dialog's
        # backdrop mask (.p-dialog-mask) in the DOM even after the dialog
        # itself visually closes, which then silently intercepts clicks on
        # whatever is tested next (a real, confirmed failure mode -- a
        # later test's delete-icon click timed out fighting this mask).
        # Explicitly wait for the mask to clear, and fall back to clicking
        # a close/cancel control if Escape didn't work at all.
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)
        mask = self.page.locator(".p-dialog-mask")
        if mask.count() > 0 and self.wizard_dialog().count() > 0:
            cancel = self.wizard_dialog().get_by_role("button", name="Cancel", exact=False)
            close = self.wizard_dialog().locator("button").filter(has_text="close")
            if cancel.count() > 0:
                cancel.first.click()
            elif close.count() > 0:
                close.first.click()
            self.page.wait_for_timeout(500)
        try:
            mask.first.wait_for(state="hidden", timeout=5000)
        except PlaywrightTimeoutError:
            pass

    # Kept for backward compatibility with the earlier method name.
    close_edit_dialog = close_wizard_dialog

    def fill_personal_info(self, first_name: str, email: str, mobile: str, last_name: str = ""):
        self.first_name_input().fill(first_name)
        if last_name:
            self.last_name_input().fill(last_name)
        self.email_input().fill(email)
        self.mobile_input().fill(mobile)

    def _select_first_option_in_each_combobox(self, dialog: Locator, max_retry_rounds: int = 2):
        """Selects the first available option in every combobox on the
        currently-visible wizard step, left to right. Confirmed live:
        Country->State is a genuine cascading pair -- State renders
        `aria-disabled="true"` until Country resolves, so a disabled
        combobox is skipped (not clicked, which would just time out) and
        the whole pass is retried up to `max_retry_rounds` times to let
        any cascade catch up."""
        for _ in range(max_retry_rounds):
            comboboxes = dialog.get_by_role("combobox")
            any_still_disabled = False
            for i in range(comboboxes.count()):
                combo = comboboxes.nth(i)
                if combo.get_attribute("aria-disabled") == "true":
                    any_still_disabled = True
                    continue
                if (combo.get_attribute("data-p") or "").find("empty") == -1:
                    continue  # already has a value selected
                combo.click()
                self.page.wait_for_timeout(400)
                options = self.page.get_by_role("option")
                if options.count() > 0:
                    options.first.click()
                else:
                    self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
            if not any_still_disabled:
                break
            self.page.wait_for_timeout(600)

    def fill_billing_info_minimal(self, company_name: str = "AutoQA Test Company"):
        """Fills only the required fields on the Billing Information step
        with safe placeholder values, picking the first available option
        for every dropdown -- this module has no CSV/design doc to define
        "correct" business values, and the point of this suite's dummy
        user/dealer is to exercise the create->assign->delete flow, not to
        validate every billing-field business rule.

        Confirmed live field layout: Company Name*/GST/PAN (labeled
        textboxes with real ids) + Currency*/Timezone*/Country*/State*
        (labeled comboboxes) all resolve via get_by_label. Address*/City*/
        PIN Code and their Billing-Address equivalents render with NO
        `for` attribute at all (get_by_label can't reach them) -- those 6
        are addressed positionally via get_by_role("textbox"), in the same
        DOM/tab order the label list confirmed live: Address, City, PIN
        Code, Billing Address, City, PIN Code."""
        dialog = self.wizard_dialog()
        # Confirmed live: on Manage User's wizard, Company Name has a real
        # `for="companyName"` and get_by_label reaches it; on Manage
        # Dealer's wizard the SAME-LOOKING label has no `for` at all --
        # it's just the FIRST of the unlabeled textboxes in DOM order.
        # Filling it separately via .first and then re-collecting
        # "unlabeled textboxes" for the address fields double-counts it
        # (a real bug hit live: the address-fill loop clobbered Company
        # Name right back over with "123 Test Street") -- so on the
        # Dealer path, Company Name is folded into the SAME positional
        # values list below instead of being filled independently.
        company_name_input = dialog.get_by_label("Company Name", exact=False)
        if company_name_input.count() > 0:
            company_name_input.fill(company_name)
        else:
            dialog.get_by_role("textbox").first.fill(company_name)

        # Confirmed live: Country->State is a real cascading pair (State
        # stays disabled until Country resolves) -- selecting comboboxes
        # strictly left-to-right with a short wait after each is required,
        # and a disabled combobox (still resolving its cascade) is skipped
        # and retried once at the end rather than failed immediately.
        self._select_first_option_in_each_combobox(dialog)

        # Confirmed live: the exact set/order of unlabeled textboxes
        # differs between User (6: Address/City/PIN/BillingAddress/City/
        # PIN) and Dealer (9: the same 6 PLUS GST/PAN, which are also
        # unlabeled for Dealer specifically) -- position-mapping a fixed
        # values list to them broke live (the real, required trailing
        # billing PIN Code ended up unfilled because GST/PAN silently
        # consumed two of the mapped slots). Filling every still-empty
        # unlabeled textbox with one generic safe value sidesteps needing
        # to know the exact field count/order at all -- none of these
        # fields need semantically "correct" data for this suite's
        # purpose (exercising create->assign->delete), just a non-empty
        # value to satisfy required-field validation.
        # Confirmed live (Bug #58): a purely alphanumeric filler value
        # here (e.g. "AutoQA123") reaches a PIN Code field the backend
        # expects as an integer and triggers a raw SQL Server conversion
        # error, leaking the DB host/port/database name in the API
        # response. A numeric-only string is safe for both PIN-code-shaped
        # fields (their real use) and free-text ones (Address/City/GST/
        # PAN accept digits fine).
        all_textboxes = dialog.get_by_role("textbox")
        for i in range(all_textboxes.count()):
            box = all_textboxes.nth(i)
            if not box.get_attribute("id") and not box.input_value():
                box.fill("100001")

        sales_name = dialog.get_by_label("Sales Person Name", exact=False)
        if sales_name.count() > 0:
            sales_name.fill("AutoQA Sales Contact")
        sales_contact = dialog.get_by_label("Sales Person Contact", exact=False)
        if sales_contact.count() > 0:
            sales_contact.fill("9876543211")

    def fill_service_info_minimal(self, arm_disarm: str = "No"):
        """Confirmed live: Step 3 ("Service") requires Plan*, Payment
        Type*, and Tax* (all comboboxes, first-available-option picked --
        this is the real "assign a plan" step the admin panel's Create
        User flow is built around) plus an Arm/Disarm Yes/No radio."""
        dialog = self.wizard_dialog()
        for combobox_index in range(dialog.get_by_role("combobox").count()):
            combo = dialog.get_by_role("combobox").nth(combobox_index)
            combo.click()
            self.page.wait_for_timeout(400)
            options = self.page.get_by_role("option")
            if options.count() > 0:
                options.first.click()
            else:
                self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        radio = dialog.get_by_role("radio", name=arm_disarm, exact=True)
        if radio.count() > 0:
            radio.click()

    def create_dummy_user(self, first_name: str, email: str, mobile: str, company_name: str):
        """Drives the Create User/Dealer wizard with the minimum required
        data (first available Plan/Payment Type/Tax) to reach a real,
        submitted record -- exercises this panel's actual "assign a plan"
        flow, not just a stub with fields left empty.

        Confirmed live: Manage User's wizard has 3 distinct steps
        (Personal/Billing/Service, Plan+Tax on their own step); Manage
        Dealer's wizard folds Plan/Payment Type/Tax/Currency/Timezone
        directly INTO the Billing step (only 2 steps total) -- this
        method detects which shape it's looking at after Billing rather
        than assuming a fixed step count."""
        self.open_create()
        self.fill_personal_info(first_name, email, mobile)
        self.wizard_next_button().click()
        self.page.wait_for_timeout(1000)
        self.fill_billing_info_minimal(company_name)
        # fill_billing_info_minimal already picks the first option in
        # EVERY combobox visible on this step -- if Plan/Payment/Tax are
        # folded in here (Dealer), that already selected them. This step's
        # advance button is "Next" for the 3-step User wizard, but
        # directly "Create Dealer" for the 2-step Dealer wizard -- look
        # for either rather than assuming "Next" exists.
        submit_pattern = re.compile("Submit|Save|Create", re.IGNORECASE)
        # This step's advance button is "Next" for the 3-step User wizard
        # (Billing->Service), but directly "Create Dealer" for the
        # 2-step Dealer wizard (Billing IS the last step). Confirmed live:
        # inferring which one happened by re-checking whether the dialog
        # is "still open" afterward is racy -- this app's post-submit
        # loading overlay (a raw `bg-white/65` full-screen div, not one of
        # BasePage.wait_for_loading_to_finish()'s known spinner selectors)
        # can leave a stale dialog reference reporting count()>0 for a
        # moment even after a REAL submit, which then wrongly re-entered
        # this branch and submitted a SECOND dealer. Read the button's
        # own label BEFORE clicking instead -- it's the only place this
        # is unambiguous.
        advance = self.wizard_dialog().get_by_role("button", name=re.compile("Next|" + submit_pattern.pattern, re.IGNORECASE))
        was_real_submit = bool(re.search(submit_pattern, advance.inner_text()))
        advance.click()
        self.page.locator(".bg-white\\/65").first.wait_for(state="hidden", timeout=10000)
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)
        if not was_real_submit:
            # Really was "Next" into a Service step (3-step User shape).
            self.fill_service_info_minimal()
            self.wizard_dialog().get_by_role("button", name=submit_pattern).click()
            self.page.locator(".bg-white\\/65").first.wait_for(state="hidden", timeout=10000)
            self.wait_for_loading_to_finish()
            self.page.wait_for_timeout(1500)

    # ------------------------------------------------------------- delete (request-based, async)
    # Confirmed live: unlike Tax's p-confirmpopup, Manage User/Dealer's
    # delete flow opens a real modal dialog ("Delete User"/"Delete
    # Dealer") requiring a mandatory Reason textbox, and submitting it
    # only queues a deletion REQUEST -- the row stays visible and the
    # total user count doesn't drop immediately. A second delete attempt
    # on the same row returns "Deletion request already exists for this
    # user" rather than deleting again or erroring. Tests must assert the
    # request was accepted, never that the row disappears.
    def delete_confirm_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container, .p-dialog").filter(
            has_text=re.compile(r"^Delete (User|Dealer)")
        )

    def request_delete(self, row: Locator, reason: str = "QA automation cleanup"):
        """Opens the delete dialog for `row`, fills the required Reason,
        and submits -- this only queues a deletion request (see class
        docstring above), it does not remove the row immediately."""
        self.delete_icon(row).click()
        self.wait_for_visible(self.delete_confirm_dialog().first)
        dialog = self.delete_confirm_dialog()
        dialog.get_by_role("textbox").first.fill(reason)
        dialog.get_by_role("button", name="Delete", exact=True).click()
        self.page.wait_for_timeout(1500)

    def last_toast_text(self) -> str:
        toast = self.page.locator(".p-toast-message, .toast, [role='alert']")
        return toast.first.inner_text() if toast.count() > 0 else ""

    def cancel_delete(self):
        self.delete_confirm_dialog().get_by_role("button", name="Cancel", exact=True).click()
        self.page.wait_for_timeout(500)
