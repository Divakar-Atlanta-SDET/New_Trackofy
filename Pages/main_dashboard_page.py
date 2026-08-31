import re
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage


class MainDashboardPage(BasePage):
    """Page object for the main Trackofy application Dashboard tab (/dashboard/graphical)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header and Top Controls
        self.dashboard_heading = page.get_by_role("heading", name="Dashboard", exact=True)
        self.graphical_view_button = page.get_by_role("button", name=re.compile(r"Graphical", re.I)).first
        self.tabular_view_button = page.get_by_role("button", name=re.compile(r"Tabular", re.I)).first
        self.refresh_dashboard_button = page.get_by_role("button", name=re.compile(r"Refresh dashboard", re.I)).first
        self.ai_insights_button = page.get_by_role("button", name=re.compile(r"AI Insights", re.I)).first
        self.widgets_button = page.locator("button").filter(has_text=re.compile(r"Widgets", re.I)).first
        self.trash_button = page.locator("button").filter(has_text=re.compile(r"Trash", re.I)).first

        # Top Summary KPI Cards
        self.total_fleet_metric = page.get_by_text("Total Fleet", exact=True).first
        self.active_devices_metric = page.get_by_text("Active Devices", exact=True).first
        self.running_devices_metric = page.get_by_text("Running", exact=True).first
        self.idle_devices_metric = page.get_by_text("Idle", exact=True).first
        self.stopped_devices_metric = page.get_by_text("Stopped", exact=True).first
        self.no_data_devices_metric = page.get_by_text("No Data", exact=True).first
        self.expired_devices_metric = page.get_by_text("Expired Devices", exact=True).first
        self.bms_enabled_metric = page.get_by_text("BMS Enabled", exact=True).first
        self.video_enabled_metric = page.get_by_text("Video Enabled", exact=True).first

        # Store & Drawer Overlays
        self.widget_store_heading = page.get_by_role("heading", name=re.compile(r"Widget Stores", re.I)).first
        self.close_widget_store_button = page.get_by_role("button", name=re.compile(r"Close widget stores", re.I)).first
        self.fleet_widget_store_link = page.get_by_role("link", name=re.compile(r"Fleet Widget Store", re.I)).first
        self.bms_widget_store_link = page.get_by_role("link", name=re.compile(r"BMS Widget Store", re.I)).first
        self.video_telematics_store_link = page.get_by_role("link", name=re.compile(r"Video Telematics", re.I)).first

    def open_graphical_dashboard(self):
        """Navigate directly to the graphical dashboard route."""
        self.page.goto("/dashboard/graphical")
        self.wait_for_dashboard_ready()

    def open_tabular_dashboard(self):
        """Navigate directly to the tabular / live dashboard route."""
        self.page.goto("/dashboard/live")
        self.wait_until_ready()

    def wait_for_dashboard_ready(self):
        """Wait until the main dashboard container and KPI section are fully loaded."""
        self.page.wait_for_url(re.compile(r".*/dashboard/(graphical|live|tabular)?.*$"), timeout=15000)
        self.wait_until_ready()
        self.wait_for_visible(self.dashboard_heading)

    def switch_to_tabular_view(self):
        """Click on Tabular view button."""
        self.wait_for_visible(self.tabular_view_button)
        self.tabular_view_button.click()
        self.wait_until_ready()

    def switch_to_graphical_view(self):
        """Click on Graphical view button."""
        self.wait_for_visible(self.graphical_view_button)
        self.graphical_view_button.click()
        self.wait_until_ready()

    def refresh_dashboard(self):
        """Click on Refresh dashboard button and wait for reload."""
        self.wait_for_visible(self.refresh_dashboard_button)
        self.refresh_dashboard_button.click()
        self.wait_for_loading_to_finish()

    def get_widget_titles_order(self) -> list[str]:
        """Extract order of visible widget card headings on the dashboard."""
        self.wait_until_ready()
        headings = self.page.locator("main h2, main h3, [class*='card'] h2").all()
        titles: list[str] = []
        for h in headings:
            if h.is_visible():
                txt = h.inner_text().strip()
                if txt and txt not in {"Dashboard", "Widget Stores", "Build your dashboard", "Actions"}:
                    titles.append(txt)
        return titles

    def drag_and_drop_widget(self, source_title: str, target_title: str):
        """Drag a widget card handle onto a target widget card position."""
        source_heading = self.page.locator("main h2, main h3").filter(has_text=re.compile(rf"\b{re.escape(source_title)}\b", re.I)).first
        target_heading = self.page.locator("main h2, main h3").filter(has_text=re.compile(rf"\b{re.escape(target_title)}\b", re.I)).first
        self.wait_for_visible(source_heading)
        self.wait_for_visible(target_heading)

        source_card = source_heading.locator("xpath=ancestor::*[contains(@class, 'card') or contains(@class, 'grid') or contains(@class, 'wrapper')][position()<=4]").last
        target_card = target_heading.locator("xpath=ancestor::*[contains(@class, 'card') or contains(@class, 'grid') or contains(@class, 'wrapper')][position()<=4]").last

        source_handle = source_card.locator(".grid-drag-handle, [aria-label*='Reorder'], mat-icon:has-text('open_with')").first
        if not source_handle.is_visible():
            source_handle = source_card

        source_handle.drag_to(target_card)
        self.wait_for_loading_to_finish()

    def open_widget_store(self):
        """Click Widgets button to open Widget Store drawer."""
        self.wait_for_visible(self.widgets_button)
        self.widgets_button.click()
        self.wait_for_visible(self.widget_store_heading)

    def close_widget_store(self):
        """Close Widget Store drawer."""
        if self.close_widget_store_button.is_visible():
            self.close_widget_store_button.click()
        else:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def open_trash_store(self):
        """Click Trash button to open Trash Store modal/panel."""
        self.wait_for_visible(self.trash_button)
        self.trash_button.click()
        self.wait_for_loading_to_finish()

    def open_ai_insights(self):
        """Click AI Insights button in header."""
        self.wait_for_visible(self.ai_insights_button)
        self.ai_insights_button.click()
        self.wait_for_loading_to_finish()

    def get_widget_column_header(self, widget_title: str, column_name: str) -> Locator:
        """Get column header locator for a given table column."""
        header = self.page.locator("th, [role='columnheader']").filter(has_text=re.compile(rf"\b{re.escape(column_name)}\b", re.I)).first
        return header

    def click_column_header_to_sort(self, widget_title: str, column_name: str):
        """Click a widget table column header to toggle sorting (Ascending / Descending)."""
        header = self.get_widget_column_header(widget_title, column_name)
        self.wait_for_visible(header)
        header.click()
        self.wait_for_loading_to_finish()

    def get_widget_table_column_values(self, widget_title: str, column_name: str) -> list[str]:
        """Extract visible cell values under a given column in a widget table."""
        rows = self.page.locator("tbody tr, table tr").all()
        values: list[str] = []
        for r in rows:
            cells = r.locator("td, [role='cell']").all()
            if cells:
                txt = cells[0].inner_text().strip()
                if txt and txt != "No data available" and txt != "No data found":
                    values.append(txt)
        return values

    def open_widget_filter(self, widget_title: str):
        """Click the Filter widget data icon button on a widget card."""
        filter_button = self.page.locator("button").filter(has=self.page.locator("mat-icon:has-text('filter_alt'), img[alt*='filter']")).first
        self.wait_for_visible(filter_button)
        filter_button.click()
        self.wait_for_loading_to_finish()
