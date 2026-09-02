import re
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage
from components.toast_notifcations import ToastNotifications


class UnitSettingsPage(BasePage):
    """Comprehensive Page Object for Unit Settings modal dialog and all sub-module tabs (/unit)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.toast = ToastNotifications(page)
        # Inline field-level validation errors only -- unlike
        # BasePage.validation_messages(), this deliberately excludes toast/
        # snackbar classes, which also fire on *success* (self.toast covers those).
        self.inline_validation_errors = page.locator("mat-error, .mat-mdc-form-field-error, .invalid-feedback")

        # Modal Container & Headers
        self.dialog = page.get_by_role("dialog").first
        self.modal_heading = page.locator("[role='dialog'] h2, h2").filter(
            has_text=re.compile(r"Unit Settings", re.I)
        ).first
        self.close_btn = page.locator("[role='dialog'] banner button, [role='dialog'] header button, [role='dialog'] button:has(img:has-text('close'))").first

        # Primary Tabs Navigation (buttons in vehicle configuration sections navigation)
        self.nav = page.get_by_role("navigation", name="Vehicle configuration sections")
        self.general_tab = page.locator("[role='dialog']").get_by_role("button", name="General").first
        self.icon_tab = page.locator("[role='dialog']").get_by_role("button", name="Icon").first
        self.sensors_tab = page.locator("[role='dialog']").get_by_role("button", name="Sensors").first
        self.service_tab = page.locator("[role='dialog']").get_by_role("button", name="Service").first
        self.alert_tab = page.locator("[role='dialog']").get_by_role("button", name="Alert").first

        # General Tab Read-Only Fields
        self.name_input = page.locator("[role='dialog']").get_by_role("textbox", name="Name").first
        self.device_model_input = page.locator("[role='dialog']").get_by_role("textbox", name="Device Model").first
        self.unit_type_disabled = page.locator("[role='dialog']").get_by_role("combobox", name="Unit Type").first
        self.serial_no_input = page.locator("[role='dialog']").get_by_role("textbox", name="Serial No").first
        self.sim1_input = page.locator("[role='dialog']").get_by_role("textbox", name="SIM 1").first
        self.sim2_input = page.locator("[role='dialog']").get_by_role("textbox", name="SIM 2").first
        self.port_no_input = page.locator("[role='dialog']").get_by_role("textbox", name="Port No").first
        self.creation_date_input = page.locator("[role='dialog']").get_by_role("textbox", name="Creation Date").first
        self.expiry_date_input = page.locator("[role='dialog']").get_by_role("textbox", name="Expiry Date").first

        # General Tab Editable Advanced & Group Fields
        self.mileage_calc_select = page.locator("[role='dialog']").get_by_role("combobox", name="Mileage Calculation On").first
        self.speed_limit_spin = page.locator("[role='dialog']").get_by_role("spinbutton", name=re.compile(r"Speed Limit", re.I)).first
        self.fuel_avg_spin = page.locator("[role='dialog']").get_by_role("spinbutton", name=re.compile(r"Fuel Consumption Avg", re.I)).first
        self.fuel_idle_spin = page.locator("[role='dialog']").get_by_role("spinbutton", name=re.compile(r"Fuel Consumption in Idling", re.I)).first
        self.polyline_colour_input = page.locator("[role='dialog'] input[type='color'], [role='dialog'] [aria-label*='Polyline Colour'], [role='dialog'] input[formcontrolname*='colour']").first
        self.location_group_select = page.locator("[role='dialog']").get_by_role("combobox", name="Location Group").first
        self.update_btn = page.locator("[role='dialog']").get_by_role("button", name="Update").first

        # Icon Tab Fields
        # Available-icon buttons are all named identically ("Icon Icon") with no
        # per-icon accessible distinction; a selected one is marked only by a
        # `bg-(--mat-sys-primary-container)` class (same convention as the
        # dashboard's active-filter button), so selection must be positional.
        self.icon_unit_type_select = page.locator("[role='dialog']").get_by_role("combobox", name="Unit Type").first
        self.current_icon_img = page.locator("[role='dialog'] img[alt='Current Icon']").first
        self.available_icons = page.locator("[role='dialog']").get_by_role("button", name="Icon Icon")
        self.available_icons_heading = page.locator("[role='dialog']").get_by_role("heading", name="Available Icons").first
        self.icon_update_btn = page.locator("[role='dialog']").get_by_role("button", name="Update").first
        # Any open mat-select's option list -- portaled to the page root, so not
        # scoped under [role='dialog']; shared by Unit Type and Sensor Type.
        self.dropdown_options = page.get_by_role("option")

        # Sensors Tab Fields
        self.standard_sensors_tab = page.locator("[role='dialog']").get_by_role("tab", name="Standard Sensors").first
        self.custom_sensors_tab = page.locator("[role='dialog']").get_by_role("tab", name="Custom Sensors").first
        self.add_sensor_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Sensor").first
        self.standard_sensor_rows = page.locator("[role='dialog'] [role='tabpanel'] table tbody tr")
        self.sensor_table_headers = page.locator("[role='dialog'] [role='tabpanel'] table thead th")
        self.sensor_items_per_page = page.locator("[role='dialog']").get_by_role("combobox", name="Items per page:").first
        self.next_page_btn = page.get_by_role("button", name="Next page").first
        # The topmost of any stacked [role='dialog']s (e.g. a sensor Detail view
        # opened on top of Unit Settings) -- portaled dialogs render in DOM/paint
        # order, so .last is the correct way to reach whichever opened most recently.
        self.topmost_dialog = page.get_by_role("dialog").last

        # Add Sensor Modal Dialog (a second, separate [role='dialog'] stacked on
        # top of the Unit Settings one). The dialog element itself has no wired
        # aria-labelledby (get_by_role(..., name=...) can't see its heading), so
        # it's disambiguated by filtering for that heading as content instead of
        # the positional .last the code previously guessed.
        self._sensor_dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name="Sensor Configuration")
        )
        self.sensor_config_heading = self._sensor_dialog.get_by_role("heading", name="Sensor Configuration").first
        self.sensor_name_input = self._sensor_dialog.get_by_role("textbox", name="Sensor Configuration Name").first
        self.sensor_type_select = self._sensor_dialog.get_by_role("combobox", name="Sensor Type").first
        # Real accessible name is the placeholder-like format string itself.
        self.config_expression_input = self._sensor_dialog.get_by_role("textbox", name="ColumnName(unit)|formula").first
        self.add_calibration_row_btn = self._sensor_dialog.get_by_role("button", name="Add Row").first
        self.clear_calibration_btn = self._sensor_dialog.get_by_role("button", name="Clear").first
        # No .first here -- callers need .nth(row_index)/.count() across all
        # calibration rows; a baked-in .first previously made every .nth() call
        # silently collapse back to row 0 (Locator.first().nth(n) == nth(0)).
        self.adc_spin = self._sensor_dialog.get_by_role("spinbutton", name="ADC")
        self.liter_spin = self._sensor_dialog.get_by_role("spinbutton", name="Liter Value")
        self.remove_calibration_row_btns = self._sensor_dialog.locator("button[mattooltip='Remove row']")
        self.save_sensor_btn = self._sensor_dialog.get_by_role("button", name="Save Config").first
        self.cancel_sensor_btn = self._sensor_dialog.get_by_role("button", name="Cancel").first

        # Custom Sensors row actions -- Angular Material `mattooltip` attributes,
        # not accessible names/labels, so these are matched by that attribute.
        self.custom_sensor_rows = page.locator("[role='dialog'] [role='tabpanel'] table tbody tr")

        # Service Sub-tabs
        self.profile_subtab = page.locator("[role='dialog']").get_by_role("button", name="Profile").first
        self.pollution_subtab = page.locator("[role='dialog']").get_by_role("button", name="Pollution").first
        self.fitness_subtab = page.locator("[role='dialog']").get_by_role("button", name="Fitness").first
        self.insurance_subtab = page.locator("[role='dialog']").get_by_role("button", name="Insurance").first
        self.vehicle_service_subtab = page.locator("[role='dialog']").get_by_role("button", name="Service").nth(1)

        # Service - Profile Form Fields
        self.profile_vin_input = page.locator("[role='dialog']").get_by_role("textbox", name="VIN").first
        self.profile_maker_input = page.locator("[role='dialog']").get_by_role("textbox", name="Maker Name").first
        self.profile_update_btn = page.locator("[role='dialog']").get_by_role("button", name="Update").first

        # Service - Pollution Form Fields
        self.pollution_history_heading = page.locator("[role='dialog']").get_by_role("heading", name=re.compile(r"Pollution History", re.I)).first
        self.pollution_add_cert_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Certificate").first
        self.pollution_cert_no_input = page.locator("[role='dialog']").get_by_role("textbox", name="Pollution Certificate No").first
        self.pollution_valid_from_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid From").first
        self.pollution_valid_till_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid Till").first
        self.pollution_cost_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Certificate Cost").first
        self.pollution_reminder_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Expiry Reminder Before (days)").first
        self.pollution_submit_btn = page.locator("[role='dialog']").get_by_role("button", name="Submit").first
        self.pollution_view_history_btn = page.locator("[role='dialog']").get_by_role("button", name="View History").first

        # Service - Fitness Form Fields
        self.fitness_history_heading = page.locator("[role='dialog']").get_by_role("heading", name=re.compile(r"Fitness History", re.I)).first
        self.fitness_add_cert_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Certificate").first
        self.fitness_valid_from_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid From").first
        self.fitness_valid_till_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid Till").first
        self.fitness_cost_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Certificate Cost (₹)").first
        self.fitness_reminder_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Expiry Reminder Before (Days)").first
        self.fitness_submit_btn = page.locator("[role='dialog']").get_by_role("button", name="Submit").first
        self.fitness_view_history_btn = page.locator("[role='dialog']").get_by_role("button", name="View History").first

        # Service - Insurance Form Fields
        self.insurance_history_heading = page.locator("[role='dialog']").get_by_role("heading", name=re.compile(r"Insurance History", re.I)).first
        self.insurance_add_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Insurance").first
        self.insurance_company_input = page.locator("[role='dialog']").get_by_role("textbox", name="Insurance Company").first
        self.insurance_premium_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Total Premium").first
        self.insurance_depreciation_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Depreciation").first
        self.insurance_idv_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="IDV").first
        self.insurance_valid_from_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid From").first
        self.insurance_valid_till_input = page.locator("[role='dialog']").get_by_role("textbox", name="Valid Till").first
        self.insurance_reminder_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Expiry Reminder Before (Days)").first
        self.insurance_submit_btn = page.locator("[role='dialog']").get_by_role("button", name="Submit").first
        self.insurance_view_history_btn = page.locator("[role='dialog']").get_by_role("button", name="View History").first

        # Service - Vehicle Service Form Fields
        self.service_history_heading = page.locator("[role='dialog']").get_by_role("heading", name=re.compile(r"Service History", re.I)).first
        self.service_add_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Service").first
        self.service_no_input = page.locator("[role='dialog']").get_by_role("textbox", name="Service No").first
        self.service_date_input = page.locator("[role='dialog']").get_by_role("textbox", name="Service Date").first
        self.odometer_before_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Odometer Before").first
        self.odometer_after_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Odometer After").first
        self.service_cost_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Service Cost").first
        self.next_service_odometer_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Next Service Odometer").first
        self.next_service_duration_input = page.locator("[role='dialog']").get_by_role("textbox", name="Next Service Duration").first
        self.service_reminder_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Reminder Before").first
        self.add_part_btn = page.locator("[role='dialog']").get_by_role("button", name="Add Part").first
        self.part_name_input = page.locator("[role='dialog']").get_by_role("textbox", name="Part Name").first
        self.part_cost_input = page.locator("[role='dialog']").get_by_role("spinbutton", name="Part Cost").first
        self.service_submit_btn = page.locator("[role='dialog']").get_by_role("button", name="Submit").first
        self.service_view_history_btn = page.locator("[role='dialog']").get_by_role("button", name="View History").first

        # Alert Tab Controls
        self.alert_heading = page.locator("[role='dialog']").get_by_role("heading", name=re.compile(r"Alert Configuration", re.I)).first
        self.alert_rows = page.locator("[role='dialog'] table tbody tr")
        self.alert_headers = page.locator("[role='dialog'] table thead th")
        self.alert_count_badge = page.locator("[role='dialog']").locator("text=/\\d+\\s*alert\\(s\\)/i").first

    def wait_for_modal_open(self):
        """Wait until Unit Settings modal opens."""
        self.wait_for_visible(self.modal_heading)

    def has_validation_error(self) -> bool:
        """True if an inline field error or an error toast is currently showing."""
        return self.inline_validation_errors.first.is_visible() or self.toast.error_toast.first.is_visible()

    def get_unit_identifier_from_header(self) -> str:
        """Extract the unit identifier displayed in parentheses in the modal heading."""
        self.wait_for_modal_open()
        text = self.modal_heading.inner_text().strip()
        match = re.search(r"\(([^)]+)\)", text)
        return match.group(1) if match else text

    def set_date_input(self, locator, value: str):
        """Set date value on Angular Material datepicker input removing readonly first."""
        locator.evaluate("el => el.removeAttribute('readonly')")
        locator.focus()
        locator.fill(value)
        locator.press("Tab")
        self.page.wait_for_timeout(300)

    def upload_certificate_file(self, file_path: str):
        """Upload certificate document file to the file input in the active form."""
        file_input = self.page.locator("[role='dialog'] form input[type='file']").first
        file_input.set_input_files(file_path)
        self.page.wait_for_timeout(300)


    def close_modal(self):
        """Close the Unit Settings modal dialog."""
        if self.close_btn.is_visible():
            self.close_btn.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def switch_tab(self, tab_name: str):
        """Switch to one of the main tabs: General, Icon, Sensors, Service, Alert."""
        tab_btn = self.page.locator("[role='dialog']").get_by_role("button", name=tab_name).first
        self.wait_for_visible(tab_btn)
        tab_btn.click()
        self.wait_for_loading_to_finish()

    def switch_service_subtab(self, subtab_name: str):
        """Switch between Service sub-tabs (Profile, Pollution, Fitness, Insurance, Service)."""
        self.switch_tab("Service")
        if subtab_name == "Service":
            subtab = self.vehicle_service_subtab
        else:
            subtab = self.page.locator("[role='dialog']").get_by_role("button", name=subtab_name).first
        self.wait_for_visible(subtab)
        subtab.click()
        self.wait_for_loading_to_finish()

    def update_speed_limit(self, speed_value: str):
        """Fill speed limit and click Update if enabled."""
        self.switch_tab("General")
        self.wait_for_visible(self.speed_limit_spin)
        self.speed_limit_spin.fill(speed_value)
        if self.update_btn.is_enabled():
            self.update_btn.click()
            self.wait_for_loading_to_finish()

    def change_polyline_color(self, color_hex: str):
        """Change the polyline color in General tab and click Update."""
        self.switch_tab("General")
        self.wait_for_visible(self.polyline_colour_input)
        self.polyline_colour_input.fill(color_hex.lower())
        if self.update_btn.is_enabled():

            self.update_btn.click()
            self.wait_for_loading_to_finish()

    # ─── Icon Tab ──────────────────────────────────────────────────────────────

    def get_selected_icon_index(self) -> int:
        """Return the index of the currently-selected available icon, or -1 if none."""
        for i in range(self.available_icons.count()):
            classes = self.available_icons.nth(i).get_attribute("class") or ""
            if "bg-(--mat-sys-primary-container)" in classes.split():
                return i
        return -1

    def select_available_icon(self, index: int):
        """Click an available icon by position (icons have no distinguishing accessible name)."""
        icon = self.available_icons.nth(index)
        self.wait_for_visible(icon)
        icon.click()

    def select_different_icon(self):
        """Select an available icon other than the currently-selected one; returns its index."""
        current = self.get_selected_icon_index()
        target = 0 if current != 0 else 1
        self.select_available_icon(target)
        return target

    # ─── Sensors Tab ───────────────────────────────────────────────────────────

    def open_add_sensor_form(self):
        """Open the Sensors tab and click Add Sensor, waiting for the config dialog."""
        self.switch_tab("Sensors")
        self.wait_for_visible(self.add_sensor_btn)
        self.add_sensor_btn.click()
        self.wait_for_visible(self.sensor_name_input)

    def open_edit_sensor_form(self, sensor_name: str):
        """Open the Custom Sensors tab and click Edit Sensor for a named row.

        Reuses the same "Sensor Configuration" dialog/fields as Add, pre-filled
        with the sensor's current values.
        """
        self.switch_tab("Sensors")
        self.custom_sensors_tab.click()
        self.wait_for_loading_to_finish()
        row = self.get_custom_sensor_row(sensor_name)
        row.locator("button[mattooltip='Edit Sensor']").click()
        self.wait_for_visible(self.sensor_name_input)

    def select_sensor_type(self, sensor_type: str):
        """Select a Sensor Type option in the open Add Sensor form."""
        self.sensor_type_select.click()
        option = self.page.get_by_role("option", name=sensor_type, exact=True).first
        self.wait_for_visible(option)
        option.click()

    def fill_sensor_basic_info(self, name: str, sensor_type: str = "Gauge"):
        """Fill Sensor Configuration Name and Sensor Type in the open Add Sensor form."""
        self.sensor_name_input.fill(name)
        self.select_sensor_type(sensor_type)

    def fill_calibration_row(self, row_index: int, adc_value: str, liter_value: str):
        """Fill ADC/Liter Value for a calibration row by index in the open Add Sensor form."""
        self.adc_spin.nth(row_index).fill(adc_value)
        self.liter_spin.nth(row_index).fill(liter_value)

    def get_custom_sensor_row(self, sensor_name: str):
        """Return the Custom Sensors table row locator for a named sensor."""
        return self.custom_sensor_rows.filter(has_text=sensor_name)

    def confirm_pending_delete(self):
        """Click Delete/Confirm/Yes on whatever delete-confirmation dialog is open, if any."""
        confirm = self.page.get_by_role("button", name=re.compile(r"^(Delete|Confirm|Yes)$", re.I)).first
        if confirm.is_visible():
            confirm.click()
            self.page.wait_for_timeout(1000)

    def delete_custom_sensor_row(self, row_locator):
        """Delete a custom sensor from an already-located row, confirming the dialog."""
        row_locator.locator("button[mattooltip='Delete Sensor']").click()
        self.page.wait_for_timeout(500)
        self.confirm_pending_delete()

    def delete_custom_sensor(self, sensor_name: str):
        """Delete a custom sensor by name via its row's Delete Sensor action."""
        self.delete_custom_sensor_row(self.get_custom_sensor_row(sensor_name))
        self.page.wait_for_timeout(1000)
        self.wait_for_loading_to_finish()

    # ─── Service History Records ──────────────────────────────────────────────

    def find_service_history_row_on_last_page(self, text: str, max_pages: int = 10):
        """Find a just-submitted history row (in the active Service sub-tab's
        table) by paging to the end of the table.

        New records are appended (not prepended), and text cells are JS-truncated
        (a literal "..." baked into the string, not just CSS-clipped) once long
        enough -- so search from the last page backwards using a short `text`
        that survives truncation, rather than assuming the row is on page 1.
        """
        # The paginator (and its Next page button) isn't rendered at all when
        # everything fits on one page, so check count() before is_enabled() --
        # calling is_enabled() on a selector matching zero elements just hangs
        # until timeout waiting for one to appear.
        next_btn = self.next_page_btn
        for _ in range(max_pages):
            if next_btn.count() > 0 and next_btn.is_enabled():
                next_btn.click()
                self.page.wait_for_timeout(600)
            else:
                break
        return self.dialog.locator("tbody tr").filter(has_text=text)

    def delete_service_history_row(self, row_locator):
        """Delete a Service (Fitness/Pollution/Insurance/Vehicle Service) history row.

        Clicking the row's Delete icon opens a "Delete ..." confirmation dialog;
        confirming there is what actually removes the record.
        """
        # A full-page loading overlay can still be fading out right after a
        # submit/page-navigation and blocks clicks until it's gone.
        overlay = self.page.locator("div.absolute.z-100000000, div[class*='z-100000000']").first
        try:
            overlay.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
        except Exception:
            pass
        row_locator.locator("button").last.click()
        self.page.wait_for_timeout(500)
        confirm_dialog = self.page.get_by_role("dialog").filter(
            has=self.page.get_by_role("heading", name=re.compile(r"^Delete", re.I))
        )
        confirm_dialog.get_by_role("button", name=re.compile(r"^Delete$", re.I)).click()
        self.page.wait_for_timeout(1000)
        self.wait_for_loading_to_finish()

