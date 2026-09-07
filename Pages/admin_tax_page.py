import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class AdminTaxPage(BasePage):
    """/admin/tax -- Create Tax Profile form (left) + Tax List table (right)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: get_by_label("Tax")/("Percent") is too broad --
        # it also case-insensitively matches the "Tax" nav menuitem and the
        # "Export taxes to .../Print taxes table" action buttons (their
        # aria-labels contain "tax"/"taxes"). get_by_placeholder on each
        # input's real, unique placeholder is the reliable choice here.
        self.tax_name_input = page.get_by_placeholder("Enter Tax Name")
        # Confirmed live: Percent is a PrimeNG p-inputnumber -- the wrapper
        # component and its real inner input both match the placeholder,
        # but the inner input alone has a proper role="spinbutton".
        self.percent_input = page.get_by_role("spinbutton", name="Enter Tax Percentage")
        self.create_tax_button = page.get_by_role("button", name="Create Tax")
        # Confirmed live: same role/placeholder quirk as Manage User/Dealer
        # -- real role is "textbox" not "searchbox", placeholder is " Search".
        self.search_input = page.get_by_placeholder("Search")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/admin/tax")
        self.expect_path("/admin/tax")

    def create_tax(self, name: str, percent: str, wait_for_row: bool = True):
        self.tax_name_input.fill(name)
        # Confirmed live: this PrimeNG p-inputnumber field doesn't register
        # plain fill() as real input (the Submit button stayed disabled
        # even after fill() populated it) -- same Angular-reactive-form
        # gap documented in BasePage.type_into(), real keystrokes required.
        self.type_into(self.percent_input, percent)
        self.create_tax_button.click()
        self.wait_for_loading_to_finish()
        if wait_for_row:
            # Confirmed live: a "Success" toast fires before the table
            # re-fetch finishes -- row_by_name() right after a fixed sleep
            # can race a still-stale table. .count() doesn't auto-wait, so
            # poll actual body text instead of a blind sleep.
            self.wait_for_texts([name])
        self.page.wait_for_timeout(500)

    def is_create_button_enabled(self) -> bool:
        # Confirmed live: "Create Tax" is a real native-disabled button
        # (disabled attribute, not just a class) until required fields are
        # filled -- this is client-side required-field enforcement without
        # a separate validation-message element.
        return self.create_tax_button.is_enabled()

    def wait_for_table_loaded(self):
        # Confirmed live: rows render as p-skeleton placeholders briefly
        # before real data arrives -- wait those out before reading cells.
        self.page.locator("p-skeleton").first.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    def row_by_name(self, name: str) -> Locator:
        return self.rows().filter(has_text=name).first

    def total_count(self) -> int:
        self.wait_for_body_pattern(r"Showing\s+\d+\s+to\s+\d+\s+of\s+\d+\s+taxes?")
        match = re.search(r"Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)\s+taxes?", self.visible_text())
        return int(match.group(1)) if match else 0

    def edit_icon(self, row: Locator) -> Locator:
        # Confirmed live: bare <i class="pi pi-pencil">, no ptooltip and no
        # aria-label at all on this page's row icons (candidate
        # accessibility bug, same family as the ptooltip-only icons on
        # Manage User/Dealer -- here there isn't even a tooltip attribute).
        return row.locator("i.pi-pencil")

    def delete_icon(self, row: Locator) -> Locator:
        return row.locator("i.pi-trash")

    def delete_confirm_dialog(self) -> Locator:
        # Confirmed live: this is a PrimeNG p-confirmpopup (a small
        # tooltip-style popup anchored to the clicked icon), NOT a
        # .cdk-overlay-container/.p-dialog modal like every CRUD confirm
        # elsewhere in the admin panel -- "Do you want to delete this tax ?"
        # with No/Yes buttons.
        return self.page.locator(".p-confirmpopup")

    def confirm_delete(self):
        self.delete_confirm_dialog().get_by_role("button", name="Yes", exact=True).click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def cancel_delete(self):
        self.delete_confirm_dialog().get_by_role("button", name="No", exact=True).click()
        self.page.wait_for_timeout(500)

    def validation_errors(self) -> list[str]:
        return self.validation_messages()
