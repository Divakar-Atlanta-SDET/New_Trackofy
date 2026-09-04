import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage
from components.calendar import Calendar


class DriverPage(SettingsListPage):
    """Driver list + Create/Update Driver dialog + Assign Unit dialog.
    Confirmed live against /settings/driver.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Add Driver", export_entity_name="drivers")

        # Create/Update Driver dialog (same dialog, pre-filled when editing)
        self.driver_dialog = page.get_by_role("dialog").filter(has=page.get_by_role("button", name=re.compile("Close driver dialog")))
        self.name_input = page.get_by_role("textbox", name="Name", exact=True)
        self.mobile_input = page.get_by_role("textbox", name="Mobile No")
        self.email_input = page.get_by_role("textbox", name="Email", exact=True)
        self.dob_input = page.get_by_role("textbox", name="Date of Birth")
        self.dob_calendar = Calendar(page, page.get_by_role("button", name="Open calendar").nth(0))
        self.emergency_contact_input = page.get_by_role("textbox", name="Emergency Contact")

        self.dl_number_input = page.get_by_role("textbox", name="DL Number")
        self.dl_issue_date_input = page.get_by_role("textbox", name="DL Issue Date")
        self.dl_issue_calendar = Calendar(page, page.get_by_role("button", name="Open calendar").nth(1))
        self.dl_expiry_date_input = page.get_by_role("textbox", name="DL Expiry Date")
        self.dl_expiry_calendar = Calendar(page, page.get_by_role("button", name="Open calendar").nth(2))
        self.upload_licence_btn = page.get_by_role("button", name="Upload Driving Licence")
        self.remove_licence_file_btn = page.get_by_role("button", name=re.compile("Remove.*licence file|Remove selected file"))

        self.address_input = page.get_by_role("textbox", name="Address", exact=True)

        self.cancel_btn = self.driver_dialog.get_by_role("button", name="Cancel")
        self.create_driver_btn = self.driver_dialog.get_by_role("button", name="Create Driver")
        self.update_driver_btn = self.driver_dialog.get_by_role("button", name="Update Driver")

        # Assign Unit dialog
        self.assignment_dialog = page.get_by_role("dialog").filter(has=page.get_by_role("heading", name="Driver Assignment"))
        self.assignment_vehicle_select = page.get_by_role("combobox", name="Select Vehicle")
        self.unassign_vehicle_btn = page.get_by_role("button", name="Unassign current vehicle")
        # Confirmed live: the submit button is named "Assign Vehicle" for a
        # driver's first-ever assignment, and "Update Assignment" once one
        # already exists -- same dialog, different button text by state.
        self.assign_vehicle_btn = self.assignment_dialog.get_by_role("button", name="Assign Vehicle")
        self.update_assignment_btn = self.assignment_dialog.get_by_role("button", name="Update Assignment")

    # ------------------------------------------------------------- rows

    def edit_button(self, driver_name: str):
        return self.row_containing(driver_name).get_by_role("button", name="Edit driver")

    def delete_button(self, driver_name: str):
        return self.row_containing(driver_name).get_by_role("button", name="Delete driver")

    def assign_unit_button(self, driver_name: str):
        return self.row_containing(driver_name).get_by_role("button", name="Assign or unassign unit")

    # ------------------------------------------------------------ flows

    def open_add_driver_form(self):
        self.add_btn.click()
        self.wait_for_visible(self.name_input)

    def open_edit_driver_form(self, driver_name: str):
        self.edit_button(driver_name).click()
        self.wait_for_visible(self.name_input)

    def fill_personal_info(self, name: str, mobile: str, email: str, dob: str, emergency_contact: str = ""):
        self.name_input.fill(name)
        self.mobile_input.fill(mobile)
        self.email_input.fill(email)
        self.set_dialog_date(self.dob_input, dob)
        if emergency_contact:
            self.emergency_contact_input.fill(emergency_contact)

    def fill_licence_info(self, dl_number: str, issue_date: str, expiry_date: str):
        self.dl_number_input.fill(dl_number)
        self.set_dialog_date(self.dl_issue_date_input, issue_date)
        self.set_dialog_date(self.dl_expiry_date_input, expiry_date)

    def set_dialog_date(self, locator, value: str):
        """Angular Material datepicker input inside a dialog -- remove
        readonly first, same trick proven on the Unit/Tracking modules."""
        locator.evaluate("el => el.removeAttribute('readonly')")
        locator.focus()
        locator.fill(value)
        locator.press("Tab")
        self.page.wait_for_timeout(300)

    def upload_licence_file(self, file_path: str):
        file_input = self.driver_dialog.locator("input[type='file']").first
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(500)

    def close_driver_dialog(self):
        if self.driver_dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()

    def _submit_assignment_if_needed(self):
        """The submit button reads "Assign Vehicle" for a driver's first-ever
        assignment and "Update Assignment" once one already exists (same
        dialog, confirmed live) -- click whichever is present. Retries the
        click a couple of times: the same dialog-open-animation timing issue
        found on Driver Performance's delete confirm showed up here too
        (an immediate click can land before the dialog settles and no-op)."""
        self.page.wait_for_timeout(500)
        for _ in range(3):
            if not self.assignment_dialog.is_visible():
                return
            btn = self.assign_vehicle_btn if self.assign_vehicle_btn.count() else self.update_assignment_btn
            if btn.count():
                btn.click()
            try:
                self.assignment_dialog.wait_for(state="hidden", timeout=5000)
                return
            except Exception:
                self.page.wait_for_timeout(800)
        self.assignment_dialog.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def assign_vehicle(self, driver_name: str, vehicle_name: str):
        """Assign a vehicle to a driver (first-time or reassignment)."""
        self.assign_unit_button(driver_name).click()
        self.wait_for_visible(self.assignment_vehicle_select)
        self.assignment_vehicle_select.click()
        self.page.get_by_role("option", name=vehicle_name, exact=True).click()
        self._submit_assignment_if_needed()

    change_assigned_vehicle = assign_vehicle

    def unassign_vehicle(self, driver_name: str):
        self.assign_unit_button(driver_name).click()
        self.wait_for_visible(self.unassign_vehicle_btn)
        self.unassign_vehicle_btn.click()
        self.update_assignment_btn.click()
        self.assignment_dialog.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def delete_driver(self, driver_name: str):
        self.delete_button(driver_name).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        # The dialog can close slightly before the row is actually removed
        # from the table (confirmed live -- a reload right after sometimes
        # still showed it), so wait for the row itself to be gone too.
        self.row_containing(driver_name).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
