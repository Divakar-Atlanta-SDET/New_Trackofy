import re

from playwright.sync_api import Locator, Page

from Pages.video_telematics_page import VideoTelematicsBasePage


class VideoTelematicsDashboardPage(VideoTelematicsBasePage):
    """Video Telematics > Dashboard (/video_telematics/dashboard).
    Confirmed live: KPI strip (Total Vehicles/Online/Offline/Alerts
    Today/Critical/Warning/Info), a Live Video panel, an Alerts &
    Notifications panel, and the shared Live Fleet Map widget.
    """

    KPI_LABELS = [
        "Total Vehicles", "Online", "Offline", "Alerts Today",
        "Critical Alerts", "Warning", "Info",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_text("Video Telematics Dashboard", exact=True)
        self.live_monitoring_indicator = page.get_by_text("Live Monitoring", exact=True)
        self.alerts_panel_heading = page.get_by_text("Alerts & Notifications", exact=True)
        # Confirmed live: two distinct "refresh" icon-buttons exist on
        # this page (Live Video panel's own, then Alerts panel's), and
        # their <mat-icon> is aria-hidden -- role+name="refresh" matches
        # neither, so these are found by icon text then walked up to
        # the real ancestor <button>.
        self.alerts_refresh_button = page.get_by_text("refresh", exact=True).nth(1).locator("xpath=ancestor::button[1]")
        # Confirmed live: this is a <button> whose text includes a
        # leading icon ligature ("history\nView alert history"), so an
        # exact text match never matches -- role+substring name does.
        self.view_alert_history_link = page.get_by_role("button", name="View alert history")
        self.live_video_heading = page.get_by_text("Live Video", exact=True)
        # Confirmed live: neither has a stable accessible name of its own
        # (name = currently selected value) -- same convention as every
        # other module combobox pair.
        self.live_video_vehicle_select = page.get_by_role("combobox").nth(0)
        self.live_video_channel_select = page.get_by_role("combobox").nth(1)
        self.live_video_refresh_button = page.get_by_text("refresh", exact=True).nth(0).locator("xpath=ancestor::button[1]")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/video_telematics/dashboard")
        self.expect_path("/video_telematics/dashboard")
        self.wait_for_visible(self.heading)

    def kpi_value(self, label: str) -> int:
        # Confirmed live: no shared role/label connects a KPI's number to
        # its own label anywhere in this widget (same structural gap as
        # My Profile's Personal & Preferences fields) -- the number is
        # the very next text sibling after the exact-text label.
        label_locator = self.page.get_by_text(label, exact=True)
        value_locator = label_locator.locator("xpath=following-sibling::*[1]")
        text = value_locator.inner_text(timeout=self.DEFAULT_TIMEOUT_MS).strip()
        return int(text)

    def is_alerts_empty_state_shown(self) -> bool:
        return self.contains_texts(["No alerts found"])
