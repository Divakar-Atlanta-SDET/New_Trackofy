import re
from playwright.sync_api import Page
from Pages.base_page import BasePage
from components.toast_notifcations import ToastNotifications


class TrackingPage(BasePage):
    """Page Object for the Trackofy Tracking Module (/tracking).

    Locators are grounded against the live app (aria-snapshot + raw DOM
    probing), not guessed. Anything that is account data (vehicle names,
    the current selection count, control default values) is read at runtime
    via the helper methods below rather than hardcoded -- the same control
    is shared between the Live and Playback tabs (only one tab's form is
    rendered at a time), so a single locator per control name is enough.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.toast = ToastNotifications(page)

        # Global nav preset bar (shared header, not page-local presets)
        self.map_focus_preset_btn = page.get_by_role("button", name="Map Focus")
        self.playback_view_preset_btn = page.get_by_role("button", name="Playback View")
        self.collapse_bottom_panel_btn = page.get_by_role("button", name="Collapse bottom panel")

        # Bottom Panel Main Tabs
        self.live_tracking_tab = page.get_by_role("button", name="Live Tracking", exact=True)
        self.playback_tracking_tab = page.get_by_role("button", name="Playback Tracking", exact=True)

        # Selected-vehicles counter badge ("Selected Vehicles N /MAX") -- .last
        # sidesteps a transient duplicate node seen during transitions.
        self.selected_vehicles_badge = page.get_by_text("Selected Vehicles").last.locator("xpath=..")

        # Shared Vehicle/Split-Screen controls (one tab's form renders at a time)
        self.split_screen_select = page.get_by_role("combobox", name="Split Screen")
        self.vehicle_select = page.get_by_role("combobox", name="Select Vehicle")
        # Named "Select Vehicle(s)" -- disambiguates from the Split Screen
        # listbox, which can otherwise linger in the DOM and confuse a bare
        # "[role='listbox']").last (confirmed live: caused stale-locator
        # timeouts once Split Screen had been interacted with first).
        self.vehicle_listbox = page.get_by_role("listbox", name=re.compile(r"Select Vehicles?"))
        self.vehicle_search_input = page.get_by_role("textbox", name="Search vehicle")
        # Scoped to the vehicle listbox -- an unscoped page.get_by_role("option")
        # also matches the page footer's native "Language Translate Widget"
        # <select> options, confirmed live (35 real vehicles read back as 44
        # "options" without this scoping).
        self.vehicle_options = self.vehicle_listbox.get_by_role("option")

        # Trail Color / Thickness (native controls, identified by formcontrolname --
        # app structure, not account data). Only exists on Live's base form; on
        # Playback it only renders once More Filters is open.
        self.trail_color_input = page.locator("input[formcontrolname='routeColor']").first
        self.trail_thickness_slider = page.locator("input[formcontrolname='thickness']").first

        self.reset_btn = page.get_by_role("button", name="Reset", exact=True)
        self.start_tracking_btn = page.get_by_role("button", name="Start Tracking", exact=True)

        # Playback-only controls
        self.from_date_input = page.get_by_role("textbox", name="From Date")
        self.to_date_input = page.get_by_role("textbox", name="To Date")
        self.from_time_input = page.get_by_role("textbox", name="From Time")
        self.to_time_input = page.get_by_role("textbox", name="To Time")
        self.open_calendar_btns = page.get_by_role("button", name="Open calendar")
        self.more_filters_btn = page.get_by_role("button", name="More Filters")
        self.hold_time_select = page.get_by_role("combobox", name="Hold Time")
        self.overspeeding_select = page.get_by_role("combobox", name="Overspeeding")
        self.load_playback_btn = page.get_by_role("button", name="Load Playback", exact=True)

        # Map
        self.map_region = page.get_by_role("region", name="Map")
        self.map_tile_btn = page.get_by_role("button", name="Map", exact=True)
        self.hybrid_tile_btn = page.get_by_role("button", name="Hybrid", exact=True)
        self.toggle_fullscreen_btn = page.get_by_role("button", name="Toggle fullscreen view")

    # ---------------------------------------------------------------- nav

    def open_tracking_page(self):
        self.page.goto("/tracking")
        self.wait_for_tracking_page_ready()

    def wait_for_tracking_page_ready(self):
        self.page.wait_for_url(re.compile(r".*/tracking/?$"), timeout=self.DEFAULT_TIMEOUT_MS)
        self.wait_until_ready()
        self.wait_for_visible(self.live_tracking_tab)

    def switch_to_live_tracking(self):
        self.wait_for_visible(self.live_tracking_tab)
        self.live_tracking_tab.click()
        self.wait_for_loading_to_finish()

    def switch_to_playback_tracking(self):
        self.wait_for_visible(self.playback_tracking_tab)
        self.playback_tracking_tab.click()
        self.wait_for_loading_to_finish()

    def toggle_more_filters(self):
        self.wait_for_visible(self.more_filters_btn)
        self.more_filters_btn.click()
        self.wait_for_loading_to_finish()

    # ------------------------------------------------------------ vehicles

    def read_selected_vehicles_counter(self) -> tuple[int, int | None]:
        """Parse the live 'Selected Vehicles N /MAX' badge. MAX is None if
        the badge only ever shows a bare count (e.g. Playback's variant)."""
        text = self.selected_vehicles_badge.inner_text()
        match = re.search(r"(\d+)\s*/\s*(\d+)", text)
        if match:
            return int(match.group(1)), int(match.group(2))
        match = re.search(r"(\d+)", text)
        return (int(match.group(1)), None) if match else (0, None)

    def open_vehicle_dropdown(self):
        if not self.vehicle_listbox.is_visible():
            self.wait_for_visible(self.vehicle_select)
            self.vehicle_select.click()
            self.wait_for_visible(self.vehicle_options.first)
            # The option list re-renders (fresh element ids) briefly after
            # opening -- confirmed live -- so give it a moment to settle
            # before the first click, or that click can hit a stale node.
            self.page.wait_for_timeout(400)

    def close_vehicle_dropdown_if_open(self):
        if self.vehicle_listbox.is_visible():
            self.page.keyboard.press("Escape")
            self.wait_for_loading_to_finish()

    def available_vehicle_count(self) -> int:
        """Open the dropdown, count real vehicle options, close it again."""
        self.open_vehicle_dropdown()
        count = self.vehicle_options.count()
        self.close_vehicle_dropdown_if_open()
        return count

    def _click_vehicle_option(self, index: int) -> str:
        """Click the option at `index`, tolerating the periodic re-render
        the vehicle listbox does on its own (confirmed live -- each row has
        a live "recently active" status indicator) which can otherwise race
        Playwright's multi-step hover-then-click actionability sequence.
        A direct in-page click dispatch sidesteps that race entirely.
        """
        option = self.vehicle_options.nth(index)
        option.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT_MS)
        name = option.inner_text().strip()
        option.evaluate("el => el.click()")
        return name

    def select_vehicle_by_index(self, index: int) -> str:
        """Select the vehicle at `index` in the (single-select, default
        Split Screen = 'No') dropdown -- it closes automatically after the
        pick. Returns the selected vehicle's displayed identifier."""
        self.open_vehicle_dropdown()
        name = self._click_vehicle_option(index)
        self.wait_for_loading_to_finish()
        self.close_vehicle_dropdown_if_open()
        return name

    def select_n_vehicles(self, n: int) -> list[str]:
        """Select the first n distinct vehicles offered by the live dropdown.

        Confirmed live: with the default Split Screen = 'No' the picker is
        single-select (each pick replaces the prior one and closes the
        dropdown) -- selecting more than one vehicle only works once Split
        Screen is 'Yes', which turns it into a real multi-select that stays
        open across picks. n<=1 leaves Split Screen untouched.
        """
        if n <= 1:
            return [self.select_vehicle_by_index(0)] if n == 1 else []

        self.select_split_screen("Yes")
        self.open_vehicle_dropdown()
        names = []
        for i in range(n):
            names.append(self._click_vehicle_option(i))
            self.page.wait_for_timeout(600)
        self.close_vehicle_dropdown_if_open()
        self.wait_for_loading_to_finish()
        return names

    def attempt_select_one_more_vehicle(self, already_selected: int) -> bool:
        """Try to select the vehicle right after however many are already
        picked (multi-select / Split Screen='Yes' mode selects by index in
        order and confirmed live not to reorder selected rows, so the next
        unselected option is simply at `already_selected`).
        Returns True if the click was made, False if there was no such
        option to click or it couldn't be interacted with in time."""
        self.open_vehicle_dropdown()
        if already_selected >= self.vehicle_options.count():
            self.close_vehicle_dropdown_if_open()
            return False
        try:
            self.vehicle_options.nth(already_selected).wait_for(state="visible", timeout=5000)
        except Exception:
            self.close_vehicle_dropdown_if_open()
            return False
        self._click_vehicle_option(already_selected)
        self.wait_for_loading_to_finish()
        self.close_vehicle_dropdown_if_open()
        return True

    # ----------------------------------------------------------- controls

    def select_split_screen(self, option_text: str):
        self.wait_for_visible(self.split_screen_select)
        self.split_screen_select.click()
        listbox = self.page.get_by_role("listbox", name="Split Screen")
        option = listbox.get_by_role("option", name=option_text, exact=True)
        self.wait_for_visible(option)
        option.click()
        self.wait_for_loading_to_finish()

    def read_trail_color(self) -> str:
        return self.trail_color_input.input_value()

    def set_trail_color(self, hex_value: str):
        self.trail_color_input.evaluate(
            "(el, value) => { el.value = value; el.dispatchEvent(new Event('input', {bubbles: true})); "
            "el.dispatchEvent(new Event('change', {bubbles: true})); }",
            hex_value,
        )

    def read_thickness_bounds(self) -> tuple[int, int]:
        slider = self.trail_thickness_slider
        return int(slider.get_attribute("min")), int(slider.get_attribute("max"))

    def read_thickness_value(self) -> int:
        return int(self.trail_thickness_slider.get_attribute("aria-valuetext"))

    def set_thickness(self, value: int):
        # The native range input sits visually hidden under Material's custom
        # slider UI (confirmed live), so .fill() fails Playwright's visibility
        # check -- set the value via JS and dispatch the events Angular listens for.
        self.trail_thickness_slider.evaluate(
            "(el, value) => { "
            "const proto = Object.getPrototypeOf(el); "
            "Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, String(value)); "
            "el.dispatchEvent(new Event('input', {bubbles: true})); "
            "el.dispatchEvent(new Event('change', {bubbles: true})); }",
            value,
        )

    def set_date_input(self, locator, value: str):
        """Angular Material datepicker input -- remove readonly first, same
        trick used for the Unit module's date fields."""
        locator.evaluate("el => el.removeAttribute('readonly')")
        locator.focus()
        locator.fill(value)
        locator.press("Tab")
        self.page.wait_for_timeout(300)

    def select_hold_time(self, option_text: str):
        self.wait_for_visible(self.hold_time_select)
        self.hold_time_select.click()
        listbox = self.page.get_by_role("listbox", name="Hold Time")
        option = listbox.get_by_role("option", name=option_text, exact=True)
        self.wait_for_visible(option)
        option.click()
        self.wait_for_loading_to_finish()

    def select_overspeeding(self, option_text: str):
        self.wait_for_visible(self.overspeeding_select)
        self.overspeeding_select.click()
        listbox = self.page.get_by_role("listbox", name="Overspeeding")
        option = listbox.get_by_role("option", name=option_text, exact=True)
        self.wait_for_visible(option)
        option.click()
        self.wait_for_loading_to_finish()

    # -------------------------------------------------------------- flows

    def start_live_tracking_flow(self) -> str:
        vehicle_name = self.select_vehicle_by_index(0)
        self.wait_for_visible(self.start_tracking_btn)
        self.start_tracking_btn.click()
        self.wait_for_loading_to_finish()
        return vehicle_name

    def load_playback_flow(self) -> str:
        vehicle_name = self.select_vehicle_by_index(0)
        if self.load_playback_btn.is_enabled():
            self.load_playback_btn.click()
            self.wait_for_loading_to_finish()
        return vehicle_name

    def vehicle_marker_on_map(self, vehicle_name: str):
        return self.page.get_by_role("button", name=vehicle_name, exact=True)
