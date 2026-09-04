import re
from playwright.sync_api import Page
from Pages.base_page import BasePage
from components.pagination import PaginationComponent
from components.search import SearchComponent
from components.toast_notifcations import ToastNotifications

ALERT_TYPES = [
    "AC Alert",
    "Ignition Alert",
    "Main Power Alert",
    "Panic Alert",
    "Speed Alert",
    "Idle Alert",
    "Temperature",
    "BMS Alert",
    "POI Alert",
    "Geofence Alert",
    "Vehicle Odometer Alert",
    "AIS Alert",
]

# Confirmed live -- not a uniform slugify(name) pattern (e.g. Vehicle Group ->
# "group", Main Power Alert -> "power", AIS Alert -> "ais-alert"), so this is
# an explicit map rather than a derived one.
ALERT_URL_SLUGS = {
    "AC Alert": "ac",
    "Ignition Alert": "ignition",
    "Main Power Alert": "power",
    "Panic Alert": "panic",
    "Speed Alert": "speed",
    "Idle Alert": "idle",
    "Temperature": "temperature",
    "BMS Alert": "bms",
    "POI Alert": "poi",
    "Geofence Alert": "geofence",
    "Vehicle Odometer Alert": "vehicle-odometer",
    "AIS Alert": "ais-alert",
}


class SettingsSideMenu(BasePage):
    """The Settings module's own left tree navigation (distinct from the
    global top nav) -- accordion-style: expanding one top-level section
    collapses whichever was open. Confirmed live against /settings.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_role("textbox", name="Search settings")
        self.collapse_menu_btn = page.get_by_role("button", name="Collapse settings menu")

        self.driver_management_btn = page.get_by_role("button", name="Driver Management", exact=True)
        self.vehicle_management_btn = page.get_by_role("button", name="Vehicle Management", exact=True)
        self.alert_configuration_btn = page.get_by_role("button", name="Alert Configuration", exact=True)
        self.route_management_btn = page.get_by_role("button", name="Route Management", exact=True)

        self.driver_btn = page.get_by_role("button", name="Driver", exact=True)
        self.driver_performance_btn = page.get_by_role("button", name="Driver Performance", exact=True)
        self.vehicle_group_btn = page.get_by_role("button", name="Vehicle Group", exact=True)
        self.vehicle_performance_btn = page.get_by_role("button", name="Vehicle Performance", exact=True)
        self.location_control_btn = page.get_by_role("button", name="Location Control", exact=True)
        self.alert_type_buttons = {
            name: page.get_by_role("button", name=name, exact=True) for name in ALERT_TYPES
        }

    def _ensure_expanded(self, section_btn):
        if section_btn.get_attribute("aria-expanded") != "true":
            section_btn.click()
            self.wait_for_loading_to_finish()

    def _goto(self, path: str):
        # Direct navigation, not click-through-the-accordion: confirmed live
        # that re-clicking an already-expanded section button collapses it
        # instead of leaving it open, which made the click-chain silently
        # strand tests on the wrong page (aria-expanded state was not
        # reliably re-checked in time). Real URLs confirmed per-page below.
        # The accordion click/expand behavior itself is covered separately
        # in test_settings_nav_functional.py using these same locators.
        if not self.page.url.endswith(path):
            # Re-navigating to the URL already loaded (e.g. /settings ->
            # /settings/driver, the default route) triggers a real full-page
            # reload that this Angular app doesn't handle cleanly -- confirmed
            # live, it left the heading unrenderable well past a 15s wait.
            self.page.goto(path)
        self.wait_for_loading_to_finish()

    def open_driver(self):
        self._goto("/settings/driver")

    def open_driver_performance(self):
        self._goto("/settings/driver-performance")

    def open_vehicle_group(self):
        self._goto("/settings/group")

    def open_vehicle_performance(self):
        self._goto("/settings/vehicle-performance")

    def open_location_control(self):
        self._goto("/settings/location")

    def open_alert(self, alert_type: str):
        """`alert_type` must be one of ALERT_TYPES (e.g. 'Speed Alert')."""
        self._goto(f"/settings/alert/{ALERT_URL_SLUGS[alert_type]}")

    def open_route_management(self):
        self._goto("/settings/route")

    def search_settings(self, query: str):
        self.search_input.fill(query)
        self.wait_for_loading_to_finish()


class SettingsListPage(BasePage):
    """Shared shape of a Settings entity list page (Driver, Vehicle Group,
    Speed Alert, Route, ...): heading, record count, an Add action,
    pagination/search/print/copy, and a data table with named per-row
    action buttons. Confirmed live across Driver, Vehicle Group, Speed
    Alert and Route Management -- entity pages compose this instead of
    re-declaring the same locators.

    `export_entity_name` is the plural noun the real Export buttons use,
    e.g. "drivers" for "Export drivers to Excel" -- components/export.py
    targets a different module's icon-ligature buttons and doesn't match
    Settings' real (descriptive-name) export buttons, so this builds its
    own instead of reusing that component unmodified.
    """

    def __init__(self, page: Page, add_button_name: str, export_entity_name: str | None = None):
        super().__init__(page)
        self.toast = ToastNotifications(page)
        self.pagination = PaginationComponent(page)
        self.search = SearchComponent(page)

        # This app nests three <main> landmarks per Settings page (shell,
        # content header, table region) but only ever renders one real <h1>
        # and one real <table> at a time (confirmed live) -- scoping to
        # main.last actually grabbed the *wrong* main (the one without the
        # heading) and broke it; unscoped is correct here. The real earlier
        # flakiness was a read-during-SPA-transition race, now handled by
        # the settle wait in the driver_page/driver_performance_page fixtures.
        self.heading = page.locator("h1").first
        self.add_btn = page.get_by_role("button", name=add_button_name, exact=True)
        self.print_btn = page.get_by_role("button", name=re.compile(r"^Print", re.I))
        self.copy_btn = page.get_by_role("button", name=re.compile(r"^Copy", re.I))
        self.table = page.locator("table").first
        self.confirm_delete_btn = page.get_by_role("dialog").get_by_role("button", name=re.compile(r"Delete|Confirm|Yes", re.I))
        self.cancel_delete_btn = page.get_by_role("dialog").get_by_role("button", name=re.compile(r"Cancel|No", re.I))

        if export_entity_name:
            self.export_excel_btn = page.get_by_role(
                "button", name=re.compile(rf"Export {export_entity_name} to Excel", re.I)
            )
            self.export_csv_btn = page.get_by_role(
                "button", name=re.compile(rf"Export {export_entity_name} to CSV", re.I)
            )
            self.export_pdf_btn = page.get_by_role(
                "button", name=re.compile(rf"Export {export_entity_name} to PDF", re.I)
            )

    def search_and_wait(self, query: str):
        """SearchComponent.search() fills and waits for network idle, but this
        app's list filter runs off a client-side debounce (no fresh request
        to wait on) that only actually commits on Enter -- confirmed live:
        fill() alone left the table unfiltered indefinitely. Press Enter too."""
        self.wait_for_visible(self.search.search_input)
        self.search.search(query)
        self.search.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(500)

    def clear_search_and_wait(self):
        try:
            self.wait_for_visible(self.search.search_input)
        except Exception:
            # Occasionally the searchbox doesn't reappear promptly after a
            # multi-dialog flow (confirmed live, cause not fully pinned down)
            # -- a reload is the reliable way back to a clean list state,
            # which is all callers actually need this for (usually teardown).
            self.page.reload()
            self.wait_for_loading_to_finish()
            self.wait_for_visible(self.search.search_input)
            return
        self.search.clear_search()
        self.search.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)

    def row_containing(self, text: str):
        return self.table.locator("tbody tr").filter(has_text=text)

    def empty_state_visible(self) -> bool:
        return self.contains_any_text(["No ", "not found", "no records", "no data"])
