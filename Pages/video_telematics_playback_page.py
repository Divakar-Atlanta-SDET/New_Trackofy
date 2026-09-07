import re
from datetime import date

from playwright.sync_api import Locator, Page

from Pages.video_telematics_page import VideoTelematicsBasePage


class VideoTelematicsPlaybackPage(VideoTelematicsBasePage):
    """Video Telematics > Playback (/video_telematics/playback) -- search
    historical MDVR recordings by vehicle/channel/date/time-range.

    Confirmed live (ADAS account): B123456 has real recordings for
    today (B123459 still has none). Selecting a file card's own
    play_arrow button loads and auto-plays it (a real <video> element
    appears; there is no discoverable pause control -- no click/hover/
    spacebar toggle found -- so playback is continuous once started).
    """

    CHANNELS = ["All Channels", "Channel 1", "Channel 2", "Channel 3"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Video Playback")
        self.filters_heading = page.get_by_text("Playback Filters", exact=True)
        self.reset_button = page.get_by_role("button", name="Reset", exact=True)
        self.find_files_button = page.get_by_role("button", name="Find Files")
        # Confirmed live: neither combobox has a stable accessible name of
        # its own (name = currently selected value) -- scoped by position,
        # same convention as the Alert Configuration list's filters.
        self.vehicle_select = page.get_by_role("combobox").nth(0)
        self.channel_select = page.get_by_role("combobox").nth(1)
        self.date_input = page.get_by_label("Date")
        self.from_time_input = page.get_by_label("From Time")
        self.to_time_input = page.get_by_label("To Time")
        self.calendar_toggle = page.get_by_role("button", name="Open calendar")

        self.playback_files_heading = page.get_by_role("heading", name="Playback Files")
        self.playback_video_heading = page.get_by_role("heading", name="Playback Video")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/video_telematics/playback")
        self.expect_path("/video_telematics/playback")
        self.wait_for_visible(self.heading)

    def files_count(self) -> int:
        match = re.search(r"Playback Files\s*\n?\s*(\d+)", self.visible_text())
        return int(match.group(1)) if match else -1

    def _open_option_panel(self, combobox: Locator) -> Locator:
        combobox.click()
        self.page.wait_for_timeout(400)
        panel_id = combobox.get_attribute("aria-controls")
        return self.page.locator(f"#{panel_id}")

    def select_vehicle(self, vehicle_id: str):
        panel = self._open_option_panel(self.vehicle_select)
        panel.get_by_role("option", name=vehicle_id, exact=False).click()
        self.page.wait_for_timeout(400)

    def select_channel(self, channel: str):
        panel = self._open_option_panel(self.channel_select)
        panel.get_by_role("option", name=channel, exact=True).click()
        self.page.wait_for_timeout(400)

    def select_date(self, target: date):
        # Confirmed live: the Date field is a readonly mat-datepicker
        # input -- must go through the real calendar popup, not fill().
        # Playwright's locator.filter(has_text=<anchored regex>) does not
        # reliably match a gridcell's exact day number here (JS regex `$`
        # semantics differ from Python's around trailing newlines in the
        # cell's computed text), so days are matched by exact trimmed
        # inner_text instead.
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)
        self.calendar_toggle.click()
        self.page.wait_for_timeout(600)
        today = date.today()
        months_diff = (target.year - today.year) * 12 + (target.month - today.month)
        nav_button_name = "Next month" if months_diff > 0 else "Previous month"
        nav_button = self.page.get_by_role("button", name=nav_button_name)
        for _ in range(abs(months_diff)):
            nav_button.click()
            self.page.wait_for_timeout(300)
        cells = self.page.get_by_role("gridcell")
        for i in range(cells.count()):
            cell = cells.nth(i)
            if cell.inner_text().strip() == str(target.day) and "mat-calendar-body-disabled" not in (cell.get_attribute("class") or ""):
                cell.click()
                break
        self.page.wait_for_timeout(400)

    def set_time_range(self, from_time: str, to_time: str):
        self.from_time_input.fill(from_time)
        self.to_time_input.fill(to_time)

    def find_files(self):
        self.find_files_button.click()
        self.page.wait_for_timeout(2000)

    def reset(self):
        self.reset_button.click()
        self.page.wait_for_timeout(800)

    def no_result_message(self) -> str:
        return self.visible_text()

    def has_api_failure_message(self) -> bool:
        return "Unable to load playback files." in self.visible_text()

    def has_no_result_message(self) -> bool:
        return "No playback files found for the selected filters." in self.visible_text()

    def file_card(self, file_number: int) -> Locator:
        label = self.page.get_by_text(f"File #{file_number}", exact=True)
        return label.locator("xpath=ancestor::article[1]")

    def select_file(self, file_number: int):
        # Confirmed live: each file card has its own scoped play_arrow
        # button -- there are multiple unlabeled "play_arrow" buttons on
        # the page, so a page-wide get_by_role("button", name="play_arrow")
        # can hit the wrong one; must be scoped to this specific card.
        self.file_card(file_number).get_by_role("button").first.click()
        self.page.wait_for_timeout(2000)

    def is_file_selected(self, file_number: int) -> bool:
        return "border-l-(--mat-sys-primary)" in (self.file_card(file_number).get_attribute("class") or "")

    def video_element(self) -> Locator:
        return self.page.locator("video").first

    def is_video_playing(self) -> bool:
        return "Playing" in self.visible_text() and self.video_element().count() > 0

    def video_context_text(self) -> str:
        text = self.visible_text()
        idx = text.find("Playback Video")
        return text[idx:idx + 200] if idx != -1 else ""

    def enter_fullscreen(self):
        self.playback_video_heading.locator("xpath=ancestor::*[4]").get_by_role("button").first.click()
        self.page.wait_for_timeout(800)

    def is_fullscreen(self) -> bool:
        return self.page.evaluate("() => !!document.fullscreenElement")
