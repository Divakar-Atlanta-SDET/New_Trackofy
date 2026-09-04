import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage

# Per-alert-type field shape, confirmed live against each of the 12 real
# Add-forms (see live probes) -- fields are NOT uniform across alert types,
# so this is an explicit per-type map rather than one assumed shared shape.
# `numeric_fields` are formcontrolname values for plain number inputs;
# alerts not listed here (Geofence, AIS) have a fundamentally different flow
# and are covered by their own dedicated tests instead of this generic page.
# `time_range` alerts use one of two different widgets, confirmed live:
# "select" is a real mat-select dropdown of preset time slots (Speed, Idle);
# "picker" is a mat-timepicker text input needing a typed HH:mm value (AC,
# Ignition, Main Power, Temperature) -- clicking+picking a listbox option on
# a "picker" field leaves it ng-pristine/empty, which is what silently kept
# the submit button disabled before this was found.
# AC/Ignition/Main Power additionally require picking a trigger condition
# (formcontrolname "on"/"off" -- e.g. alert when AC turns on vs off) that
# carries no accessible label; confirmed live via the raw formcontrolname
# rather than a role/name lookup.
ALERT_SPECS = {
    "AC Alert": dict(add_name="Add AC Alert", vehicle_label="Select Vehicles", time_range=True, time_widget="picker", numeric_fields=[], extra_checkbox_formcontrolname="on"),
    "Ignition Alert": dict(add_name="Add Ignition Alert", vehicle_label="Select Vehicle", time_range=True, time_widget="picker", numeric_fields=[], extra_checkbox_formcontrolname="on"),
    "Main Power Alert": dict(add_name="Add Main Power Alert", vehicle_label="Select Units", time_range=True, time_widget="picker", numeric_fields=[], extra_checkbox_formcontrolname="on"),
    "Panic Alert": dict(add_name="Add Panic Alert", vehicle_label="Select Vehicles", time_range=False, numeric_fields=[]),
    "Speed Alert": dict(add_name="Add Speed Alert", vehicle_label="Select Units", time_range=True, time_widget="select", numeric_fields=["speedLimit"]),
    "Idle Alert": dict(add_name="Add Idle Alert", vehicle_label="Select Vehicles", time_range=True, time_widget="select", numeric_fields=[], numeric_by_label=["Idle Time (in minutes)"]),
    # Max must be greater than Min -- see fill_numeric_fields' distinct-value handling.
    "Temperature": dict(add_name="Add Temperature Alert", vehicle_label="Select Vehicles", time_range=True, time_widget="picker", numeric_fields=[], numeric_by_label=["Minimum Temperature", "Maximum Temperature"]),
    # The threshold field's label changes with the "Alert Type" pick
    # ("Voltage Limit" / "Temperature Limit") but its formcontrolname is
    # always "temp" -- confirmed live -- so target it by that instead of a
    # fixed label.
    "BMS Alert": dict(add_name="Add BMS Alert", vehicle_label="Select Vehicles", time_range=False, numeric_fields=["temp"], extra_combos=["Alert Type", "Condition"]),
    "POI Alert": dict(add_name="Add POI Alert", vehicle_label="Select Units", time_range=False, numeric_fields=[], extra_combos=["POIs"]),
    # "Current Odometer" and "Service At" are both auto-computed/disabled
    # once a vehicle is selected (Service At = Current Odometer + Service
    # Interval) -- confirmed live -- so only Service Interval is user-editable.
    "Vehicle Odometer Alert": dict(add_name="Add Odometer Alert", vehicle_label="Vehicle", time_range=False, numeric_fields=[], numeric_by_label=["Service Interval"]),
}


class AlertConfigPage(SettingsListPage):
    """Generic Alert Configuration list + Create/Edit dialog, parametrized by
    `alert_type` (one of ALERT_SPECS' keys). Covers the 10 alert types that
    share this create-dialog shape. Geofence (separate full-page flow) and
    AIS Alert (bulk toggle, not a per-record CRUD form) are out of scope for
    this class -- confirmed live neither matches this shape.
    """

    def __init__(self, page: Page, alert_type: str):
        self.alert_type = alert_type
        self.spec = ALERT_SPECS[alert_type]
        super().__init__(page, add_button_name=self.spec["add_name"])
        # Only one modal is ever open at a time in this app (confirmed
        # throughout Settings) -- no need to disambiguate by heading/close-label.
        self.dialog = page.get_by_role("dialog")
        self.vehicle_select = self.dialog.get_by_role("combobox", name=self.spec["vehicle_label"])
        self.vehicle_listbox = page.get_by_role("listbox")
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")
        self.submit_btn = self.dialog.get_by_role("button", name=re.compile(r"Create Alert|Save Changes", re.I))

    def open_add_form(self):
        self.add_btn.click()
        self.wait_for_visible(self.vehicle_select)

    def select_vehicles(self, count: int = 1) -> list[str]:
        self.vehicle_select.click()
        self.wait_for_visible(self.vehicle_listbox.get_by_role("option").first)
        options = self.vehicle_listbox.get_by_role("option")
        names = []
        for i in range(count):
            opt = options.nth(i)
            opt.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT_MS)
            names.append(opt.inner_text().strip())
            opt.click()
            self.page.wait_for_timeout(300)
        if self.vehicle_listbox.is_visible():
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)
        return names

    def set_time_range(self):
        if not self.spec["time_range"]:
            return
        if self.spec["time_widget"] == "picker":
            # A masked timepicker input -- .fill() left it ng-pristine
            # (confirmed live), same class of issue as Tracking's date
            # fields; real keystrokes are needed instead.
            for fc, value in (("startTime", "09:00"), ("endTime", "17:00")):
                field = self.dialog.locator(f"input[formcontrolname='{fc}']")
                field.click()
                field.press("Control+A")
                field.press("Delete")
                field.press_sequentially(value)
                self.page.wait_for_timeout(300)
            self.page.keyboard.press("Tab")
            self.page.wait_for_timeout(300)
            return
        # "select" widget: a real dropdown of preset time slots. Start must
        # be before End -- pick the first option for Start and a later one
        # for End rather than the same option for both (confirmed live:
        # picking identical Start/End times left the form invalid).
        combos = self.dialog.get_by_role("combobox").all()[1:3]
        pick_last = [False, True]
        for combo, last in zip(combos, pick_last):
            combo.click()
            self.page.wait_for_timeout(300)
            listbox = self.page.get_by_role("listbox")
            self.wait_for_visible(listbox.get_by_role("option").first)
            option = listbox.get_by_role("option").last if last else listbox.get_by_role("option").first
            option.click()
            self.page.wait_for_timeout(300)

    def set_extra_combos(self):
        for label in self.spec.get("extra_combos", []):
            combo = self.dialog.get_by_role("combobox", name=label)
            if combo.count() == 0:
                continue
            combo.click()
            self.page.wait_for_timeout(300)
            listbox = self.page.get_by_role("listbox")
            listbox.get_by_role("option").first.click()
            self.page.wait_for_timeout(300)
            if listbox.is_visible():
                self.page.keyboard.press("Escape")

    def fill_numeric_fields(self, value: str = "10"):
        for fc in self.spec.get("numeric_fields", []):
            field = self.dialog.locator(f"input[formcontrolname='{fc}']")
            field.fill(value)
        # Multiple by-label fields (e.g. Temperature's Min/Max) need
        # distinct increasing values -- filling both with the same value
        # left the form invalid (confirmed live, Max must exceed Min).
        for i, label in enumerate(self.spec.get("numeric_by_label", [])):
            field = self.dialog.get_by_role("spinbutton", name=label)
            field.fill(str(int(value) + i * 10))

    def set_notify(self, channel: str = "Application"):
        cb = self.dialog.get_by_role("checkbox", name=channel)
        if cb.count() > 0 and not cb.is_checked():
            cb.click()
        fc = self.spec.get("extra_checkbox_formcontrolname")
        if fc:
            extra = self.dialog.locator(f"input[type='checkbox'][formcontrolname='{fc}'], mat-checkbox[formcontrolname='{fc}'] input")
            if extra.count() > 0 and not extra.is_checked():
                self.dialog.locator(f"mat-checkbox[formcontrolname='{fc}']").click()

    def fill_valid_form(self):
        self.select_vehicles(1)
        self.set_time_range()
        self.set_extra_combos()
        self.fill_numeric_fields()
        self.set_notify()

    def submit(self):
        self.submit_btn.click()
        self.dialog.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()

    def edit_button(self, row_text: str):
        return self.row_containing(row_text).get_by_role("button", name=re.compile("Edit", re.I))

    def delete_button(self, row_text: str):
        return self.row_containing(row_text).get_by_role("button", name=re.compile("Delete", re.I))

    def delete_alert(self, row_text: str):
        self.delete_button(row_text).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.page.wait_for_timeout(400)
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        self.row_containing(row_text).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)


class GeofenceAlertPage(SettingsListPage):
    """Geofence Alert's "Add" flow is a dedicated full page (a map + drawing
    tools at /settings/alert/geofence/create-geofence), not a dialog like
    the other 11 alert types -- confirmed live. Actually drawing a shape on
    the map canvas is out of scope for reliable UI automation (same class of
    limitation as the Tracking module's GPS/map interactions); this page
    object covers navigation and the create page's non-map controls only.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Add Geofence")
        self.name_input = page.locator("input[formcontrolname='geofence_name']")
        self.create_btn = page.get_by_role("button", name="Create Geofence")
        self.cancel_btn = page.get_by_role("button", name="Cancel")

    def open_create_page(self):
        self.add_btn.click()
        self.wait_for_visible(self.name_input)

    def close_create_page(self):
        if self.cancel_btn.count() > 0 and self.cancel_btn.is_visible():
            self.cancel_btn.click()


class AisAlertPage(SettingsListPage):
    """AIS Alert is NOT a create/delete record form like the other 11 alert
    types -- confirmed live it's a per-vehicle settings grid: each table row
    is an existing vehicle with an Edit action that opens a dialog of
    individual sub-alert toggles (Power/Ignition/Emergency/Driving/Geofence
    categories, each with several named sub-alerts as real mat-slide-toggle
    switches). There is no Add/Create/Delete here.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="__no_add_button__")
        self.dialog = page.get_by_role("dialog")
        self.update_btn = self.dialog.get_by_role("button", name="Update Changes")
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")

    def open_edit_for_row(self, row_index: int = 0):
        self.table.locator("tbody tr").nth(row_index).locator("button").first.click()
        self.wait_for_visible(self.dialog)
        self.page.wait_for_timeout(800)

    def toggles(self):
        return self.dialog.get_by_role("switch")

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()
