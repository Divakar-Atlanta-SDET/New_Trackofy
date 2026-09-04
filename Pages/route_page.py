import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage


class RouteManagementPage(SettingsListPage):
    """Route Management list + the dedicated Create Route page (a full page
    with a map, not a dialog -- confirmed live at /settings/route/create-route).
    Origin/destination use a real Places-style autocomplete that returns
    live suggestions, confirmed workable via UI automation (unlike
    Geofence's freeform shape-drawing).
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Add Route")
        self.name_input = page.locator("input[formcontrolname='routeName']")
        self.origin_input = page.get_by_placeholder("Search starting location")
        self.destination_input = page.get_by_placeholder("Search destination")
        self.add_waypoint_btn = page.get_by_role("button", name="Add Waypoint")
        self.show_route_btn = page.get_by_role("button", name="Show Route")
        self.save_btn = page.get_by_role("button", name="Save Route")
        self.cancel_btn = page.get_by_role("button", name="Cancel")
        self.reset_btn = page.get_by_role("button", name="Reset")

        # The Create Route page has a second sub-tab, "Custom Route" --
        # confirmed live: same routeName field, but source/destination
        # inputs (formcontrolname="source"/"destination") instead of the
        # Create Route tab's placeholder-identified fields, plus a manual
        # "Start Drawing" tool to trace a path on the map. Actually drawing
        # a freeform path via mouse events is out of scope for reliable UI
        # automation (same limitation class as Geofence's shape drawing);
        # this covers the tab and its non-drawing controls only.
        self.custom_route_tab = page.get_by_role("tab", name=re.compile("Custom Route"))
        self.custom_source_input = page.locator("input[formcontrolname='source']")
        self.custom_destination_input = page.locator("input[formcontrolname='destination']")
        self.start_drawing_btn = page.get_by_role("button", name="Start Drawing")
        self.clear_route_btn = page.get_by_role("button", name="Clear Route")

    def open_custom_route_tab(self):
        self.custom_route_tab.click()
        self.wait_for_visible(self.custom_source_input)
        self.page.wait_for_timeout(1000)

    def open_create_route(self):
        self.add_btn.click()
        self.wait_for_visible(self.name_input)
        # The map/places widget can still be initializing after the page's
        # own DOM is ready -- typing into the search boxes before it's live
        # produced no suggestions at all (confirmed live).
        self.page.wait_for_timeout(2000)

    def pick_location(self, input_locator, query: str) -> str:
        """Type into an origin/destination/waypoint search box and pick the
        first live suggestion. Returns the resulting resolved value."""
        # The autocomplete's suggestion search is debounced off real
        # keystrokes -- .fill() sets the value without firing them, which
        # left the suggestion panel never opening (confirmed live, same
        # class of issue as the alert forms' masked timepicker inputs).
        # This is Google Places Autocomplete (confirmed live via the input's
        # own "pac-target-input" class), not a Material mat-select -- its
        # suggestions are real .pac-item rows, not <mat-option>. Clicking a
        # .pac-item is flaky (confirmed live: the suggestion panel's own
        # container intercepts the click while still positioning itself) --
        # keyboard selection (ArrowDown + Enter) is the standard, reliable
        # way to pick a Places Autocomplete suggestion. The live Places API
        # call itself is occasionally slow -- retry the keystrokes once
        # rather than fail outright on a single timeout.
        suggestion = self.page.locator(".pac-item:visible").first
        attempts = 3
        for attempt in range(attempts):
            input_locator.click()
            input_locator.press("Control+A")
            input_locator.press("Delete")
            input_locator.press_sequentially(query, delay=80)
            try:
                self.wait_for_visible(suggestion, timeout=8000)
                break
            except Exception:
                if attempt == attempts - 1:
                    raise
                self.page.wait_for_timeout(1500)
        input_locator.press("ArrowDown")
        self.page.wait_for_timeout(200)
        input_locator.press("Enter")
        self.page.wait_for_timeout(500)
        return input_locator.input_value()

    def add_waypoint(self, query: str) -> str:
        """Clicks Add Waypoint and picks a location for the newly added
        field -- confirmed live each click adds another "Search waypoint"
        field, so `.last` always targets the one just added."""
        self.add_waypoint_btn.click()
        self.page.wait_for_timeout(500)
        waypoint_input = self.page.get_by_placeholder("Search waypoint").last
        self.wait_for_visible(waypoint_input)
        return self.pick_location(waypoint_input, query)

    def create_route(self, name: str, origin_query: str, destination_query: str):
        self.open_create_route()
        self.name_input.fill(name)
        self.pick_location(self.origin_input, origin_query)
        self.pick_location(self.destination_input, destination_query)
        self.page.wait_for_timeout(500)
        self.save_btn.click()
        # Confirmed live: a successful save redirects to /home, not back to
        # /settings/route like every other Settings entity (see
        # Bug_Report.md #12) -- navigate back explicitly rather than assume.
        self.expect_path("/home")
        self.page.goto("/settings/route")
        self.expect_path("/settings/route")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def cancel_create_route(self):
        self.cancel_btn.click()
        self.page.wait_for_timeout(1500)
        if not self.is_on_path("/settings/route"):
            # Same redirect-to-/home quirk seen on save (Bug_Report.md #12)
            # -- confirmed live it can also happen on Cancel.
            self.page.goto("/settings/route")
            self.expect_path("/settings/route")
        self.wait_for_loading_to_finish()

    # Row action buttons carry no accessible name (confirmed live, icon-only)
    # but the columns are in a fixed, confirmed order: Show Route, Assign
    # Unit, Details, Delete -- same column-position pattern already used in
    # driver_performance_page.py for buttons without accessible names.
    def show_route_button(self, route_name: str):
        return self.row_containing(route_name).locator("td").nth(6).locator("button")

    def assign_unit_button(self, route_name: str):
        return self.row_containing(route_name).locator("td").nth(7).locator("button")

    def details_button(self, route_name: str):
        return self.row_containing(route_name).locator("td").nth(8).locator("button")

    def delete_button(self, route_name: str):
        return self.row_containing(route_name).locator("td").nth(9).locator("button")

    def delete_route(self, route_name: str):
        self.delete_button(route_name).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.page.wait_for_timeout(400)
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        self.row_containing(route_name).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
