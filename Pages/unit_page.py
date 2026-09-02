import re
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage


class UnitPage(BasePage):
    """Page Object for the Trackofy Unit List page (/unit)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header and Unit Count Badge
        self.unit_list_heading = page.locator("h1, header h1").filter(has_text=re.compile(r"Unit List", re.I)).first
        # The header count lives in <span class="tx-data-count"><strong>39</strong> units</span>
        # next to the heading -- targeted via that class rather than "first
        # <strong> on the page" (which also matches the All/Active/Expired/Due
        # Soon filter buttons' counts and only worked before by DOM-order luck).
        self.unit_count_badge = page.locator(".tx-data-count strong").first

        # Search and Filters
        self.search_box = page.get_by_placeholder(re.compile(r"Search units", re.I))
        self.unit_type_filter = page.get_by_role("combobox", name=re.compile(r"unit types", re.I))

        # Table & Rows
        self.table = page.get_by_role("table").first
        self.table_rows = page.locator("tbody tr")

    def open_unit_list(self):
        """Navigate to the Unit list page."""
        self.page.goto("/unit")
        self.wait_for_unit_page_ready()

    def wait_for_unit_page_ready(self):
        """Wait until Unit list page is loaded."""
        self.page.wait_for_url(re.compile(r".*/unit/?$"), timeout=15000)
        self.wait_until_ready()
        self.wait_for_visible(self.unit_list_heading)
        self.table_rows.first.wait_for(state="visible", timeout=15000)

    def search_unit(self, keyword: str):
        """Type keyword into search input."""
        self.wait_for_visible(self.search_box)
        self.search_box.fill(keyword)
        self.wait_for_loading_to_finish()

    def filter_by_unit_type(self, unit_type: str):
        """Select a unit type filter option."""
        combo = self.page.locator("mat-select, [role='combobox']").filter(has_text=re.compile(r"Unit Types", re.I)).first
        self.wait_for_visible(combo)
        combo.click()
        option = self.page.get_by_role("option", name=unit_type).first
        self.wait_for_visible(option)
        option.click()
        self.wait_for_loading_to_finish()

    def open_unit_settings_by_index(self, index: int = 0):
        """Click the Open unit settings button on a specific table row."""
        self.table_rows.first.wait_for(state="visible", timeout=15000)
        row = self.table_rows.nth(index)
        btn = row.get_by_role("button", name="Open unit settings")
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def get_unit_count(self) -> int:
        """Read total unit count from badge with fallback to table rows."""
        self.table_rows.first.wait_for(state="visible", timeout=15000)
        row_count = self.table_rows.count()
        if self.unit_count_badge.is_visible():
            txt = self.unit_count_badge.inner_text().strip()
            match = re.search(r"\d+", txt)
            if match:
                val = int(match.group(0))
                if val > 0:
                    return val
        return row_count
