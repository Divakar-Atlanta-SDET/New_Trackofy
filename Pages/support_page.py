import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class SupportPage(BasePage):
    """Support Management (/profile/support) -- the user's ticket list.
    Confirmed live: heading with a count, "Raise Ticket" button, Rows-per-
    page select, pagination, a searchbox (needs a real Enter keypress),
    and a table (Ticket No., Description, Raised On, Priority, Status,
    Attachment, History). "View ticket history" navigates to a real route
    `/profile/support/ticket-history/<ticket_no>` (not a dialog) whose
    data populates a couple of seconds after the shell renders.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_role("searchbox")
        self.rows_per_page_select = page.get_by_label("Rows per page")
        self.next_page_button = page.get_by_role("button", name="Next page")
        self.previous_page_button = page.get_by_role("button", name="Previous page")
        self.first_page_button = page.get_by_role("button", name="First page")
        self.last_page_button = page.get_by_role("button", name="Last page")
        self.raise_ticket_button = page.get_by_role("button", name="Raise Ticket")
        self.table = page.get_by_role("table")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/profile/support")
        self.expect_path("/profile/support")
        self.wait_for_visible(self.table)
        self.page.wait_for_timeout(2000)

    def ticket_count(self) -> int:
        match = re.search(r"(\d+)\s*tickets?\b", self.visible_text())
        return int(match.group(1)) if match else -1

    def rows(self) -> Locator:
        return self.table.locator("tbody tr").filter(has_not_text=re.compile(r"no .*(found|records|tickets)", re.I))

    def row(self, ticket_no: str) -> Locator:
        return self.rows().filter(has_text=ticket_no).first

    def row_ticket_no(self, row: Locator) -> str:
        # Confirmed live: cell 0 also contains a decorative mat-icon
        # ("confirmation_number" ligature text) as a sibling of the real
        # ticket number span -- reading the whole cell picks up both.
        # Scope to the .tx-card-meta span, which holds only the number.
        return row.locator("td").nth(0).locator(".tx-card-meta").inner_text().strip()

    def row_description(self, row: Locator) -> str:
        return row.locator("td").nth(1).inner_text().strip()

    def row_priority(self, row: Locator) -> str:
        return row.locator("td").nth(3).inner_text().strip()

    def row_status(self, row: Locator) -> str:
        return row.locator("td").nth(4).inner_text().strip()

    def row_history_button(self, row: Locator) -> Locator:
        return row.get_by_role("button", name="View ticket history")

    def row_attachment_button(self, row: Locator) -> Locator:
        return row.get_by_role("button", name="View ticket attachment")

    def open_ticket_history(self, row: Locator):
        self.row_history_button(row).click()
        self.page.wait_for_url(re.compile(r".*/profile/support/ticket-history/.+"), timeout=self.DEFAULT_TIMEOUT_MS)
        self.wait_until_ready()
        # Confirmed live: this detail page's real data (Status/Priority/
        # Assigned To/etc.) populates a couple of seconds after the shell
        # renders -- reading immediately shows placeholder dashes.
        self.page.wait_for_timeout(3000)

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

    def change_rows_per_page(self, value: str):
        self.rows_per_page_select.select_option(label=value)
        self.page.wait_for_timeout(1000)

    # ------------------------------------------------------------- Raise Support Ticket dialog

    def open_raise_ticket_dialog(self):
        self.raise_ticket_button.click()
        self.wait_for_visible(self.raise_ticket_dialog())

    def raise_ticket_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(
            has_text="Raise Support Ticket"
        )

    def vehicle_combobox(self) -> Locator:
        return self.raise_ticket_dialog().get_by_role("combobox").nth(0)

    def category_combobox(self) -> Locator:
        return self.raise_ticket_dialog().get_by_role("combobox").nth(1)

    def severity_combobox(self) -> Locator:
        return self.raise_ticket_dialog().get_by_role("combobox").nth(2)

    def open_vehicle_dropdown(self):
        self.vehicle_combobox().click()
        self.page.wait_for_timeout(600)

    def select_vehicle(self, vehicle_id: str):
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()
        self.page.wait_for_timeout(400)

    def close_vehicle_dropdown(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def selected_vehicles_text(self) -> str:
        return self.vehicle_combobox().inner_text().strip()

    def selected_vehicle_count_text(self) -> str:
        text = self.raise_ticket_dialog().inner_text()
        match = re.search(r"(\d+)\s*selected", text)
        return match.group(0) if match else ""

    def select_category(self, category: str):
        self.category_combobox().click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=category, exact=True).click()
        self.page.wait_for_timeout(300)

    def select_severity(self, severity: str):
        self.severity_combobox().click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=severity, exact=True).click()
        self.page.wait_for_timeout(300)

    def comment_textarea(self) -> Locator:
        return self.raise_ticket_dialog().get_by_placeholder("Describe the issue in detail...")

    def comment_counter_text(self) -> str:
        match = re.search(r"(\d+)/(\d+)", self.raise_ticket_dialog().inner_text())
        return match.group(0) if match else ""

    def email_input(self) -> Locator:
        return self.raise_ticket_dialog().get_by_placeholder("example@mail.com")

    def mobile_input(self) -> Locator:
        return self.raise_ticket_dialog().get_by_placeholder("Enter 10-digit number")

    def attachment_file_input(self) -> Locator:
        return self.raise_ticket_dialog().locator("input[type='file']")

    def submit_ticket_button(self) -> Locator:
        return self.raise_ticket_dialog().get_by_role("button", name="Submit Ticket")

    def cancel_ticket_button(self) -> Locator:
        return self.raise_ticket_dialog().get_by_role("button", name="Cancel", exact=True)

    def close_ticket_dialog(self):
        self.raise_ticket_dialog().get_by_role("button", name="Close support ticket form").click()

    def fill_valid_ticket(
        self,
        vehicle_id: str | None = None,
        category: str = "Others",
        severity: str = "Low",
        comment: str = "Automated test ticket -- please ignore.",
        email: str = "pytest.qa@example.com",
        mobile: str = "9876543210",
    ):
        self.open_raise_ticket_dialog()
        self.open_vehicle_dropdown()
        if vehicle_id is None:
            # Avoid depending on a specific vehicle ID existing in this
            # account's fleet -- just take whatever the first real option is.
            vehicle_id = self.page.get_by_role("option").first.inner_text()
        self.select_vehicle(vehicle_id)
        self.close_vehicle_dropdown()
        self.select_category(category)
        self.select_severity(severity)
        self.type_into(self.comment_textarea(), comment)
        self.email_input().fill(email)
        self.mobile_input().fill(mobile)
