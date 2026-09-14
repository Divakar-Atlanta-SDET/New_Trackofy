import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class CanBasePage(BasePage):
    """Shared CAN sub-menu (Dashboard/Unit/Trends/Reports/Alerts/Settings)
    and the persistent Live Fleet Map widget, present on every CAN
    sub-page. Routes confirmed live: /can/dashboard, /can/units,
    /can/trends, /can/report, /can/alerts, /can/settings -- note Unit and
    Reports use different URL segments (units, report) than their nav
    labels ("Unit", "Reports") would suggest.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: the dashboard's own "Open Units" shortcut link
        # shares the exact href (/can/units) with the CAN sub-menu's
        # "Unit" link -- scoping to the sidebar landmark (as Playwright's
        # own strict-mode-violation error suggested) disambiguates them.
        sidebar = page.get_by_role("complementary")
        self.nav_dashboard = sidebar.locator("a[href='/can/dashboard']")
        self.nav_unit = sidebar.locator("a[href='/can/units']")
        self.nav_trends = sidebar.get_by_role("link", name="Trends", exact=True)
        self.nav_reports = sidebar.locator("a[href='/can/report']")
        self.nav_alerts = sidebar.get_by_role("link", name="Alerts", exact=True)
        self.nav_settings = sidebar.locator("a[href='/can/settings']")

        self.module_heading = page.get_by_role("heading", name="CAN", exact=True)
        self.collapse_menu_button = page.get_by_role("button", name="Collapse CAN menu")

        self.live_fleet_map_heading = page.get_by_text("Live Fleet Map", exact=True)
        self.map_view_button = page.get_by_role("button", name="Map", exact=True)
        self.hybrid_view_button = page.get_by_role("button", name="Hybrid", exact=True)
        self.map_fullscreen_button = page.get_by_role("button", name="Toggle fullscreen view")

    def safe_click(self, locator: Locator):
        # Confirmed live (filed as a bug, Bug_Report.md): the Live Fleet
        # Map's full-viewport ".can-map-viewport-boundary" wrapper is
        # itself pointer-events:none, but an unstyled child <div> inside
        # it (pointer-events:auto) can sit on top of ordinary page
        # controls -- confirmed reproducing 3/3 for the Unit sub-nav link,
        # and observed intermittently intercepting comboboxes/buttons
        # across every CAN sub-page during this suite's own live runs.
        # A plain click is tried first (so a real, unforced click is what
        # gets exercised whenever nothing is actually in the way); on
        # failure, calling the DOM .click() method directly bypasses
        # point-based hit testing entirely and reliably reaches the
        # element's real click handler regardless of what's visually on
        # top of it. See Tests/edgecase/test_can_navigation_edgecase.py
        # for the test that pins the real (broken), non-workaround
        # behavior for the one nav-link case confirmed reproducible.
        try:
            locator.click(timeout=5000)
        except Exception:
            locator.evaluate("el => el.click()")

    def open_dashboard(self):
        self.safe_click(self.nav_dashboard)
        self.expect_path("/can/dashboard")

    def open_unit(self):
        self.safe_click(self.nav_unit)
        self.expect_path("/can/units")

    def open_trends(self):
        self.safe_click(self.nav_trends)
        self.expect_path("/can/trends")

    def open_reports(self):
        self.safe_click(self.nav_reports)
        self.expect_path("/can/report")

    def open_alerts(self):
        self.safe_click(self.nav_alerts)
        self.expect_path("/can/alerts")

    def open_settings(self):
        self.safe_click(self.nav_settings)
        self.expect_path("/can/settings")

    def _read_stable_int(self, pattern: str, retries: int = 15, interval_ms: int = 500, source=None) -> int:
        # Confirmed live 2026-09-14: every one of these regex-matched
        # counts (map unit count, pagination total, configured rule
        # count, alert count) reads "0" as a loading placeholder
        # immediately after page load/navigation -- usually resolving to
        # the real value within ~0.5s, but confirmed to sometimes take
        # several seconds (matches this app's already-documented
        # intermittent slow-load pattern elsewhere). A same-value-twice
        # check alone isn't enough -- a "0" that hasn't started updating
        # yet also reads the same twice. Requires TWO consecutive
        # non-zero agreeing reads, falling back to a zero/last value
        # only once retries are exhausted.
        get_text = source or self.visible_text
        last = None
        for _ in range(retries):
            match = re.search(pattern, get_text())
            current = int(match.group(1)) if match else -1
            if current == last and current != 0:
                return current
            last = current
            self.page.wait_for_timeout(interval_ms)
        return last if last is not None else -1

    def live_fleet_map_unit_count(self) -> int:
        # Confirmed live: the map widget shows "directions_car\n<n>" as
        # its own live fleet count, independent of any page's own table.
        return self._read_stable_int(r"directions_car\s*\n?\s*(\d+)")

    def custom_option(self, name: str = None) -> Locator:
        # Confirmed live 2026-09-14: the dropdown panel opened by these
        # "can-select" comboboxes (Protocol/Unit/Metric/Mode/Chart Type,
        # across Settings/Trends/Report/Alerts/Unit) is NOT a native/
        # Material overlay with role=option items -- it's a plain inline
        # panel (`.tx-list-popup.cs-panel`) of `<div class="cs-option">`
        # elements with no ARIA role at all. get_by_role("option") never
        # matches these; it was instead silently matching a hidden
        # Google Translate widget's <option> tags present site-wide,
        # which made every "select the first option" call unreliable.
        # A separate multi-select variant ("can-multiselect", used by
        # Alerts' filter-drawer Protocol/Level/Unit) renders its own
        # panel as `.tx-list-popup.cms-panel` of `<label class=
        # "tx-list-item">` checkbox items instead -- matches either.
        options = self.page.locator(".cs-panel .cs-option, .cms-panel .tx-list-item")
        if name:
            return options.filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        return options

    def combobox_by_visible_label(self, label_text: str, container: Locator = None) -> Locator:
        # Confirmed live: some CAN form comboboxes (e.g. Trends/Report's
        # "Units" and "Metric" selects, and every filter-drawer select on
        # Alerts) aren't wired to their visible <label> via
        # aria-labelledby -- get_by_role(..., name=...) finds nothing for
        # them even though the label text is on screen right next to the
        # control. Same fallback already established in ReportsPage.
        # _combobox_by_label: try the accessible name first, then fall
        # back to the nearest mat-form-field wrapper containing that
        # visible label text. `container` scopes the search (e.g. to a
        # filter drawer) when the same label appears more than once on
        # the page (main form + drawer both showing "Protocol").
        scope = container or self.page
        named = scope.get_by_role("combobox", name=label_text).first
        if named.count() > 0 and named.is_visible():
            return named
        field = scope.locator("mat-form-field, .mat-mdc-form-field").filter(
            has_text=re.compile(rf"\b{re.escape(label_text)}\b")
        ).first
        combobox = field.locator("[role='combobox'], mat-select").first
        if combobox.count() > 0:
            return combobox
        # Confirmed live: some of these multiselects (e.g. Trends/Report's
        # "Units") are a custom searchable-select trigger built from a
        # plain <input>, not a real mat-select/role=combobox.
        input_trigger = field.locator("input").first
        if input_trigger.count() > 0:
            return input_trigger
        # Confirmed live: the filter-drawer selects have no mat-form-field
        # wrapper at all -- just a bare <label> ("Protocol"/"Level"/
        # "Unit") followed by a readonly placeholder input directly.
        label_el = scope.get_by_text(label_text, exact=True).first
        if label_el.count() > 0:
            sibling_input = label_el.locator("xpath=following::input[1]")
            if sibling_input.count() > 0:
                return sibling_input
        return field

    # ------------------------------------------------------------- common table pattern
    # Every CAN data page (Dashboard's unit table, Unit, Alerts, Settings'
    # rules table) shares the same export/print/copy row and "Search
    # table" searchbox -- confirmed live accessible names below (not the
    # raw icon-ligature text, which is what's visible but not what's
    # exposed as each button's accessible name).

    def export_button(self, format_name: str) -> Locator:
        # Confirmed live 2026-09-14: the real accessible name differs by
        # page -- Alerts/Settings/Unit use "Export to <Format>", but
        # Report uses "Export report to <Format>". Matches either.
        label_by_format = {"excel": "Excel", "csv": "CSV", "pdf": "PDF"}
        return self.page.get_by_role("button", name=re.compile(rf"Export (report )?to {label_by_format[format_name]}", re.I))

    def print_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile("Print", re.I))

    def copy_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile("Copy", re.I))

    def search_table(self, query: str):
        search_box = self.page.get_by_role("searchbox", name="Search table")
        self.wait_for_visible(search_box)
        search_box.fill(query)
        self.wait_for_loading_to_finish()

    def clear_table_search(self):
        self.search_table("")

    def refresh_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"Refresh", re.I))

    def apply_filter_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"Apply Filter", re.I))

    def filter_drawer(self) -> Locator:
        return self.page.locator(".cdk-overlay-container, [role='dialog']").filter(
            has_text=re.compile(r"(Reset|Apply)")
        ).last

    def reset_filter_button(self, drawer: Locator) -> Locator:
        # Confirmed live: real accessible name is "Reset filters", not
        # the plain visible "Reset" text.
        return drawer.get_by_role("button", name=re.compile("Reset filters", re.I))

    def apply_filter_submit_button(self, drawer: Locator) -> Locator:
        # Confirmed live: real accessible name is "Apply filters" (also
        # shared with the toolbar trigger button outside the drawer --
        # scoping to `drawer` here disambiguates them).
        return drawer.get_by_role("button", name=re.compile("Apply filters", re.I))

    # ------------------------------------------------------------- pagination (native <select>, matches ReportsPage's table pagination)

    def rows_per_page_select(self) -> Locator:
        return self.page.get_by_role("combobox", name="Rows per page")

    def change_rows_per_page(self, value: str):
        rows_combo = self.rows_per_page_select()
        self.wait_for_visible(rows_combo)
        rows_combo.select_option(label=value)
        self.wait_for_loading_to_finish()

    def click_next_page(self):
        self.safe_click(self.page.get_by_role("button", name="Next page"))
        self.wait_for_loading_to_finish()

    def click_previous_page(self):
        self.safe_click(self.page.get_by_role("button", name="Previous page"))
        self.wait_for_loading_to_finish()

    def click_first_page(self):
        self.safe_click(self.page.get_by_role("button", name="First page"))
        self.wait_for_loading_to_finish()

    def click_last_page(self):
        self.safe_click(self.page.get_by_role("button", name="Last page"))
        self.wait_for_loading_to_finish()

    def pagination_info(self) -> str:
        match = re.search(r"(\d+)\s*[–-]\s*(\d+)\s*/\s*(\d+)", self.visible_text())
        return match.group(0) if match else ""

    def pagination_total(self) -> int:
        return self._read_stable_int(r"/\s*(\d+)", source=self.pagination_info)
