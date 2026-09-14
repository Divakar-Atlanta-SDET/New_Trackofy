import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanAlertsPage(CanBasePage):
    """CAN > Alerts (/can/alerts) -- the CAN warning/critical Alert Log
    table, its Protocol/Level/Unit filters, search, export, sorting, and
    pagination.
    """

    COLUMNS = ["S.No", "Level", "Unit", "IMEI", "Protocol", "Metric", "Actual", "Limit", "Message", "Last Contact"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Alerts", exact=True)
        self.alert_log_heading = page.get_by_role("heading", name="Alert Log", exact=True)
        self.table = page.get_by_role("table")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/alerts")
        self.expect_path("/can/alerts")
        self.wait_for_visible(self.heading)
        # Confirmed live 2026-09-14: same loading-race as can_unit_page's
        # open() -- the heading appears before the table's real row data
        # has loaded, so a caller reading cell_values()/level_values()
        # immediately afterward can get an empty table. Here
        # wait_for_loading_to_finish() alone isn't enough (its own
        # spinner clears before the table body actually re-renders) --
        # also poll briefly for the "No records found" placeholder to
        # clear, up to a real content-load timeout.
        self.wait_for_loading_to_finish()
        no_records = self.page.get_by_text("No records found", exact=False)
        for _ in range(10):
            if no_records.count() == 0 or self.total_alert_count() > 0:
                break
            self.page.wait_for_timeout(500)

    def total_alert_count(self) -> int:
        return self._read_stable_int(r"(\d+)\s*\nalerts")

    def rows(self) -> Locator:
        return self.table.last.locator("tbody tr")

    def row_count(self) -> int:
        if self.table.count() == 0:
            return 0
        return self.rows().count()

    def cell_values(self, column_index: int, max_rows: int = 20) -> list[str]:
        rows = self.rows()
        count = min(rows.count(), max_rows)
        values = []
        for i in range(count):
            cells = rows.nth(i).locator("td")
            if cells.count() > column_index:
                values.append(cells.nth(column_index).inner_text().strip())
        return values

    def level_values(self, max_rows: int = 20) -> list[str]:
        return self.cell_values(self.COLUMNS.index("Level"), max_rows)

    def open_apply_filter(self):
        self.safe_click(self.apply_filter_button())
        self.wait_for_visible(self.filter_drawer())

    def filter_by_protocol(self, protocol_name: str):
        self.open_apply_filter()
        drawer = self.filter_drawer()
        self.safe_click(self.combobox_by_visible_label("Protocol", container=drawer))
        self.safe_click(self.custom_option(protocol_name))
        self.safe_click(self.apply_filter_submit_button(drawer))
        self.wait_for_loading_to_finish()

    def filter_by_level(self, level: str):
        self.open_apply_filter()
        drawer = self.filter_drawer()
        self.safe_click(self.combobox_by_visible_label("Level", container=drawer))
        self.safe_click(self.custom_option(level))
        self.safe_click(self.apply_filter_submit_button(drawer))
        self.wait_for_loading_to_finish()

    def filter_by_unit(self, unit_name: str):
        self.open_apply_filter()
        drawer = self.filter_drawer()
        self.safe_click(self.combobox_by_visible_label("Unit", container=drawer))
        self.safe_click(self.custom_option(unit_name))
        self.safe_click(self.apply_filter_submit_button(drawer))
        self.wait_for_loading_to_finish()

    def reset_filters(self):
        drawer = self.filter_drawer()
        self.safe_click(self.reset_filter_button(drawer))
        self.wait_for_loading_to_finish()
