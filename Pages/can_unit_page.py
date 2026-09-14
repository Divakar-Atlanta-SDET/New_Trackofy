import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanUnitPage(CanBasePage):
    """CAN > Unit (/can/units) -- CAN-enabled unit list with search,
    protocol/status filters, export, sorting, and pagination.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Units", exact=True)
        self.list_heading = page.get_by_role("heading", name="Unit List", exact=True)
        self.table = page.get_by_role("table")
        self.protocol_filter = page.get_by_role("combobox", name="Protocol")
        self.status_filter = page.get_by_role("combobox", name="Status")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/units")
        self.expect_path("/can/units")
        self.wait_for_visible(self.heading)
        # Confirmed live 2026-09-14: the heading appears before the
        # table's real row data has loaded -- same loading-race shape
        # already fixed for numeric KPI reads (_read_stable_int), just
        # affecting row content here instead. A caller reading
        # cell_values() immediately after open() can get an empty/
        # incomplete table.
        self.wait_for_loading_to_finish()

    def rows(self) -> Locator:
        return self.table.last.locator("tbody tr")

    def row_count(self) -> int:
        if self.table.count() == 0:
            return 0
        return self.rows().count()

    def column_headers(self) -> list[str]:
        if self.table.count() == 0:
            return []
        headers = self.table.last.locator("thead th")
        return [headers.nth(i).inner_text().strip() for i in range(headers.count()) if headers.nth(i).inner_text().strip()]

    def cell_values(self, column_index: int, max_rows: int = 20) -> list[str]:
        rows = self.rows()
        count = min(rows.count(), max_rows)
        values = []
        for i in range(count):
            cells = rows.nth(i).locator("td")
            if cells.count() > column_index:
                values.append(cells.nth(column_index).inner_text().strip())
        return values

    def row_by_unit_name(self, unit_name: str) -> Locator:
        return self.rows().filter(has_text=unit_name)

    def view_unit(self, row: Locator):
        # Confirmed live: the row action's real accessible name is "View
        # unit insights", not the visible "visibility" icon-ligature text.
        self.safe_click(row.get_by_role("button", name="View unit insights"))
        self.wait_for_loading_to_finish()

    def sort_by_column(self, column_name: str):
        header = self.table.last.locator("thead").get_by_text(column_name, exact=False).first
        self.wait_for_visible(header)
        self.safe_click(header)
        self.wait_for_loading_to_finish()

    def open_apply_filter(self):
        self.safe_click(self.apply_filter_button())
        self.wait_for_visible(self.filter_drawer())

    def filter_by_protocol(self, protocol_name: str):
        self.open_apply_filter()
        drawer = self.filter_drawer()
        self.safe_click(drawer.get_by_role("combobox", name="Protocol"))
        self.safe_click(self.custom_option(protocol_name))
        self.safe_click(self.apply_filter_submit_button(drawer))
        self.wait_for_loading_to_finish()

    def filter_by_status(self, status: str):
        self.open_apply_filter()
        drawer = self.filter_drawer()
        self.safe_click(drawer.get_by_role("combobox", name="Status"))
        self.safe_click(self.custom_option(status))
        self.safe_click(self.apply_filter_submit_button(drawer))
        self.wait_for_loading_to_finish()

    def reset_filters(self):
        drawer = self.filter_drawer()
        self.safe_click(self.reset_filter_button(drawer))
        self.wait_for_loading_to_finish()

    def has_no_results_state(self) -> bool:
        return self.contains_any_text(["No data", "No results", "No records found"])
