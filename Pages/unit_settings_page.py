import re
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage


class UnitSettingsPage(BasePage):
    """Comprehensive Page Object for Unit Settings modal dialog and all sub-module tabs (/unit)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Modal Container & Headers
        self.modal_heading = page.locator("h1, h2, h3, [role='dialog'] h2").filter(has_text=re.compile(r"Unit Settings", re.I)).first
        self.close_btn = page.get_by_role("button", name=re.compile(r"close", re.I)).first

        # Primary Tabs Navigation
        self.general_tab = page.locator("button, [role='tab'], a").filter(has_text=re.compile(r"General", re.I)).first
        self.icon_tab = page.locator("button, [role='tab'], a").filter(has_text=re.compile(r"Icon", re.I)).first
        self.sensors_tab = page.locator("button, [role='tab'], a").filter(has_text=re.compile(r"Sensors", re.I)).first
        self.service_tab = page.locator("button, [role='tab'], a").filter(has_text=re.compile(r"Service", re.I)).first
        self.alert_tab = page.locator("button, [role='tab'], a").filter(has_text=re.compile(r"Alert", re.I)).first

        # General Tab Form Fields
        self.name_input = page.locator("input[formcontrolname='name'], input[placeholder*='Name']").first
        self.device_model_input = page.locator("input[formcontrolname='deviceModel']").first
        self.serial_no_input = page.locator("input[formcontrolname='serialNo']").first
        self.sim1_input = page.locator("input[formcontrolname='sim1']").first
        self.sim2_input = page.locator("input[formcontrolname='sim2']").first
        self.port_no_input = page.locator("input[formcontrolname='portNo']").first
        self.creation_date_input = page.locator("input[formcontrolname='creationDate']").first
        self.expiry_date_input = page.locator("input[formcontrolname='expiryDate']").first

        # Advanced General Editable Fields
        self.mileage_calc_select = page.locator("mat-select[formcontrolname*='mileage'], combobox[name*='Mileage']").first
        self.speed_limit_spin = page.locator("input[formcontrolname*='speed'], input[aria-label*='Speed']").first
        self.fuel_avg_spin = page.locator("input[formcontrolname*='fuel'], input[aria-label*='Fuel']").first
        self.fuel_idle_spin = page.locator("input[formcontrolname*='Idle'], input[formcontrolname*='idling'], input[aria-label*='Idle'], spinbutton[name*='Idling']").first
        self.polyline_colour_input = page.locator("input[formcontrolname*='colour'], input[type='color']").first
        self.location_group_select = page.locator("mat-select[formcontrolname*='locationGroup'], combobox[name*='Location Group']").first
        self.update_btn = page.get_by_role("button", name=re.compile(r"^(Update|Save)$", re.I)).first

        # Icon Tab Fields
        self.icon_unit_type_select = page.locator("mat-select[formcontrolname*='unitType'], combobox[name*='Unit Type']").first
        self.current_icon_img = page.locator("img[alt='Current Icon'], img.current-icon").first
        self.available_icons = page.locator(".icon-grid img, .available-icons img")

        # Sensors Tab Fields
        self.standard_sensors_tab = page.locator("button, [role='tab']").filter(has_text=re.compile(r"Standard Sensors", re.I)).first
        self.custom_sensors_tab = page.locator("button, [role='tab']").filter(has_text=re.compile(r"Custom Sensors", re.I)).first
        self.add_sensor_btn = page.get_by_role("button", name=re.compile(r"Add Sensor", re.I)).first
        self.sensor_name_input = page.locator("input[formcontrolname='sensorName'], input[placeholder*='Sensor Name']").first
        self.sensor_type_select = page.locator("mat-select[formcontrolname='sensorType']").first
        self.config_expression_input = page.locator("input[formcontrolname='configurationExpression']").first
        self.add_calibration_row_btn = page.get_by_role("button", name=re.compile(r"Add Row", re.I)).first
        self.clear_calibration_btn = page.get_by_role("button", name=re.compile(r"Clear", re.I)).first
        self.cancel_sensor_btn = page.get_by_role("button", name=re.compile(r"Cancel", re.I)).first
        self.save_sensor_btn = page.get_by_role("button", name=re.compile(r"Save Config", re.I)).first

        # Service Sub-tabs
        self.fitness_subtab = page.locator("a, button, [role='tab'], div, span").filter(has_text=re.compile(r"^Fitness$", re.I)).first
        self.insurance_subtab = page.locator("a, button, [role='tab'], div, span").filter(has_text=re.compile(r"^Insurance$", re.I)).first
        self.pollution_subtab = page.locator("a, button, [role='tab'], div, span").filter(has_text=re.compile(r"^Pollution$", re.I)).first
        self.vehicle_service_subtab = page.locator("a, button, [role='tab'], div, span").filter(has_text=re.compile(r"^Service$", re.I)).first

        # Service Sub-tab Forms
        self.fitness_valid_from = page.locator("input[formcontrolname*='validFrom'], input[placeholder*='Valid From']").first
        self.fitness_valid_till = page.locator("input[formcontrolname*='validTill'], input[placeholder*='Valid Till']").first
        self.fitness_cost_input = page.locator("input[formcontrolname*='cost'], input[placeholder*='Cost']").first
        self.fitness_reminder_input = page.locator("input[formcontrolname*='reminder'], input[placeholder*='Reminder']").first
        self.fitness_submit_btn = page.get_by_role("button", name=re.compile(r"^(Submit|Save)$", re.I)).first

        self.insurance_company_input = page.locator("input[formcontrolname*='company']").first
        self.insurance_premium_input = page.locator("input[formcontrolname*='premium']").first
        self.insurance_depreciation_input = page.locator("input[formcontrolname*='depreciation']").first
        self.insurance_idv_input = page.locator("input[formcontrolname*='idv']").first
        self.insurance_file_input = page.locator("input[type='file']").first

        self.pollution_cert_no = page.locator("input[formcontrolname*='cert'], input[placeholder*='Certificate']").first
        self.pollution_cost_input = page.locator("input[formcontrolname*='cost']").first

        self.service_no_input = page.locator("input[formcontrolname*='serviceNo']").first
        self.service_date_input = page.locator("input[formcontrolname*='serviceDate']").first
        self.odometer_before_input = page.locator("input[formcontrolname*='odometerBefore']").first
        self.odometer_after_input = page.locator("input[formcontrolname*='odometerAfter']").first
        self.service_cost_input = page.locator("input[formcontrolname*='serviceCost']").first
        self.next_service_odometer_input = page.locator("input[formcontrolname*='nextServiceOdometer']").first
        self.next_service_duration_input = page.locator("input[formcontrolname*='nextServiceDuration']").first
        self.add_part_btn = page.get_by_role("button", name=re.compile(r"Add Part", re.I)).first
        self.view_history_btn = page.get_by_role("button", name=re.compile(r"View History", re.I)).first

        # Alert Tab Controls
        self.alert_rows = page.locator("table tbody tr")
        self.no_alerts_message = page.locator("text=/No alerts/i, text=/No data/i").first

        # Toast Container
        self.toast_container = page.locator(".toast-container, .ngx-toastr, mat-snack-bar-container, [role='alert'], [class*='toast']").first

    def wait_for_modal_open(self):
        """Wait until Unit Settings modal opens."""
        self.wait_for_visible(self.modal_heading)

    def close_modal(self):
        """Close the Unit Settings modal dialog using Escape press."""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def switch_tab(self, tab_name: str):
        """Switch to one of the main tabs: General, Icon, Sensors, Service, Alert."""
        tab_map = {
            "General": self.general_tab,
            "Icon": self.icon_tab,
            "Sensors": self.sensors_tab,
            "Service": self.service_tab,
            "Alert": self.alert_tab,
        }
        target_tab = tab_map.get(tab_name)
        if target_tab:
            self.wait_for_visible(target_tab)
            target_tab.click()
            self.wait_for_loading_to_finish()

    def switch_service_subtab(self, subtab_name: str):
        """Switch between Service sub-tabs (Fitness, Insurance, Pollution, Service)."""
        self.switch_tab("Service")
        subtab = self.page.locator("a, button, [role='tab'], div, span").filter(has_text=re.compile(rf"\b{re.escape(subtab_name)}\b", re.I)).first
        if subtab.is_visible():
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

    def expect_toast_notification(self, text_pattern: str = None):
        """Assert success or status toast message appears after save/update."""
        if text_pattern:
            toast = self.page.locator(".toast-container, .ngx-toastr, mat-snack-bar-container, [role='alert'], [class*='toast']").filter(has_text=re.compile(text_pattern, re.I)).first
        else:
            toast = self.toast_container
        self.wait_for_visible(toast)
