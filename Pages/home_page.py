import re

from playwright.sync_api import Page


class HomePage:
    """Page object for the authenticated Trackofy Home tab."""

    def __init__(self, page: Page, config):
        self.page = page
        self.config = config

        self.home_tab = page.get_by_text("Home", exact=True).first
        self.home_content = page.locator("main")
        self.map_region = page.get_by_role("region", name="Map")
        self.fleet_tab = page.get_by_role("button", name="Fleet", exact=True)
        self.vehicle_checkboxes = page.locator("input[type='checkbox'][aria-label^='Actively track ']")
        self.active_tracking_summary = page.get_by_text(
            re.compile(r"Actively tracking \d+ vehicle", re.IGNORECASE)
        )
        self.clear_tracking_button = page.get_by_role("button", name="Clear")
        self.loading_indicator = page.get_by_text(
            re.compile(r"^(loading|please wait)\b", re.IGNORECASE)
        )
        self.application_error = page.get_by_text(
            re.compile(
                r"(something went wrong|http failure|unauthorized|internal server error)",
                re.IGNORECASE,
            )
        )

    def open(self):
        self.page.goto(f"{self.config['base_url']}/home")

    def vehicle_checkbox(self, vehicle_id: str):
        return self.page.locator(
            f"input[type='checkbox'][aria-label='Actively track {vehicle_id}']"
        )

    def map_vehicle_marker(self, vehicle_id: str):
        return self.page.locator(
            f"[role='button'][title='{vehicle_id}'], [role='button'][aria-label='{vehicle_id}']"
        ).first

    def selected_vehicle_map_label(self, vehicle_id: str):
        return self.page.locator(
            ".trackofy-vehicle-marker-label-selected",
            has_text=vehicle_id,
        )

    def map_info_window_vehicle(self, vehicle_id: str):
        return self.page.locator(".trackofy-vehicle-iw", has_text=vehicle_id)

    def get_first_vehicle_id(self):
        aria_label = self.vehicle_checkboxes.first.get_attribute("aria-label")
        return aria_label.replace("Actively track ", "")

    def get_total_fleet_count(self):
        total_fleet_card = self.page.locator("div", has_text="Total Fleet").first
        total_text = total_fleet_card.inner_text()
        match = re.search(r"Total Fleet\s*(\d+)", total_text)
        return int(match.group(1))

    def get_active_devices_count(self):
        active_devices_card = self.page.get_by_role(
            "button", name=re.compile(r"Active Devices\s+\d+")
        )
        active_devices_text = active_devices_card.inner_text()
        match = re.search(r"Active Devices\s*(\d+)", active_devices_text)
        return int(match.group(1))

    def get_active_vehicle_filter_count(self):
        active_filter_text = self.page.get_by_role(
            "button", name=re.compile(r"Active \(\d+\)")
        ).inner_text()
        match = re.search(r"\((\d+)\)", active_filter_text)
        return int(match.group(1))

    def get_side_menu_vehicle_count(self):
        pagination_text = self.page.get_by_text(
            re.compile(r"Showing \d+ - \d+ of \d+ vehicles")
        ).inner_text()
        match = re.search(r"of\s+(\d+)\s+vehicles", pagination_text)
        return int(match.group(1))

    def get_visible_vehicle_checkbox_count(self):
        return self.vehicle_checkboxes.count()
