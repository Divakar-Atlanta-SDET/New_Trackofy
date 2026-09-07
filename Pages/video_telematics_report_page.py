import re
from datetime import date

from playwright.sync_api import Locator, Page

from Pages.video_telematics_page import VideoTelematicsBasePage


class VideoTelematicsReportPage(VideoTelematicsBasePage):
    """Video Telematics > Report (/video_telematics/report) -- historical
    ADAS/DMS alert reporting with notification and evidence data.

    Confirmed live (ADAS account): default filters (last 5 days, All
    Vehicles, All Alerts) return 89 real records, matching the design
    doc's own screenshot exactly. Confirmed live via a read-only probe
    (Bug_Report.md #40, broadened): the Vehicle and Alert Type filters
    are multi-selects that start with EVERY option already
    aria-selected="true" -- the same shared-component bug already
    pinned on the Alert Configuration list's Vehicle filter -- so a
    plain single click toggles an option OFF rather than isolating it.
    select_vehicle()/select_alert_type() below apply the same
    isolate-by-deselecting-others workaround used there.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Video Telematics Reports")
        self.filters_toggle = page.get_by_role("button", name=re.compile("Report Filters", re.I))
        self.clear_all_button = page.get_by_role("button", name="Clear All", exact=True)
        self.generate_button = page.get_by_role("button", name="Generate Report")
        # Confirmed live: positional, same convention as Alert/Playback --
        # none of these comboboxes has a stable accessible name of its own.
        self.vehicle_select = page.get_by_role("combobox").nth(0)
        self.alert_type_select = page.get_by_role("combobox").nth(1)
        self.notification_select = page.get_by_role("combobox").nth(2)
        self.report_data_select = page.get_by_role("combobox").nth(3)
        self.rows_per_page_select = page.get_by_label("Rows per page")
        self.from_date_input = page.get_by_label("From Date")
        self.to_date_input = page.get_by_label("To Date")
        self.search_input = page.get_by_placeholder("Search report...")
        self.table = page.get_by_role("table")
        self.first_page_button = page.get_by_role("button", name="First page")
        self.previous_page_button = page.get_by_role("button", name="Previous page")
        self.next_page_button = page.get_by_role("button", name="Next page")
        self.last_page_button = page.get_by_role("button", name="Last page")
        self.export_excel_button = page.get_by_role("button", name="Export report to Excel")
        self.export_csv_button = page.get_by_role("button", name="Export report to CSV")
        self.export_pdf_button = page.get_by_role("button", name="Export report to PDF")
        self.print_button = page.get_by_role("button", name="Print report")
        self.copy_button = page.get_by_role("button", name="Copy report")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/video_telematics/report")
        self.expect_path("/video_telematics/report")
        self.wait_for_visible(self.heading)

    def record_count(self) -> int:
        # "record" is singular when the count is exactly 1 (confirmed
        # live: "1\nrecord", not "1\nrecords") -- records? covers both.
        match = re.search(r"(\d+)\s*\n?\s*records?\b", self.visible_text())
        return int(match.group(1)) if match else -1

    def expand_filters(self):
        if "expand_more" in self.filters_toggle.inner_text():
            self.filters_toggle.click()
            self.page.wait_for_timeout(500)

    def collapse_filters(self):
        if "expand_less" in self.filters_toggle.inner_text():
            self.filters_toggle.click()
            self.page.wait_for_timeout(500)

    def generate(self):
        self.generate_button.click()
        self.page.wait_for_timeout(2500)

    def clear_all(self):
        self.clear_all_button.click()
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------- filters

    def _open_option_panel(self, combobox: Locator) -> Locator:
        combobox.click()
        self.page.wait_for_timeout(500)
        panel_id = combobox.get_attribute("aria-controls")
        return self.page.locator(f"#{panel_id}")

    def _isolate_multiselect_option(self, combobox: Locator, target: str, select_all: bool = False):
        # Confirmed live (Bug #40, broadened): this multi-select starts
        # with every option already aria-selected="true", so a plain
        # click on the target toggles it OFF instead of isolating it --
        # deselect every other selected option first, matching the
        # Alert Configuration list's own workaround for the same bug.
        # Fixed-index iteration is unsafe here: with 50+ options (Alert
        # Type), clicking one can reorder/re-render the list, silently
        # shifting which item a stale index now refers to. Instead,
        # re-scan fresh and fix exactly one mismatch per pass until the
        # panel converges to "only target selected".
        panel = self._open_option_panel(combobox)
        options = panel.get_by_role("option")
        max_passes = options.count() + 5
        for _ in range(max_passes):
            options = panel.get_by_role("option")
            mismatch = None
            for i in range(options.count()):
                option = options.nth(i)
                is_target = select_all or target in option.inner_text()
                is_selected = option.get_attribute("aria-selected") == "true"
                if is_target != is_selected:
                    mismatch = option
                    break
            if mismatch is None:
                break
            mismatch.click()
            self.page.wait_for_timeout(200)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def select_vehicle(self, vehicle_id: str):
        self._isolate_multiselect_option(self.vehicle_select, vehicle_id, select_all=(vehicle_id == "All Vehicles"))

    def select_alert_type(self, alert_name: str):
        self._isolate_multiselect_option(self.alert_type_select, alert_name, select_all=(alert_name == "All Alerts"))

    def select_notification(self, status: str):
        panel = self._open_option_panel(self.notification_select)
        panel.get_by_role("option", name=status, exact=True).click()
        self.page.wait_for_timeout(500)

    def select_report_data(self, option: str):
        panel = self._open_option_panel(self.report_data_select)
        panel.get_by_role("option", name=option, exact=True).click()
        self.page.wait_for_timeout(500)

    def _select_date(self, date_input: Locator, target: date):
        # Same readonly-mat-datepicker pattern as Playback's Date field,
        # scoped to this specific field's own calendar toggle (Report has
        # two date fields, From/To, each with its own popup trigger).
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)
        field = date_input.locator("xpath=ancestor::mat-form-field[1]")
        toggle = field.get_by_role("button", name="Open calendar")
        toggle.click()
        self.page.wait_for_timeout(600)
        today = date.today()
        months_diff = (target.year - today.year) * 12 + (target.month - today.month)
        nav_name = "Next month" if months_diff > 0 else "Previous month"
        nav_button = self.page.get_by_role("button", name=nav_name)
        for _ in range(abs(months_diff)):
            nav_button.click()
            self.page.wait_for_timeout(300)
        cells = self.page.get_by_role("gridcell")
        for i in range(cells.count()):
            cell = cells.nth(i)
            if cell.inner_text().strip() == str(target.day) and "mat-calendar-body-disabled" not in (cell.get_attribute("class") or ""):
                cell.click()
                break
        self.page.wait_for_timeout(400)
        # Confirmed live: From/To Date share one mat-date-range-input --
        # picking a day can leave the popup/backdrop open (range mode
        # expects a start+end click in one session), which then
        # intercepts the next unrelated click (e.g. Generate Report).
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def select_from_date(self, target: date):
        self._select_date(self.from_date_input, target)

    def select_to_date(self, target: date):
        self._select_date(self.to_date_input, target)

    # ------------------------------------------------------------- table

    def rows(self) -> Locator:
        return self.table.locator("tbody tr").filter(has_not_text=re.compile(r"no .*(found|records)", re.I))

    def row_vehicle_text(self, row: Locator) -> str:
        return row.locator("td").nth(1).inner_text().strip()

    def row_datetime_text(self, row: Locator) -> str:
        return row.locator("td").nth(2).inner_text().strip()

    def row_category_text(self, row: Locator) -> str:
        return row.locator("td").nth(3).inner_text().strip()

    def row_alert_text(self, row: Locator) -> str:
        return row.locator("td").nth(4).inner_text().strip()

    def row_notification_text(self, row: Locator) -> str:
        return row.locator("td").nth(6).inner_text().strip()

    def row_has_evidence(self, row: Locator) -> bool:
        # Confirmed live: the Location icon-button is always present (index
        # 0); rows with real evidence additionally have View/Snapshots/Play
        # icon-buttons (indices 1-3). "No Evidence" rows have only index 0.
        return row.get_by_role("button").count() > 1

    def open_view_evidence(self, row: Locator):
        row.get_by_role("button").nth(1).click()
        self.page.wait_for_timeout(1200)

    def open_view_snapshots(self, row: Locator):
        row.get_by_role("button").nth(2).click()
        self.page.wait_for_timeout(1200)

    def open_play_video(self, row: Locator):
        row.get_by_role("button").nth(3).click()
        self.page.wait_for_timeout(1200)

    def evidence_panel_visible(self) -> bool:
        return "SEVERITY" in self.visible_text() and "Delivery Status" in self.visible_text()

    def evidence_panel_header_text(self) -> str:
        # The evidence panel renders inline (not a scoped dialog element
        # we can locate directly), and the underlying report table stays
        # visible behind it -- so whole-page text always still contains
        # every row's own timestamp regardless of which panel is open.
        # Scope to just the panel's own header block (between its
        # "video_library" title icon and the "SEVERITY" section that
        # follows it) so integrity checks aren't fooled by the table.
        text = self.visible_text()
        start = text.rfind("video_library")
        end = text.find("SEVERITY", start) if start != -1 else -1
        return text[start:end] if start != -1 and end != -1 else ""

    def close_evidence_panel(self):
        close_btn = self.page.get_by_role("button", name=re.compile("^close$", re.I))
        if close_btn.count() > 0:
            close_btn.first.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

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
