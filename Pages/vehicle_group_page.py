import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage


class VehicleGroupPage(SettingsListPage):
    """Vehicle Group list + Create/Update Unit Group dialog.
    Confirmed live against Settings > Vehicle Management > Vehicle Group.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="New Unit Group", export_entity_name="unit groups")

        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("button", name="Close unit group form")
        )
        self.group_name_input = self.dialog.get_by_role("textbox", name="Unit Group Name")
        self.units_select = self.dialog.get_by_role("combobox", name="Select Units")
        self.units_listbox = page.get_by_role("listbox", name="Select Units")
        self.unit_options = self.units_listbox.get_by_role("option")
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")
        self.create_group_btn = self.dialog.get_by_role("button", name="Create Group")
        self.update_group_btn = self.dialog.get_by_role("button", name="Update Group")

    def open_add_group_form(self):
        self.add_btn.click()
        self.wait_for_visible(self.group_name_input)

    def edit_button(self, group_name: str):
        return self.row_containing(group_name).get_by_role("button", name="Edit unit group")

    def delete_button(self, group_name: str):
        return self.row_containing(group_name).get_by_role("button", name="Delete unit group")

    def view_button(self, group_name: str):
        return self.row_containing(group_name).get_by_role("button", name="View assigned vehicles")

    def open_edit_group_form(self, group_name: str):
        self.edit_button(group_name).click()
        self.wait_for_visible(self.group_name_input)
        # Confirmed live: the dialog renders before the group's existing
        # name/units are populated into it -- reading/filling immediately
        # caught a still-blank name field (which then made the button look
        # disabled). Give the async populate a moment to land.
        self.page.wait_for_timeout(1000)

    def open_units_dropdown(self):
        if not self.units_listbox.is_visible():
            self.units_select.click()
            self.wait_for_visible(self.unit_options.first)

    def select_units(self, count: int) -> list[str]:
        """Select the first `count` distinct units -- confirmed live this is
        a real multi-select that stays open across picks (unlike Tracking's
        default single-select vehicle picker)."""
        self.open_units_dropdown()
        names = []
        for i in range(count):
            option = self.unit_options.nth(i)
            option.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT_MS)
            names.append(option.inner_text().strip())
            option.click()
            self.page.wait_for_timeout(300)
        if self.units_listbox.is_visible():
            self.page.keyboard.press("Escape")
        return names

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()

    def delete_group(self, group_name: str):
        self.delete_button(group_name).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.page.wait_for_timeout(400)  # let the confirm dialog's open animation settle
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        self.row_containing(group_name).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
