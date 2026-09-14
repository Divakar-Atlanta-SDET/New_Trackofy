import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanDashboardPage(CanBasePage):
    """CAN > Dashboard (/can/dashboard) -- KPI cards, Protocol Wise Assets
    and Online vs Offline charts, Recent Alerts panel, AI Fleet Summary,
    and the CAN Unit table.
    """

    KPI_LABELS = ["Total Assets", "Online / Reporting", "Offline / Stale", "Protocols", "Active Alerts"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Dashboard", exact=True)
        self.protocol_chart_heading = page.get_by_role("heading", name="Protocol Wise Assets", exact=True)
        self.online_offline_chart_heading = page.get_by_role("heading", name="Online vs Offline", exact=True)
        self.recent_alerts_heading = page.get_by_role("heading", name="Recent Alerts", exact=True)
        self.can_unit_table_heading = page.get_by_role("heading", name="CAN Unit", exact=True)
        # Confirmed live: the real accessible names differ from the
        # visible icon-ligature-prefixed text ("View All"/"Open Units"/
        # "AI Summary"/plain "refresh").
        self.view_all_alerts_link = page.get_by_role("link", name=re.compile(r"View all CAN alerts", re.I))
        self.open_units_link = page.get_by_role("link", name=re.compile(r"Open units page", re.I))
        self.ai_summary_button = page.get_by_role("button", name=re.compile(r"Open AI fleet summary", re.I))
        self.refresh_button_kpi = page.get_by_role("button", name=re.compile(r"Refresh dashboard", re.I))
        self.table = page.get_by_role("table")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/dashboard")
        self.expect_path("/can/dashboard")
        self.wait_for_visible(self.heading)

    def kpi_value(self, label: str) -> str:
        # Confirmed live: the KPI strip renders as
        # "<icon>\n\n<Label>\n\n<value>\n\n<optional %>" per card -- the
        # numeric value is the first number immediately following the
        # exact label text in the page's visible text. The value can
        # still be arriving asynchronously right after the heading
        # becomes visible, so poll briefly rather than reading once.
        import time

        deadline = time.monotonic() + 5
        while True:
            body = self.visible_text()
            match = re.search(rf"{re.escape(label)}\s*\n+\s*(\d+(?:\.\d+)?)", body)
            if match:
                return match.group(1)
            if time.monotonic() >= deadline:
                return ""
            self.page.wait_for_timeout(250)

    def all_kpi_values(self) -> dict[str, str]:
        return {label: self.kpi_value(label) for label in self.KPI_LABELS}

    def recent_alert_rows(self) -> Locator:
        panel = self.page.locator("*").filter(has=self.recent_alerts_heading).last
        return panel.locator("article, li, .alert-item").filter(has_text=re.compile(r"(Warning|Critical)"))

    def open_view_all_alerts(self):
        self.safe_click(self.view_all_alerts_link)
        self.expect_path("/can/alerts")

    def open_units_from_dashboard(self):
        self.safe_click(self.open_units_link)
        self.expect_path("/can/units")

    def open_ai_summary(self):
        self.safe_click(self.ai_summary_button)
        self.page.wait_for_timeout(1000)

    def ai_summary_panel(self) -> Locator:
        # Confirmed live 2026-09-14: this panel is a plain inline
        # <aside class="cai-drawer"> in the page's own DOM, not a CDK
        # overlay/dialog -- the panel genuinely opens with real content
        # (fleet stats, vitals, highlights), the old locator just never
        # matched it.
        return self.page.locator("aside.cai-drawer")

    def click_refresh(self):
        self.safe_click(self.refresh_button_kpi.first)

    def unit_table_row_count(self) -> int:
        if self.table.count() == 0:
            return 0
        return self.table.last.locator("tbody tr").count()
