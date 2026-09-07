from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class AdminPlanPage(BasePage):
    """Create Plan (/admin/plan/create-plan), Manage Plan
    (/admin/plan/manage-plan)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: Plan Name has a real id ("planName") -- reachable
        # via get_by_label. BillType* also has a real id, but "Currency*"'s
        # label incorrectly shares BillType's id (a real, confirmed bug --
        # see comment on bill_type_combobox below), so Currency has no
        # independently-reachable label target and isn't automated here
        # (it auto-derives from BillType selection, confirmed live).
        self.plan_name_input = page.get_by_label("Plan Name", exact=False)
        # Confirmed live: with BOTH "BillType*" and "Currency*" labels
        # pointing to the same id ("billType"), get_by_label("BillType")
        # actually resolves to ZERO matches (not even a strict-mode
        # multi-match error) -- the duplicate association breaks label
        # lookup entirely for this field, not just for Currency as
        # originally assumed. Positional access is the only way in.
        self.bill_type_combobox = page.get_by_role("combobox").nth(0)
        # Confirmed live: Selling Amount is a PrimeNG p-inputnumber -- both
        # the wrapper component and its real inner input share
        # id="totalAmount" (same duplicate-id shape as Tax's Percent
        # field), so a plain #totalAmount selector is ambiguous; the
        # inner input's real placeholder-derived accessible name
        # disambiguates it.
        self.selling_amount_input = page.get_by_role("spinbutton", name="Total Selling Amount")
        self.description_input = page.get_by_label("Description", exact=False)
        self.submit_button = page.get_by_role("button", name="Submit")
        self.search_input = page.get_by_placeholder("Search")

    def open_create_plan(self, base_url: str):
        self.page.goto(f"{base_url}/admin/plan/create-plan")
        self.expect_path("/admin/plan/create-plan")

    def open_manage_plan(self, base_url: str):
        self.page.goto(f"{base_url}/admin/plan/manage-plan")
        self.expect_path("/admin/plan/manage-plan")

    def select_combobox_option(self, combobox: Locator, option_name: str = "", exact: bool = False):
        combobox.click()
        self.page.wait_for_timeout(500)
        options = self.page.get_by_role("option")
        if option_name:
            options.filter(has_text=option_name).first.click()
        else:
            options.first.click()
        self.page.wait_for_timeout(300)

    def payment_type_table(self) -> Locator:
        return self.page.locator("table").filter(has_text="Payment Type")

    def check_payment_type_row(self, index: int = 0):
        """Confirmed live: checking a Payment Type row's own checkbox
        (Monthly=0, Quarterly=1, Half Yearly=2, Yearly=3) both enables
        AND auto-derives that row's Amount from Selling Amount (e.g.
        Selling Amount 99 -> Monthly 99, Quarterly 297, Half Yearly 594,
        Yearly 1188) -- no manual amount entry needed or wanted; a manual
        press_sequentially into an already-populated field just appends
        digits onto the existing value (confirmed live: 99 + typed "50"
        became "9950", not "50")."""
        self.payment_type_table().locator("tbody tr").nth(index).locator("input[type=checkbox]").click()
        self.page.wait_for_timeout(500)

    def check_menu_item(self, index: int = 0):
        """Confirmed live: at least one Menu List item checkbox must be
        checked for Submit to enable -- these gate which app features
        this plan grants access to, each with a default "Total Cost 100"
        already pre-filled."""
        self.page.get_by_role("checkbox").nth(index).click()
        self.page.wait_for_timeout(500)

    def fill_required_fields(self, plan_name: str, bill_type: str, selling_amount: str, description: str = ""):
        self.plan_name_input.fill(plan_name)
        self.select_combobox_option(self.bill_type_combobox, bill_type)
        self.page.wait_for_timeout(500)
        self.selling_amount_input.click()
        self.selling_amount_input.press_sequentially(selling_amount, delay=60)
        if description:
            self.description_input.fill(description)

    def create_plan_minimal(self, plan_name: str, selling_amount: str = "99", bill_type: str = "Postpaid"):
        """Drives Create Plan to a submit-enabled state using the real
        minimum: Plan Name, BillType, Selling Amount, ONE Payment Type
        row, and ONE Menu List item.

        Confirmed live (reverified after the user reported the button
        looked clickable with a minimal selection): an earlier version
        of this docstring claimed Submit stayed disabled until every
        Payment Type row and every Menu List item were checked. That was
        a false conclusion caused by the earlier investigation missing a
        SECOND, separate confirmation dialog ("Please check your selling
        amount before submitting... Do you want to continue?") that
        Submit opens -- only the first (form-level) Submit was ever
        clicked, its own confirmation-dialog Submit never was, so no
        `POST /api/create-plan` call was ever actually attempted. With
        both clicks performed (see submit()), a minimal 1-row/1-item
        selection creates a real plan just as reliably as checking
        everything -- confirmed via a real `plan_id` returned by the
        API across repeated trials. See submit()'s docstring for the
        confirmation-dialog handling."""
        self.plan_name_input.fill(plan_name)
        self.select_combobox_option(self.bill_type_combobox, bill_type)
        self.page.wait_for_timeout(500)
        self.selling_amount_input.click()
        self.selling_amount_input.press_sequentially(selling_amount, delay=60)
        self.page.wait_for_timeout(500)
        self.check_payment_type_row(0)
        self.page.wait_for_timeout(800)
        self.check_menu_item(0)
        self.page.wait_for_timeout(1500)

    def is_submit_enabled(self) -> bool:
        return self.submit_button.is_enabled()

    def submit(self):
        # Confirmed live: clicking the form's own Submit button doesn't
        # create the plan directly -- it opens a SECOND confirmation
        # dialog ("Please check your selling amount before submitting...
        # Do you want to continue?", Cancel/Submit) with its own,
        # separately-scoped Submit button (get_by_role("button",
        # name="Submit") resolves to 2 elements once this dialog is
        # open). The real POST /api/create-plan call only fires after
        # THAT second Submit is clicked.
        self.submit_button.click()
        self.page.wait_for_timeout(1000)
        confirm_submit = self.page.get_by_role("button", name="Submit").last
        confirm_submit.click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1500)

    # ------------------------------------------------------------- Manage Plan list
    def search(self, query: str):
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    def row_by_name(self, name: str) -> Locator:
        return self.rows().filter(has_text=name).first

    def menu_tag(self, row: Locator) -> Locator:
        """The row's "Menu" tag opens a read-only menu-cost breakdown
        dialog -- confirmed live this is the ONLY interactive element on
        a Manage Plan row. Confirmed live: there is no Edit or Delete
        action anywhere on this table (no action-icon column exists at
        all -- columns are S.No/Plan Name/Payments/Menu/Description
        only), the same gap already documented for Manage Dealer
        (Bug #59) -- a plan created here is permanent."""
        return row.locator("p-tag")
