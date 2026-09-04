import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class DownloadsPage(BasePage):
    """Downloads (/profile/downloads) -- generated report file history.
    Confirmed live: heading with a count, Rows-per-page select, pagination
    buttons, a searchbox (requires a real Enter keypress to filter, same
    quirk as other modules this session), and a table (#, Report Name,
    Requested On, Duration, Status, Download). Done rows have a real
    download <a> link; Pending rows show a plain "----" placeholder with
    no interactive control at all.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_role("searchbox")
        self.rows_per_page_select = page.get_by_label("Rows per page")
        self.next_page_button = page.get_by_role("button", name="Next page")
        self.previous_page_button = page.get_by_role("button", name="Previous page")
        self.first_page_button = page.get_by_role("button", name="First page")
        self.last_page_button = page.get_by_role("button", name="Last page")
        self.table = page.get_by_role("table")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/profile/downloads")
        self.expect_path("/profile/downloads")
        self.wait_for_visible(self.table)
        # Confirmed live: the table can render with only a partial/loading
        # row set for a moment after the shell appears -- give the real
        # data a beat before reading rows.
        self.page.wait_for_timeout(2000)

    def report_count(self) -> int:
        match = re.search(r"(\d+)\s*reports?\b", self.visible_text())
        return int(match.group(1)) if match else -1

    def rows(self) -> Locator:
        # Confirmed live: a "No records found"-style empty state also
        # renders as a real <tr> in tbody -- same quirk seen in the
        # Administrator module's user table.
        return self.table.locator("tbody tr").filter(has_not_text=re.compile(r"no .*(found|records)", re.I))

    def row(self, report_name: str) -> Locator:
        return self.rows().filter(has_text=report_name).first

    def row_status(self, row: Locator) -> str:
        return row.locator("td").nth(4).inner_text().strip()

    def row_report_name(self, row: Locator) -> str:
        return row.locator("td").nth(1).inner_text().strip()

    def row_serial_number(self, row: Locator) -> str:
        """The '#' column -- confirmed live report names commonly repeat
        (the same report generated multiple times), so this (or the
        Requested On date) is what actually identifies a specific row."""
        return row.locator("td").nth(0).inner_text().strip()

    def row_download_link(self, row: Locator) -> Locator:
        return row.get_by_role("link", name="Download report")

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
