import re

from playwright.sync_api import Locator, Page

from Pages.video_telematics_page import VideoTelematicsBasePage


class VideoTelematicsAlertPage(VideoTelematicsBasePage):
    """Video Telematics > Alert (/video_telematics/alert) -- the Alert
    Configuration list, its filters/search/pagination, and the Create/
    Edit Video Alert dialog.
    """

    DELIVERY_CHANNELS = ["Application", "Email", "WhatsApp"]
    PRIORITIES = ["Critical", "Warning", "Moderate"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_text("Alert Configuration", exact=True)
        # Confirmed live: these two comboboxes' accessible names aren't
        # exactly "Vehicle"/"Priority" (extra whitespace/adjacent text
        # folded in by the browser's name computation) -- substring
        # match works, exact=True does not.
        self.vehicle_filter = page.get_by_role("combobox", name="Vehicle")
        self.priority_filter = page.get_by_role("combobox", name="Priority")
        self.search_input = page.get_by_placeholder("Search alerts...")
        self.add_alert_button = page.get_by_role("button", name="Add Alert")
        self.rows_per_page_select = page.get_by_label("Rows per page")
        self.next_page_button = page.get_by_role("button", name="Next page")
        self.previous_page_button = page.get_by_role("button", name="Previous page")
        self.first_page_button = page.get_by_role("button", name="First page")
        self.last_page_button = page.get_by_role("button", name="Last page")
        self.table = page.get_by_role("table")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/video_telematics/alert")
        self.expect_path("/video_telematics/alert")
        self.wait_for_visible(self.heading)

    def alert_count(self) -> int:
        match = re.search(r"(\d+)\s*alert", self.visible_text())
        return int(match.group(1)) if match else -1

    def rows(self) -> Locator:
        return self.table.locator("tbody tr").filter(has_not_text=re.compile(r"no .*(found|records)", re.I))

    def row(self, alert_name: str) -> Locator:
        return self.rows().filter(has_text=alert_name)

    def row_category(self, row: Locator) -> str:
        return row.locator("td").nth(1).inner_text().strip()

    def row_vehicle_text(self, row: Locator) -> str:
        return row.locator("td").nth(2).inner_text().strip()

    def row_alert_name(self, row: Locator) -> str:
        return row.locator("td").nth(3).inner_text().strip()

    def row_priority_text(self, row: Locator) -> str:
        return row.locator("td").nth(4).inner_text().strip()

    def row_whatsapp(self, row: Locator) -> str:
        return row.locator("td").nth(5).inner_text().strip()

    def row_email(self, row: Locator) -> str:
        return row.locator("td").nth(6).inner_text().strip()

    def row_delivery(self, row: Locator) -> str:
        return row.locator("td").nth(7).inner_text().strip()

    def row_status(self, row: Locator) -> str:
        return row.locator("td").nth(8).inner_text().strip()

    def row_edit_button(self, row: Locator) -> Locator:
        return row.get_by_role("button", name="edit")

    def row_delete_button(self, row: Locator) -> Locator:
        return row.get_by_role("button", name="delete")

    def search(self, query: str):
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def clear_search(self):
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def _open_option_panel(self, combobox: Locator) -> Locator:
        # Confirmed live: page-wide get_by_role("option") also matches
        # unrelated open panels (rows-per-page, language selector) --
        # scope strictly to this combobox's own listbox panel via its
        # aria-controls id.
        combobox.click()
        self.page.wait_for_timeout(500)
        panel_id = combobox.get_attribute("aria-controls")
        return self.page.locator(f"#{panel_id}")

    def select_vehicle_filter(self, vehicle: str):
        # Confirmed live (Bug #40, Bug_Report.md): this is a multi-select
        # that starts with EVERY vehicle already aria-selected="true"
        # ("All vehicles" is just the display label for "all selected"),
        # so a plain click on the target vehicle toggles it OFF instead
        # of isolating it. To genuinely filter to just one vehicle,
        # deselect every other currently-selected option first.
        panel = self._open_option_panel(self.vehicle_filter)
        options = panel.get_by_role("option")
        select_all = vehicle == "All vehicles"
        for i in range(options.count()):
            option = options.nth(i)
            is_target = select_all or vehicle in option.inner_text()
            is_selected = option.get_attribute("aria-selected") == "true"
            if is_target and not is_selected:
                option.click()
                self.page.wait_for_timeout(300)
            elif not is_target and is_selected:
                option.click()
                self.page.wait_for_timeout(300)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(800)

    def select_priority_filter(self, priority: str):
        # Confirmed live: the reset-to-default option's own text is just
        # "All" (prefixed with a decorative icon ligature), not "All
        # priorities" -- that's only the combobox's own displayed value
        # once selected, not the option label in the open list.
        option_name = "All" if priority == "All priorities" else priority
        panel = self._open_option_panel(self.priority_filter)
        panel.get_by_role("option", name=option_name, exact=True).click()
        self.page.wait_for_timeout(800)

    # ------------------------------------------------------------- Create/Edit dialog

    def open_create_dialog(self):
        self.add_alert_button.click()
        self.wait_for_visible(self.create_dialog())

    def create_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text="Create Video Alert")

    def edit_dialog(self) -> Locator:
        # Confirmed live: this dialog's real title is "Update Video
        # Alert", not "Edit Video Alert" (only the row action icon/label
        # is "edit" -- the dialog itself says "Update").
        return self.page.locator(".cdk-overlay-container").filter(has_text=re.compile("Update Video Alert", re.I))

    def open_edit_dialog(self, row: Locator):
        self.row_edit_button(row).click()
        self.wait_for_visible(self.edit_dialog())

    def vehicle_combobox(self, dialog: Locator) -> Locator:
        return dialog.get_by_role("combobox", name="Select Vehicles")

    def alert_combobox(self, dialog: Locator) -> Locator:
        return dialog.get_by_role("combobox", name="Alerts")

    def priority_combobox(self, dialog: Locator) -> Locator:
        return dialog.get_by_role("combobox", name="Priority")

    def open_vehicle_dropdown(self, dialog: Locator):
        self.vehicle_combobox(dialog).click()
        self.page.wait_for_timeout(400)

    def close_vehicle_dropdown(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def toggle_vehicle(self, vehicle_id: str):
        """Click a vehicle option in the already-open dropdown -- unlike
        the buggy list filter (Bug #40), this multi-select starts with
        nothing selected, so a plain click here correctly toggles the
        one option on/off."""
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()
        self.page.wait_for_timeout(300)

    def select_vehicle(self, dialog: Locator, vehicle_id: str):
        self.open_vehicle_dropdown(dialog)
        self.toggle_vehicle(vehicle_id)
        self.close_vehicle_dropdown()

    def select_alert(self, dialog: Locator, alert_name: str):
        self.alert_combobox(dialog).click()
        self.page.wait_for_timeout(400)
        self.page.get_by_role("option", name=alert_name, exact=True).click()
        # Confirmed live: even for this single-select combobox, the
        # overlay backdrop can briefly outlive the option click and
        # intercept the next real click (e.g. Cancel) -- Escape clears
        # it defensively regardless of whether the panel already closed.
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def select_priority(self, dialog: Locator, priority: str):
        self.priority_combobox(dialog).click()
        self.page.wait_for_timeout(400)
        self.page.get_by_role("option", name=priority, exact=True).click()
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def channel_checkbox(self, dialog: Locator, channel: str) -> Locator:
        return dialog.get_by_role("checkbox", name=channel, exact=True)

    def delivery_mode_radio(self, dialog: Locator, mode: str) -> Locator:
        # mode: "Real time" or "Interval"
        return dialog.get_by_role("radio", name=mode, exact=True)

    def cooldown_input(self, dialog: Locator) -> Locator:
        return dialog.get_by_label("Cooldown Minutes")

    def status_checkbox(self, dialog: Locator) -> Locator:
        return dialog.get_by_role("checkbox", name="Enabled", exact=True)

    def submit_create(self, dialog: Locator):
        dialog.get_by_role("button", name="Create Alert").click()

    def submit_update(self, dialog: Locator):
        dialog.get_by_role("button", name=re.compile("Update|Save", re.I)).click()

    def cancel_dialog(self, dialog: Locator):
        dialog.get_by_role("button", name="Cancel", exact=True).click()

    def close_dialog_via_x(self, dialog: Locator):
        dialog.get_by_role("button", name="Close", exact=True).click()

    def fill_valid_alert(
        self, dialog: Locator, vehicle_id: str | None = None,
        alert_name: str = "Forward Collision Alarm Level Two Start",
        priority: str = "Critical",
    ):
        if vehicle_id is None:
            self.vehicle_combobox(dialog).click()
            self.page.wait_for_timeout(400)
            vehicle_id = self.page.get_by_role("option").first.inner_text()
            self.page.get_by_role("option", name=vehicle_id, exact=True).click()
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        else:
            self.select_vehicle(dialog, vehicle_id)
        self.select_alert(dialog, alert_name)
        self.select_priority(dialog, priority)

    # ------------------------------------------------------------- Delete

    def delete_confirm_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text=re.compile("delete", re.I))

    def delete_alert(self, row: Locator):
        self.row_delete_button(row).click()
        self.wait_for_visible(self.delete_confirm_dialog())
        self.delete_confirm_dialog().get_by_role("button", name="Delete", exact=True).click()
        self.page.wait_for_timeout(1000)
