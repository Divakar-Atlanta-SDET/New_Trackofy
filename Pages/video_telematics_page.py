from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class VideoTelematicsBasePage(BasePage):
    """Shared left-nav (Dashboard/Alert/Playback/Report) and the
    persistent Live Fleet Map widget, present on every Video Telematics
    sub-page (routes confirmed live: /video_telematics/dashboard,
    /alert, /playback, /report).
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: the module's own "Dashboard" nav link shares
        # its exact accessible name with the main app's global nav
        # Dashboard link (both render as role=link, name="Dashboard") --
        # role/text alone can't disambiguate them, so this scopes by the
        # one real structural difference between them, their href.
        self.nav_dashboard = page.locator("a[href='/video_telematics/dashboard']")
        self.nav_alert = page.get_by_role("link", name="Alert", exact=True)
        self.nav_playback = page.get_by_role("link", name="Playback", exact=True)
        self.nav_report = page.get_by_role("link", name="Report", exact=True)

        self.live_fleet_map_heading = page.get_by_text("Live Fleet Map", exact=True)
        self.map_view_button = page.get_by_role("button", name="Map", exact=True)
        self.hybrid_view_button = page.get_by_role("button", name="Hybrid", exact=True)
        self.map_minimize_button = page.get_by_role("button", name="Minimize map")
        self.map_fullscreen_button = page.get_by_role("button", name="Toggle fullscreen view")

    def map_view_active(self) -> bool:
        return "bg-(--mat-sys-primary-container)" in (self.map_view_button.get_attribute("class") or "")

    def hybrid_view_active(self) -> bool:
        return "bg-(--mat-sys-primary-container)" in (self.hybrid_view_button.get_attribute("class") or "")

    def open_dashboard(self):
        self.nav_dashboard.click()
        self.expect_path("/video_telematics/dashboard")

    def open_alert(self):
        self.nav_alert.click()
        self.expect_path("/video_telematics/alert")

    def open_playback(self):
        self.nav_playback.click()
        self.expect_path("/video_telematics/playback")

    def open_report(self):
        self.nav_report.click()
        self.expect_path("/video_telematics/report")
