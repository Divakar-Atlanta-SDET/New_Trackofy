import re
import time
from datetime import datetime
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage
from data.reports import STANDARD_REPORT_NAMES, STANDARD_REPORTS

class ReportsPage(BasePage):
    MAX_REPORT_LOAD_SECONDS = 6.0
    REPORT_EXTRA_COMBOBOXES = {
        "Trip Report": ["Select Trip Type"],
        "Sensor Report": ["Select Sensor"],
        "BMS Summary Report": ["Select Parameter"],
        "BMS Cell Report": ["Select Report Type"],
        "ADAS Alarm Report": ["Select Alert Type"],
        "Alert": ["Alert Name"],
    }

    def __init__(self, page:Page):
        super().__init__(page)
        self.standard_tab = self.page.get_by_role("link", name="Standard")
        self.custom_tab = self.page.get_by_role("link", name="Custom")
        self.schedule_tab = self.page.get_by_role("link", name="Schedule")
        self.report_cards = self.page.locator(".relative.group.overflow-hidden, .relative.group")
        self.generate_buttons = self.page.get_by_role("button", name=re.compile(r"^Generate(?: report)?$"))
        self.new_button = self.page.get_by_role("button", name="New")
        self.report_search_box = self.page.get_by_placeholder(re.compile(r"Search Report|Search reports", re.IGNORECASE))
        self.result_table = self.page.get_by_role("table")
        self.no_data_text = self.page.get_by_text("No data", exact=False)
    
    def go_to_reports(self):
        self.page.goto("/reports/standard")
        self.wait_for_reports_page()

    def open_standard_reports(self):
        self.page.goto("/reports/standard")
        self.wait_for_reports_page()

    def open_custom_reports(self):
        self.page.goto("/reports/custom")
        self.expect_path("/reports/custom")
        self.wait_for_visible(self.new_button)
        self.wait_for_custom_reports_page()

    def open_schedule_reports(self):
        if self.is_on_path("/reports/scheduled"):
            self.page.reload()
        else:
            self.page.goto("/reports/scheduled")
        self.expect_path("/reports/scheduled")
        self.wait_for_schedule_reports_page()
        self.wait_for_schedule_list_loaded()

    def refresh_schedule_reports(self):
        self.page.reload()
        self.expect_path("/reports/scheduled")
        self.wait_for_schedule_reports_page()
        self.wait_for_schedule_list_loaded()

    def refresh(self):
        self.page.reload()
        self.wait_until_ready()

    def report_tabs_state(self) -> dict[str, bool]:
        self.wait_for_texts(["Standard", "Custom", "Schedule"])
        return {
            "Standard": self.standard_tab.is_visible(),
            "Custom": self.custom_tab.is_visible(),
            "Schedule": self.schedule_tab.is_visible(),
        }

    def open_reports_tab(self, tab_name: str):
        tab_map = {
            "Standard": (self.standard_tab, "/reports/standard"),
            "Custom": (self.custom_tab, "/reports/custom"),
            "Schedule": (self.schedule_tab, "/reports/scheduled"),
        }
        tab, expected_path = tab_map[tab_name]
        self.wait_for_visible(tab)
        tab.click()
        self.expect_path(expected_path)
        if tab_name == "Standard":
            self.wait_for_reports_page()
        elif tab_name == "Custom":
            self.wait_for_custom_reports_page()
        else:
            self.wait_for_schedule_reports_page()

    def wait_for_reports_page(self):
        self.expect_path("/reports/standard")
        self.wait_for_visible(self.report_search_box)
        self.wait_for_texts(["Standard", "Custom", "Schedule"])
        self.wait_for_any_text(STANDARD_REPORT_NAMES)

    def wait_for_custom_reports_page(self):
        self.expect_path("/reports/custom")
        self.wait_for_visible(self.new_button)
        self.wait_for_texts(["Standard", "Custom", "Schedule", "New"])

    def wait_for_schedule_reports_page(self):
        self.expect_path("/reports/scheduled")
        self.wait_for_visible(self.new_button)
        self.wait_for_texts(["Standard", "Custom", "Schedule", "New"])

    def search_report(self, report_name: str):
        self.wait_for_visible(self.report_search_box)
        self.report_search_box.fill(report_name)
        report_button = self.page.get_by_role("button", name=re.compile(rf"\b{re.escape(report_name)}\b")).first
        try:
            self.wait_for_visible(report_button, timeout=5000)
        except Exception:
            self.open_standard_reports()
            self._open_visible_category_for(report_name)
            self.report_search_box.evaluate(
                "(element, value) => element.value = value",
                report_name,
            )
    
    def report_search_value(self) -> str:
        return self.report_search_box.input_value()

    def standard_catalog_names(self) -> list[str]:
        found_report_names: list[str] = []
        self.report_search_box.fill("")
        self.wait_for_loading_to_finish()
        self.wait_for_standard_categories()
        self._collect_visible_standard_report_names(found_report_names)
        category_buttons = self.page.locator("button").filter(has_text=re.compile(r"\d+\s+reports?"))
        for index in range(1, category_buttons.count()):
            category_button = category_buttons.nth(index)
            if not category_button.is_visible():
                continue
            category_button.click()
            self.wait_for_loading_to_finish()
            self._collect_visible_standard_report_names(found_report_names)
        return found_report_names

    def _collect_visible_standard_report_names(self, found_report_names: list[str]):
        body_text = self.visible_text()
        for report_name in STANDARD_REPORT_NAMES:
            if report_name in body_text and report_name not in found_report_names:
                found_report_names.append(report_name)

    def expand_standard_report_categories(self):
        category_buttons = self.page.locator("button").filter(has_text=re.compile(r"\d+\s+reports"))
        for index in range(category_buttons.count()):
            button = category_buttons.nth(index)
            if not button.is_visible():
                continue
            button_text = button.inner_text()
            if "expand_more" in button_text:
                button.click()
                self.wait_for_loading_to_finish()

    def open_standard_report_form(self, report_name: str):
        self.wait_for_reports_page()
        self.open_standard_report_category_for(report_name)
        last_error = None
        for _ in range(3):
            report_title = self._standard_report_button(report_name)
            self.wait_for_visible(report_title)
            try:
                report_title.click()
                break
            except Exception as exc:
                last_error = exc
                self.wait_for_loading_to_finish()
        else:
            raise last_error or AssertionError(f"Could not open standard report form: {report_name}")
        self.wait_for_visible(self.page.get_by_text("Configure report filters", exact=True))
        self.wait_for_standard_report_form(report_name)

    def open_standard_report_category_for(self, report_name: str):
        self.report_search_box.fill("")
        self.wait_for_loading_to_finish()
        self.wait_for_standard_categories()
        try:
            self._standard_report_button(report_name)
            return
        except AssertionError:
            pass
        self._open_visible_category_for(report_name)

    def is_standard_report_available(self, report_name: str) -> bool:
        self.wait_for_reports_page()
        try:
            self.open_standard_report_category_for(report_name)
            self._standard_report_button(report_name)
            return True
        except AssertionError:
            return False

    def wait_for_standard_categories(self):
        self.page.wait_for_function(
            """() => {
                const text = document.body.innerText || '';
                return text.includes('Fleet Performance')
                    && text.includes('Trips & Movement')
                    && text.includes('Driver & Safety')
                    && text.includes('BMS & Sensors');
            }""",
            timeout=self.DEFAULT_TIMEOUT_MS,
        )

    def _open_visible_category_for(self, report_name: str):
        category_buttons = self.page.locator("button").filter(has_text=re.compile(r"\d+\s+reports?"))
        for index in range(category_buttons.count()):
            category_button = category_buttons.nth(index)
            if not category_button.is_visible():
                continue
            try:
                self._standard_report_button(report_name)
                return
            except AssertionError:
                pass
            category_button.click()
            self.wait_for_loading_to_finish()
            try:
                self._standard_report_button(report_name)
                return
            except AssertionError:
                pass
        raise AssertionError(f"Could not find report in current catalog: {report_name}")

    def _standard_report_button(self, report_name: str) -> Locator:
        report_buttons = self.page.get_by_role("button", name=re.compile(rf"\b{re.escape(report_name)}\b"))
        for index in range(report_buttons.count()):
            candidate = report_buttons.nth(index)
            if candidate.is_visible() and candidate.is_enabled():
                return candidate
        raise AssertionError(f"Could not find enabled report button in current catalog: {report_name}")

    def wait_for_standard_report_form(self, report_name: str):
        self.wait_for_texts([report_name, "Configure report filters", "Generate report"])

    def standard_report_form_has_fields(self, report_name: str, fields: list[str]) -> bool:
        expected_texts = [
            report_name,
            "Configure report filters",
            "Generate report",
            *[field.replace(" *", "") for field in fields],
        ]
        return self.contains_texts(expected_texts)

    def reset_form(self):
        self._first_visible(
            self.page.get_by_role("button", name="refresh"),
            self.page.get_by_role("button", name=re.compile(r"^(Reset|Clear|Refresh)$", re.IGNORECASE)),
            self.page.locator("button").filter(has_text=re.compile(r"(refresh|Reset|Clear)", re.IGNORECASE)),
            self.page.get_by_text("refresh", exact=True),
        ).click()
        self.wait_for_loading_to_finish()

    def is_submit_enabled(self) -> bool:
        fetch_button = self.page.get_by_role("button", name=re.compile(r"^Generate(?: report)?$"))
        self.wait_for_visible(fetch_button)
        return fetch_button.is_enabled()

    def field_value(self, label: str) -> str:
        field = self.page.get_by_role("textbox", name=label)
        if field.count() > 0:
            for index in range(field.count()):
                candidate = field.nth(index)
                if candidate.is_visible():
                    return candidate.input_value()
            return field.first.input_value()
        field = self.page.get_by_label(label, exact=False)
        for index in range(field.count()):
            candidate = field.nth(index)
            if candidate.is_visible():
                return candidate.input_value()
        return field.first.input_value()

    def _set_textbox_value(self, textbox, value: str):
        self.wait_for_visible(textbox)
        textbox.evaluate(
            """(element, newValue) => {
                element.removeAttribute('readonly');
                element.value = newValue;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
            }""",
            value,
        )

    def selected_report_type(self) -> str:
        body_text = self.page.locator("body").inner_text()
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            if line in {"Selected Report Type", "Configure report filters"} and index > 0:
                previous_line = lines[index - 1]
                for report_name in sorted(STANDARD_REPORT_NAMES, key=len, reverse=True):
                    if previous_line == report_name or report_name in previous_line:
                        return report_name
            if line == "Selected Report Type" and index + 1 < len(lines):
                next_line = lines[index + 1]
                for report_name in sorted(STANDARD_REPORT_NAMES, key=len, reverse=True):
                    if next_line == report_name or report_name in next_line:
                        return report_name
        for report_name in sorted(STANDARD_REPORT_NAMES, key=len, reverse=True):
            if report_name in body_text:
                return report_name
        return ""

    def _report_fields(self, report_name: str) -> list[str]:
        for report in STANDARD_REPORTS:
            if report["name"] == report_name:
                return report["fields"]
        return []

    def open_new_custom_report_modal(self):
        self.open_custom_reports()
        self.new_button.click()
        self.wait_for_visible(self.page.get_by_text("Create Custom Report", exact=True))

    def open_new_schedule_report_modal(self):
        self.open_schedule_reports()
        self.new_button.click()
        self.wait_for_visible(self.page.get_by_text("Create Schedule Report", exact=True))

    def schedule_entries(self) -> list[dict[str, str]]:
        self.wait_for_schedule_list_loaded()
        self.wait_for_loading_to_finish()
        lines = [line.strip() for line in self.page.locator("body").inner_text().splitlines() if line.strip()]
        body_text = "\n".join(lines)
        compact_pattern = re.compile(
            r"(?P<title>[A-Za-z][A-Za-z0-9 ]{2,60}?)\s+"
            r"(?P<frequency>Daily|Weekly|Monthly|Manual)\s*\|\s*"
            r"(?P<status>Sent|Pending)\s+"
            r"Delivery:?\s*(?P<delivery>\d{2}-\d{2}-\d{4},\s*\d{1,2}:\d{2}\s*[AP]M)",
            re.IGNORECASE,
        )
        compact_entries = [match.groupdict() for match in compact_pattern.finditer(body_text)]
        if compact_entries:
            return compact_entries

        entries: list[dict[str, str]] = []
        ignored_titles = {
            "Home",
            "Dashboard",
            "Unit",
            "Tracking",
            "Reports",
            "Settings",
            "Administrator",
            "Standard",
            "Custom",
            "Schedule",
            "Search Report",
            "New",
            "Map",
            "Hybrid",
            "Styled Map",
        }

        for delivery_index, line in enumerate(lines):
            if line != "Delivery" and not line.startswith("Delivery:"):
                continue
            delivery = line.replace("Delivery:", "", 1).strip()
            if not delivery and delivery_index + 1 < len(lines):
                delivery = lines[delivery_index + 1]

            frequency = ""
            status = ""
            title = ""
            frequency_index = -1
            for index in range(delivery_index - 1, max(delivery_index - 8, -1), -1):
                if not status:
                    status_match = re.search(r"\b(Sent|Pending)\b", lines[index], re.IGNORECASE)
                    if status_match:
                        status = status_match.group(1)
                if not frequency:
                    frequency_match = re.search(r"\b(Daily|Weekly|Monthly|Manual)\b", lines[index], re.IGNORECASE)
                    if frequency_match:
                        frequency = frequency_match.group(1)
                        frequency_index = index

            if frequency_index != -1:
                for title_index in range(frequency_index - 1, max(frequency_index - 8, -1), -1):
                    candidate = lines[title_index]
                    if candidate not in ignored_titles and candidate not in {"edit", "delete", "|", "repeat", "Schedule:"}:
                        title = candidate
                        break

            if title and frequency and status:
                entries.append(
                    {
                        "title": title,
                        "frequency": frequency,
                        "status": status,
                        "delivery": delivery,
                    }
                )
        return entries

    def schedule_count(self) -> int:
        return len(self.schedule_entries())

    def wait_for_schedule_list_loaded(self):
        self.wait_for_text_absent("Loading", timeout=45000)

    def wait_for_schedule_count_greater_than(self, previous_count: int, timeout: int = 60000):
        self.page.wait_for_function(
            """previousCount => {
                const text = document.body.innerText || '';
                const loadingSelectors = '.mat-mdc-progress-spinner, mat-spinner, .spinner, .loading, [aria-busy="true"]';
                const isVisible = element => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && style.visibility !== 'hidden' && element.getClientRects().length > 0;
                };
                const isLoading = text.includes('Loading') || Array.from(document.querySelectorAll(loadingSelectors)).some(isVisible);
                if (isLoading) return false;
                const entries = text.match(/Delivery:?\\s*\\n?\\s*\\d{2}-\\d{2}-\\d{4},\\s*\\d{1,2}:\\d{2}\\s*[AP]M/g) || [];
                return entries.length > previousCount;
            }""",
            arg=previous_count,
            timeout=timeout,
        )
        self.wait_for_schedule_list_loaded()

    def wait_for_schedule_count_less_than(self, previous_count: int, timeout: int = 60000):
        self.page.wait_for_function(
            """previousCount => {
                const text = document.body.innerText || '';
                const loadingSelectors = '.mat-mdc-progress-spinner, mat-spinner, .spinner, .loading, [aria-busy="true"]';
                const isVisible = element => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && style.visibility !== 'hidden' && element.getClientRects().length > 0;
                };
                const isLoading = text.includes('Loading') || Array.from(document.querySelectorAll(loadingSelectors)).some(isVisible);
                if (isLoading) return false;
                const entries = text.match(/Delivery:?\\s*\\n?\\s*\\d{2}-\\d{2}-\\d{4},\\s*\\d{1,2}:\\d{2}\\s*[AP]M/g) || [];
                return entries.length < previousCount;
            }""",
            arg=previous_count,
            timeout=timeout,
        )
        self.wait_for_schedule_list_loaded()

    def schedule_entry_titles(self) -> list[str]:
        self.wait_for_loading_to_finish()
        body_text = self.page.locator("body").inner_text()
        return re.findall(r"^([A-Za-z][A-Za-z0-9 ]+)\s*$", body_text, re.MULTILINE)

    def first_schedule_entry(self) -> dict[str, str] | None:
        entries = self.schedule_entries()
        return entries[0] if entries else None

    def open_first_schedule_edit(self):
        edit_button = self.page.get_by_text("edit", exact=True).first
        self.wait_for_visible(edit_button)
        edit_button.click()
        self.wait_for_visible(self.page.get_by_text("Schedule Report", exact=True))

    def delete_first_schedule_entry(self, previous_count: int | None = None):
        delete_icon = self.page.get_by_label("Delete report").first
        if delete_icon.count() == 0:
            delete_icon = self.page.get_by_text("delete", exact=True).first
        self.wait_for_visible(delete_icon)
        delete_icon.click()
        delete_button = self.page.get_by_role("button", name="Delete", exact=True).last
        self.wait_for_visible(delete_button)
        delete_button.click()
        self.wait_for_dialog_closed()
        self.wait_for_loading_to_finish()
        if previous_count is not None:
            self.wait_for_schedule_count_less_than(previous_count)

    def schedule_submit_enabled(self) -> bool:
        schedule_button = self.schedule_action_button()
        self.wait_for_visible(schedule_button)
        return schedule_button.is_enabled()

    def schedule_form_values(self) -> dict[str, str]:
        return {
            "vehicles": self._combobox_value("Select Vehicles"),
            "report_scope": self._combobox_value("Select Report Type"),
            "standard_report": self._combobox_value("Select Standard Report"),
            "frequency": self._combobox_value("Select Frequency"),
            "schedule_time": self._editable_combobox_value("Schedule Time"),
            "email_1": self.page.get_by_role("textbox", name="Email 1").input_value(),
        }

    def schedule_action_button(self):
        dialog = self.schedule_dialog()
        return dialog.get_by_role("button", name=re.compile(r"^(Schedule|Update|.*Schedule.*)$")).last

    def schedule_dialog(self):
        return self.page.locator("[role='dialog'], .mat-mdc-dialog-container, mat-dialog-container").filter(
            has_text=re.compile(r"(Create Schedule Report|Schedule Report)")
        ).first

    def _open_combobox_options(self, combobox_name: str):
        combobox = self._combobox_by_label(combobox_name)
        self.wait_for_visible(combobox)
        combobox.click()
        options = self.page.locator("[role='option'], mat-option, .mat-mdc-option")
        try:
            self.wait_for_visible(options.first, timeout=5000)
        except Exception:
            combobox.press("ArrowDown")
            self.wait_for_visible(options.first)
        return options

    def _combobox_value(self, combobox_name: str) -> str:
        combobox = self._combobox_by_label(combobox_name)
        self.wait_for_visible(combobox)
        text_lines = [line.strip() for line in combobox.inner_text().splitlines() if line.strip()]
        ignored = {combobox_name, f"{combobox_name}*", "Select"}
        values = [line for line in text_lines if line not in ignored and not line.startswith("Select ")]
        return values[-1] if values else ""

    def _editable_combobox_value(self, combobox_name: str) -> str:
        combobox = self._combobox_by_label(combobox_name)
        self.wait_for_visible(combobox)
        try:
            return combobox.input_value()
        except Exception:
            return self._combobox_value(combobox_name)

    def _combobox_by_label(self, combobox_name: str) -> Locator:
        named_combobox = self.page.get_by_role("combobox", name=combobox_name).first
        if named_combobox.count() > 0:
            return named_combobox

        label_text = re.sub(r"\s+\*$", "", combobox_name).strip()
        field = self.page.locator("mat-form-field, .mat-mdc-form-field").filter(
            has_text=re.compile(rf"\b{re.escape(label_text)}\b")
        ).first
        if field.count() > 0:
            combobox = field.locator("[role='combobox'], mat-select, input[role='combobox']").first
            if combobox.count() > 0:
                return combobox

        return self.page.get_by_role("combobox").filter(has_text=combobox_name).first

    def _textbox_by_label(self, textbox_name: str) -> Locator:
        named_textbox = self.page.get_by_role("textbox", name=textbox_name).first
        if named_textbox.count() > 0:
            return named_textbox

        field = self.page.locator("mat-form-field, .mat-mdc-form-field").filter(
            has_text=re.compile(rf"\b{re.escape(textbox_name)}\b")
        ).first
        if field.count() > 0:
            textbox = field.locator("input, textarea").first
            if textbox.count() > 0:
                return textbox

        return self.page.locator("input, textarea").filter(has_text=textbox_name).first

    def _visible_option_names(self) -> list[str]:
        options = self.page.locator("[role='option'], mat-option, .mat-mdc-option")
        self.wait_for_visible(options.first)
        names: list[str] = []
        for index in range(options.count()):
            option = options.nth(index)
            if option.is_visible():
                name = option.inner_text().strip()
                if name:
                    names.append(name)
        return names

    def _select_option(self, option_name: str):
        option = self.page.locator("[role='option'], mat-option, .mat-mdc-option").filter(has_text=option_name).first
        self.wait_for_visible(option)
        option.click()
        self.wait_for_loading_to_finish()

    def _option_names_for_combobox(self, combobox_name: str) -> list[str]:
        self._open_combobox_options(combobox_name)
        option_names = self._visible_option_names()
        self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()
        return option_names

    def _select_first_real_option(self, combobox_name: str, excluded_options: set[str] | None = None) -> str:
        excluded = {"Select All", "All", "No Data Found", *(excluded_options or set())}
        self._open_combobox_options(combobox_name)
        option_names = [
            option_name
            for option_name in self._visible_option_names()
            if option_name.strip() and option_name not in excluded and not option_name.startswith("Select ")
        ]
        if not option_names:
            self.page.keyboard.press("Escape")
            self.wait_for_loading_to_finish()
            raise AssertionError(f"No selectable options found for combobox: {combobox_name}")

        selected = option_names[0]
        self._select_option(selected)
        return selected

    def has_missing_option_data(self) -> bool:
        return self.contains_any_text(["No Data Found"])

    def _fill_textbox(self, textbox_name: str, value: str):
        textbox = self.page.get_by_role("textbox", name=textbox_name)
        self.wait_for_visible(textbox)
        textbox.fill(value)
        textbox.evaluate(
            """(element, currentValue) => {
                element.value = currentValue;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
            }""",
            value,
        )
        self.wait_for_loading_to_finish()

    def select_all_schedule_vehicles(self):
        vehicle_combo = self._combobox_by_label("Select Vehicles")
        self.wait_for_visible(vehicle_combo)
        vehicle_combo.click()
        select_all = self.page.get_by_role("checkbox", name="Select All")
        try:
            self.wait_for_visible(select_all, timeout=5000)
        except Exception:
            vehicle_combo.press("ArrowDown")
            self.wait_for_visible(select_all)
        select_all.check()
        try:
            self.page.locator(".cdk-overlay-backdrop").click(timeout=3000)
        except Exception:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def available_schedule_report_names(self, report_scope: str) -> list[str]:
        self.select_all_schedule_vehicles()
        self._open_combobox_options("Select Report Type")
        self._select_option(report_scope)

        report_combobox_name = (
            "Select Standard Report"
            if report_scope == "Standard Report"
            else "Select Custom Report"
        )
        try:
            self._open_combobox_options(report_combobox_name)
            report_names = self._visible_option_names()
            self.page.keyboard.press("Escape")
            self.wait_for_loading_to_finish()
        except Exception:
            selected_report = self._combobox_value(report_combobox_name)
            report_names = [selected_report] if selected_report else []
        return report_names

    def fill_schedule_report_form(
        self,
        *,
        report_scope: str,
        report_name: str,
        frequency: str,
        schedule_time: str,
        email_1: str,
        from_date: str | None = None,
        to_date: str | None = None,
        schedule_till_day_name: str | None = None,
    ):
        self.select_all_schedule_vehicles()

        if self._combobox_value("Select Report Type") != report_scope:
            self._open_combobox_options("Select Report Type")
            self._select_option(report_scope)

        if report_scope == "Standard Report":
            report_combobox_name = "Select Standard Report"
        else:
            report_combobox_name = "Select Custom Report"
        if self._combobox_value(report_combobox_name) != report_name:
            self._open_combobox_options(report_combobox_name)
            self._select_option(report_name)

        self._open_combobox_options("Select Frequency")
        self._select_option(frequency)

        if frequency == "Custom":
            self._fill_textbox("From", from_date or "")
            self._fill_textbox("To", to_date or "")
        elif schedule_till_day_name:
            self.page.get_by_role("button", name="Open calendar").click()
            target_day = int(schedule_till_day_name)
            today = datetime.now()
            target_date = today.replace(day=target_day)
            if target_day < today.day:
                if today.month == 12:
                    target_date = target_date.replace(year=today.year + 1, month=1)
                else:
                    target_date = target_date.replace(month=today.month + 1)
            calendar_day_label = f"{target_date.day} {target_date.strftime('%B %Y')}"
            calendar_day_button = self.page.get_by_role("button", name=calendar_day_label, exact=True)
            self.wait_for_visible(calendar_day_button)
            calendar_day_button.click()

        schedule_time_input = self.page.get_by_role("combobox", name="Schedule Time")
        if schedule_time_input.count() == 0:
            schedule_time_input = self._combobox_by_label("Schedule Time")
        self.wait_for_visible(schedule_time_input)
        schedule_time_input.fill(schedule_time)
        email_input = self._textbox_by_label("Email 1")
        self.wait_for_visible(email_input)
        email_input.fill(email_1)
        self.wait_for_loading_to_finish()

    def save_schedule_report(self, previous_count: int | None = None):
        schedule_button = self.schedule_action_button()
        self.wait_for_visible(schedule_button)
        schedule_button.click()
        self.wait_for_loading_to_finish()
        self.wait_for_dialog_closed()
        if previous_count is not None:
            self.wait_for_schedule_count_greater_than(previous_count)
        else:
            self.wait_for_schedule_list_loaded()

    def is_schedule_dialog_open(self) -> bool:
        return self.page.get_by_text(re.compile(r"(Create Schedule Report|Schedule Report)")).first.is_visible()

    def close_dialog(self):
        close_button = self.page.get_by_role("button", name="Close")
        if close_button.count() > 0 and close_button.first.is_visible():
            close_button.first.click()
            self.wait_for_dialog_closed()
            return

        close_icons = self.page.get_by_text("close", exact=True)
        for index in range(close_icons.count() - 1, -1, -1):
            icon = close_icons.nth(index)
            if icon.is_visible():
                icon.click()
                self.wait_for_dialog_closed()
                return

        self.page.keyboard.press("Escape")
        self.wait_for_dialog_closed()

    def select_report(self, report_number): 
        report_name = STANDARD_REPORT_NAMES[report_number - 1]
        self.open_standard_report_form(report_name)

    def apply_common_date_filters(self,start_date,end_date):
        start_date_input = self._first_visible(
            self.page.get_by_role("textbox", name="Start Date"),
            self.page.get_by_label("Start Date", exact=False),
        )
        end_date_input = self._first_visible(
            self.page.get_by_role("textbox", name="End Date"),
            self.page.get_by_label("End Date", exact=False),
        )
        self._set_textbox_value(start_date_input, start_date)
        self._set_textbox_value(end_date_input, end_date)
        self.wait_for_loading_to_finish()

    def select_vehicle(self,vehicle_name):
        vehicle_combo = self._vehicle_combobox()
        self.wait_for_visible(vehicle_combo)
        vehicle_combo.click()
        vehicle_option = self.page.get_by_role("option", name=vehicle_name).first
        self.wait_for_visible(vehicle_option)
        vehicle_option.click()
        try:
            self.page.locator(".cdk-overlay-backdrop").click(timeout=3000)
        except Exception:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def select_vehicle_by_combobox_name(self, combobox_name: str, vehicle_name: str):
        vehicle_combo = self.page.get_by_role("combobox", name=combobox_name).first
        self.wait_for_visible(vehicle_combo)
        vehicle_combo.click()
        vehicle_option = self.page.get_by_role("option", name=vehicle_name).first
        try:
            self.wait_for_visible(vehicle_option, timeout=5000)
            vehicle_option.click()
        except Exception:
            self.page.keyboard.press("Escape")
            self.wait_for_loading_to_finish()
            self._select_first_real_option(combobox_name)
            return
        try:
            self.page.locator(".cdk-overlay-backdrop").click(timeout=3000)
        except Exception:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def select_Driver(self,driver_name):
        self.page.get_by_role("combobox", name="Select Driver").locator("span").click()
        self.page.get_by_text(driver_name).nth(1).click()
        
    def select_all_vehicles(self):
        self._vehicle_combobox().locator("span").click()
        self.page.get_by_role("checkbox", name="Select All").click()
        self.page.locator(".cdk-overlay-backdrop").click()

    def set_time_interval_hours_minutes(self,hours,minutes): # for idle report
        self.page.get_by_label('Time Interval Hour', exact=True).fill(hours)
        self.page.get_by_label('Time Interval Minute', exact=True).fill(minutes)
        ignition_off = self.page.get_by_label('Ignition Off') 
        ignition_off.click()
        ignition_on = self.page.get_by_label('Ignition On') 
        ignition_on.click()

    def min_max_distance(self,min_distance,max_distance): # for distance chart report
        min_distance_field = self.page.get_by_label('Minimum Distance (km)', exact=True)
        min_distance_field.fill(min_distance)
        max_distance_field = self.page.get_by_label('Maximum Distance (km)', exact=True)
        max_distance_field.fill(max_distance)

    

    def click_fetch(self):
        fetch_button = self.page.get_by_role("button", name=re.compile(r"^Generate(?: report)?$"))
        self.wait_for_visible(fetch_button)
        fetch_button.click()

    def configure_standard_report(
        self,
        report_name: str,
        *,
        start_date: str,
        end_date: str,
        vehicle_name: str,
        driver_name: str,
    ):
        self.open_standard_report_form(report_name)
        report_fields = self._report_fields(report_name)

        if report_name == "Fleet Summary":
            self.select_vehicle(vehicle_name)
            return

        if report_name == "Driver Report":
            self.select_Driver(driver_name)
            self.apply_common_date_filters(start_date, end_date)
            return

        if report_name == "Driver Performance":
            self.apply_common_date_filters(start_date, end_date)
        elif report_name == "BMS Summary Report":
            self.select_vehicle_by_combobox_name("Select Vehicle", vehicle_name)
            self.apply_common_date_filters(start_date, end_date)
        elif report_name == "BMS Cell Report":
            self.select_vehicle_by_combobox_name("Select Vehicle", vehicle_name)
            self.apply_common_date_filters(start_date, end_date)
        elif report_name == "ADAS Alarm Report":
            self.select_vehicle_by_combobox_name("Select Vehicle", vehicle_name)
            self.apply_common_date_filters(start_date, end_date)
        else:
            self.select_vehicle(vehicle_name)
            self.apply_common_date_filters(start_date, end_date)

        if report_name == "Distance Chart":
            self.min_max_distance("0", "100")
        elif report_name == "Idle":
            self.set_time_interval_hours_minutes("0", "30")

        for combobox_name in self.REPORT_EXTRA_COMBOBOXES.get(report_name, []):
            if self.is_submit_enabled():
                break
            self._select_first_real_option(combobox_name)

        if not self.is_submit_enabled():
            for field_name in report_fields:
                if not field_name.startswith("Select "):
                    continue
                if field_name in {"Select Vehicles *", "Select Vehicle", "Select Driver"}:
                    continue
                if self.is_submit_enabled():
                    break
                try:
                    self._select_first_real_option(field_name)
                except Exception:
                    continue

    def generate_standard_report(
        self,
        report_name: str,
        *,
        start_date: str,
        end_date: str,
        vehicle_name: str,
        driver_name: str,
        measure_performance: bool = False,
    ) -> float | None:
        self.configure_standard_report(
            report_name,
            start_date=start_date,
            end_date=end_date,
            vehicle_name=vehicle_name,
            driver_name=driver_name,
        )
        if measure_performance:
            return self._measure_report_fetch(report_name)
        self.click_fetch()
        self.wait_for_table()
        return None

    def click_back(self):
        self._first_visible(
            self.page.get_by_role("button", name="arrow_back"),
            self.page.get_by_text("arrow_back", exact=True),
            self.page.get_by_role("button", name="Close report panel"),
        ).click()
        self.wait_for_reports_page()

    def wait_for_table(self):
        result = self.page.get_by_role("table").or_(self.page.get_by_text("info", exact=True)).or_(self.page.get_by_text("No data", exact=False))
        result.first.wait_for(state="visible", timeout=45000)
        return True

    def standard_catalog_visible(self) -> bool:
        try:
            self.wait_for_visible(self.report_search_box)
        except Exception:
            return False
        return bool(self.standard_catalog_names()) and self.contains_any_text(
            ["Fleet Performance", "Trips & Movement", "Driver & Safety", "BMS & Sensors"]
        )

    def custom_catalog_visible(self) -> bool:
        return self.contains_texts(["New"]) and self.contains_any_text(["Generate", "edit", "delete"])

    def schedule_catalog_visible(self) -> bool:
        return self.contains_texts(["New"]) and self.contains_any_text(["Delivery", "No scheduled reports", "No data"])

    def has_results_table(self) -> bool:
        return self.result_table.count() > 0 and self.result_table.first.is_visible()

    def has_no_data_message(self) -> bool:
        return self.no_data_text.count() > 0 and self.no_data_text.first.is_visible()

    def has_info_result_state(self) -> bool:
        info = self.page.get_by_text("info", exact=True)
        return info.count() > 0 and info.first.is_visible()

    def report_download_notice(self) -> str:
        body_text = self.visible_text()
        match = re.search(
            r"([A-Za-z ]+ Report Downloaded)\s+Please find your downloaded report in the downloads page\.",
            body_text,
            re.MULTILINE,
        )
        return match.group(0).strip() if match else ""

    def result_table_headers(self) -> list[str]:
        if not self.has_results_table():
            return []
        header_text = self.result_table.locator("thead").inner_text()
        return [line.strip() for line in header_text.splitlines() if line.strip()]

    def result_row_count(self) -> int:
        if not self.has_results_table():
            return 0
        rows = self.result_table.locator("tbody tr")
        return rows.count()

    def result_surface(self) -> dict[str, object]:
        if self.has_results_table():
            return {
                "kind": "table",
                "headers": self.result_table_headers(),
                "row_count": self.result_row_count(),
                "message": "",
            }
        if self.has_no_data_message():
            return {"kind": "no_data", "headers": [], "row_count": 0, "message": ""}
        download_notice = self.report_download_notice()
        if download_notice:
            return {"kind": "download_notice", "headers": [], "row_count": 0, "message": download_notice}
        if self.has_info_result_state():
            return {"kind": "info", "headers": [], "row_count": 0, "message": ""}
        return {"kind": "missing", "headers": [], "row_count": 0, "message": ""}

    def _measure_report_fetch(self, report_label: str) -> float:
        start = time.perf_counter()
        self.click_fetch()
        self.wait_for_table()
        elapsed_seconds = round(time.perf_counter() - start, 3)
        print(f"{report_label} report loaded in {elapsed_seconds} seconds")
        return elapsed_seconds

    def fetch_and_measure_normal(self, report_number,start_date,end_date,vehicle_name):
        self.select_report(report_number)
        self.select_vehicle(vehicle_name)
        self.apply_common_date_filters(start_date,end_date)
        return self._measure_report_fetch("Normal")

    def fetch_and_measure_ditance_Chart(self, report_number,start_date,end_date,vehicle_name,min_distance,max_distance):
        self.select_report(report_number)
        self.select_vehicle(vehicle_name)
        self.apply_common_date_filters(start_date,end_date)
        self.min_max_distance(min_distance,max_distance)
        return self._measure_report_fetch("Distance Chart")

    def fetch_and_measure_idle(self, report_number,start_date,end_date,vehicle_name,hours,minutes):
        self.select_report(report_number)
        self.select_vehicle(vehicle_name)
        self.apply_common_date_filters(start_date,end_date)
        self.set_time_interval_hours_minutes(hours,minutes)
        return self._measure_report_fetch("Idle")

    def fetch_and_measure_fleet_summary(self, report_number,vehicle_name):
        self.select_report(report_number)
        self.select_vehicle(vehicle_name)
        return self._measure_report_fetch("Fleet Summary")

    def fetch_and_measure_driver_report(self, report_number, start_date, end_date,driver_name):
        self.select_report(report_number)
        self.select_Driver(driver_name)
        self.apply_common_date_filters(start_date, end_date)
        return self._measure_report_fetch("Driver Report")

    def fetch_and_measure_driver_performance(self, report_number, start_date, end_date):
        self.select_report(report_number)
        self.apply_common_date_filters(start_date, end_date)
        return self._measure_report_fetch("Driver Performance")

    def _first_visible(self, *locators: Locator) -> Locator:
        for locator in locators:
            if locator.count() == 0:
                continue
            candidate = locator.first
            if candidate.is_visible():
                return candidate
        for locator in locators:
            if locator.count() == 0:
                continue
            candidate = locator.first
            try:
                self.wait_for_visible(candidate, timeout=5000)
                return candidate
            except Exception:
                continue
        raise AssertionError("No visible locator matched the current report surface.")

    def _vehicle_combobox(self) -> Locator:
        return self._first_visible(
            self.page.get_by_role("combobox", name="Select Vehicles *"),
            self.page.get_by_role("combobox", name="Select Vehicles"),
            self.page.get_by_role("combobox", name="Select Vehicle"),
        )
