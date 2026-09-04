from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage


class LocationControlPage(SettingsListPage):
    """Location Control list + Add/Update Location dialog + Assign Unit dialog.
    Confirmed live against Settings > Vehicle Management > Location Control.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Add Location")

        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("button", name="Close location form")
        )
        self.location_input = self.dialog.get_by_role("textbox", name="Location")
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")
        self.create_btn = self.dialog.get_by_role("button", name="Create Location")
        self.update_btn = self.dialog.get_by_role("button", name="Update Location")

        # Row action buttons have no accessible name (confirmed live) but do
        # carry a real mattooltip attribute -- same pattern used elsewhere
        # in this codebase (e.g. unit_settings_page.py's calibration rows).
        self.assign_unit_dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name="Location Unit Assignment")
        )
        self.assign_vehicles_select = self.assign_unit_dialog.get_by_role("combobox", name="Select Vehicles")
        self.assign_vehicles_listbox = page.get_by_role("listbox", name="Select Vehicles")
        self.assign_vehicle_options = self.assign_vehicles_listbox.get_by_role("option")
        self.assign_units_btn = self.assign_unit_dialog.get_by_role("button", name="Assign Units")

    def open_add_location_form(self):
        self.add_btn.click()
        self.wait_for_visible(self.location_input)

    def edit_button(self, location_name: str):
        return self.row_containing(location_name).locator("button[mattooltip='Edit location']")

    def delete_button(self, location_name: str):
        return self.row_containing(location_name).locator("button[mattooltip='Delete location']")

    def assign_unit_button(self, location_name: str):
        return self.row_containing(location_name).locator("button[mattooltip='Assign units to location']")

    def open_edit_location_form(self, location_name: str):
        self.edit_button(location_name).click()
        self.wait_for_visible(self.location_input)
        self.page.wait_for_timeout(500)  # dialogs on this app can populate async

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()

    def delete_location(self, location_name: str):
        """Deletes rows matching `location_name` one at a time -- the app does
        not enforce name uniqueness (confirmed live, see SET-085), so more
        than one row can match; loop rather than assume a single match."""
        # A lingering toast or an unclosed dialog's overlay backdrop can
        # intercept the click (confirmed live) -- clear both before deleting
        # rather than assuming the caller left the page in a clean state.
        for toast in (self.toast.success_toast, self.toast.error_toast, self.toast.warning_toast, self.toast.info_toast):
            if toast.is_visible():
                toast.locator("mat-icon", has_text="close").click()
        backdrop = self.page.locator("div.cdk-overlay-backdrop-showing")
        if backdrop.count() > 0:
            # Escape alone doesn't reliably dismiss every overlay this app
            # can leave open (confirmed live) -- a reload is the reliable
            # way back to a clean state, same fallback used elsewhere in
            # this page's search-clearing method.
            self.page.reload()
            self.wait_for_loading_to_finish()
            self.wait_for_visible(self.heading)
        while self.row_containing(location_name).count() > 0:
            self.delete_button(location_name).first.click()
            self.wait_for_visible(self.confirm_delete_btn)
            self.page.wait_for_timeout(400)  # let the confirm dialog's open animation settle
            self.confirm_delete_btn.click()
            self.wait_for_dialog_closed()
            self.page.wait_for_timeout(300)

    def open_assign_unit_dialog(self, location_name: str):
        self.assign_unit_button(location_name).click()
        self.wait_for_visible(self.assign_vehicles_select)

    def assign_units(self, location_name: str, count: int) -> list[str]:
        """Assign `count` distinct units to a location. Confirmed live this
        picker is a real multi-select that stays open across picks (same
        pattern as Vehicle Group's Select Units)."""
        self.open_assign_unit_dialog(location_name)
        self.assign_vehicles_select.click()
        self.wait_for_visible(self.assign_vehicle_options.first)
        names = []
        for i in range(count):
            option = self.assign_vehicle_options.nth(i)
            option.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT_MS)
            names.append(option.inner_text().strip())
            option.click()
            self.page.wait_for_timeout(300)
        if self.assign_vehicles_listbox.is_visible():
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)
        self.assign_units_btn.click()
        self.assign_unit_dialog.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
        return names
