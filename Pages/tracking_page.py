import re
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage


class TrackingPage(BasePage):
    """Page Object for the Trackofy Tracking Module (/tracking)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Header / Navigation
        self.tracking_nav_link = page.locator("a[href*='/tracking'], link[name*='Tracking']").first
        self.page_heading = page.locator("h1, header h1, title").first

        # Preset View Controls (Bottom Right / View Presets Bar)
        self.map_focus_preset_btn = page.get_by_role("button", name=re.compile(r"Map Focus", re.I)).first
        self.playback_view_preset_btn = page.get_by_role("button", name=re.compile(r"Playback View", re.I)).first
        self.collapse_bottom_panel_btn = page.get_by_role("button", name=re.compile(r"Collapse bottom panel", re.I)).first

        # Bottom Panel Main Tabs
        self.live_tracking_tab = page.get_by_role("button", name=re.compile(r"Live Tracking", re.I)).first
        self.playback_tracking_tab = page.get_by_role("button", name=re.compile(r"Playback Tracking", re.I)).first

        # Vehicle Counter Badge
        self.selected_vehicles_counter = page.locator("text='Selected Vehicles', text='No vehicles selected'").last

        # Live Tracking Form Controls
        self.live_split_screen_select = page.get_by_role("combobox", name=re.compile(r"Split Screen", re.I)).first
        self.live_vehicle_select = page.get_by_role("combobox", name=re.compile(r"Select Vehicle", re.I)).first
        self.live_trail_color_input = page.get_by_text("Color").first
        self.live_trail_thickness_slider = page.get_by_role("slider").first
        self.live_reset_btn = page.get_by_role("button", name=re.compile(r"Reset", re.I)).first
        self.start_tracking_btn = page.get_by_role("button", name=re.compile(r"Start Tracking", re.I)).first

        # Playback Tracking Form Controls
        self.playback_split_screen_select = page.get_by_role("combobox", name=re.compile(r"Split Screen", re.I)).first
        self.playback_vehicle_select = page.get_by_role("combobox", name=re.compile(r"Select Vehicle", re.I)).first
        self.from_date_input = page.get_by_role("textbox", name=re.compile(r"From Date", re.I)).first
        self.from_date_calendar_btn = page.get_by_role("button", name=re.compile(r"Open calendar", re.I)).first
        self.from_time_input = page.get_by_role("textbox", name=re.compile(r"From Time", re.I)).first
        self.to_date_input = page.get_by_role("textbox", name=re.compile(r"To Date", re.I)).first
        self.to_date_calendar_btn = page.get_by_role("button", name=re.compile(r"Open calendar", re.I)).last
        self.to_time_input = page.get_by_role("textbox", name=re.compile(r"To Time", re.I)).first

        # Playback More Filters Section
        self.more_filters_btn = page.get_by_role("button", name=re.compile(r"More Filters", re.I)).first
        self.hold_time_select = page.get_by_role("combobox", name=re.compile(r"Hold Time", re.I)).first
        self.overspeeding_select = page.get_by_role("combobox", name=re.compile(r"Overspeeding", re.I)).first
        self.playback_trail_color_input = page.get_by_text("Color").last
        self.playback_trail_thickness_slider = page.get_by_role("slider").last

        # Playback Action Buttons
        self.load_playback_btn = page.get_by_role("button", name=re.compile(r"Load Playback", re.I)).first
        self.playback_reset_btn = page.get_by_role("button", name=re.compile(r"Reset", re.I)).last

        # Map Canvas & Elements
        self.map_container = page.get_by_role("button", name=re.compile(r"(Live Tracking|Playback Tracking|Map|Hybrid)", re.I)).first
        self.map_tile_btn = page.get_by_role("button", name=re.compile(r"^Map$", re.I)).first
        self.hybrid_tile_btn = page.get_by_role("button", name=re.compile(r"^Hybrid$", re.I)).first
        self.map_selected_vehicle_pill = page.locator("text=/Selected:/i").first

        # Toast Container
        self.toast_container = page.locator(".toast-container, .ngx-toastr, mat-snack-bar-container, [role='alert'], [class*='toast']").first

    def open_tracking_page(self):
        """Navigate directly to the Tracking module (/tracking)."""
        self.page.goto("/tracking")
        self.wait_for_tracking_page_ready()

    def wait_for_tracking_page_ready(self):
        """Wait until Tracking page is loaded."""
        self.page.wait_for_url(re.compile(r".*/tracking/?$"), timeout=15000)
        self.wait_until_ready()
        self.wait_for_visible(self.live_tracking_tab)

    def switch_to_live_tracking(self):
        """Switch to Live Tracking tab."""
        self.wait_for_visible(self.live_tracking_tab)
        self.live_tracking_tab.click()
        self.wait_for_loading_to_finish()

    def switch_to_playback_tracking(self):
        """Switch to Playback Tracking tab."""
        self.wait_for_visible(self.playback_tracking_tab)
        self.playback_tracking_tab.click()
        self.wait_for_loading_to_finish()

    def toggle_more_filters(self):
        """Toggle the More Filters expand/collapse section in Playback."""
        self.wait_for_visible(self.more_filters_btn)
        self.more_filters_btn.click()
        self.wait_for_loading_to_finish()

    def select_first_available_vehicle(self) -> str:
        """Open vehicle dropdown and select the first available vehicle."""
        self.switch_to_live_tracking()
        self.wait_for_visible(self.live_vehicle_select)
        self.live_vehicle_select.click()
        first_option = self.page.get_by_role("option").first
        self.wait_for_visible(first_option)
        vehicle_name = first_option.inner_text().strip()
        first_option.click()
        self.wait_for_loading_to_finish()
        return vehicle_name

    def select_first_available_playback_vehicle(self) -> str:
        """Open Playback vehicle dropdown and select the first available vehicle."""
        self.switch_to_playback_tracking()
        self.wait_for_visible(self.playback_vehicle_select)
        self.playback_vehicle_select.click()
        first_option = self.page.get_by_role("option").first
        self.wait_for_visible(first_option)
        vehicle_name = first_option.inner_text().strip()
        first_option.click()
        self.wait_for_loading_to_finish()
        return vehicle_name

    def select_split_screen_option(self, option_text: str):
        """Select a split screen option."""
        self.wait_for_visible(self.live_split_screen_select)
        self.live_split_screen_select.click()
        opt = self.page.get_by_role("option", name=re.compile(option_text, re.I)).first
        if opt.is_visible():
            opt.click()
        self.wait_for_loading_to_finish()

    def start_live_tracking_flow(self) -> str:
        """Perform full live tracking flow: select vehicle and click Start Tracking."""
        vehicle_name = self.select_first_available_vehicle()
        self.wait_for_visible(self.start_tracking_btn)
        self.start_tracking_btn.click()
        self.wait_for_loading_to_finish()
        return vehicle_name

    def load_playback_flow(self) -> str:
        """Perform full playback flow: select vehicle and click Load Playback."""
        vehicle_name = self.select_first_available_playback_vehicle()
        if self.load_playback_btn.is_enabled():
            self.load_playback_btn.click()
            self.wait_for_loading_to_finish()
        return vehicle_name

    def select_preset_map_focus(self):
        """Click the Map Focus preset button."""
        if self.map_focus_preset_btn.is_visible():
            self.map_focus_preset_btn.click()
            self.wait_for_loading_to_finish()

    def select_preset_playback_view(self):
        """Click the Playback View preset button."""
        if self.playback_view_preset_btn.is_visible():
            self.playback_view_preset_btn.click()
            self.wait_for_loading_to_finish()

    def expect_toast_notification(self, text_pattern: str = None):
        """Assert success or status toast message appears."""
        if text_pattern:
            toast = self.page.locator(".toast-container, .ngx-toastr, mat-snack-bar-container, [role='alert'], [class*='toast']").filter(has_text=re.compile(text_pattern, re.I)).first
        else:
            toast = self.toast_container
        self.wait_for_visible(toast)
