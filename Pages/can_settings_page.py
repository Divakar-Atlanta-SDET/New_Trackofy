import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanSettingsPage(CanBasePage):
    """CAN > Settings (/can/settings) -- Alert Configuration form
    (create a threshold rule) and the Configured Alert Rules table.
    """

    COLUMNS = ["S.No", "Unit", "Metric", "Mode", "Warning", "Critical", "Notify", "Status", "Actions"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Alert Settings", exact=True)
        self.config_heading = page.get_by_role("heading", name="Alert Configuration", exact=True)
        self.rules_heading = page.get_by_role("heading", name="Configured Alert Rules", exact=True)

        self.warning_limit_input = page.get_by_role("textbox", name=re.compile("Warning Limit"))
        self.critical_limit_input = page.get_by_role("textbox", name=re.compile("Critical Limit"))
        self.application_checkbox = page.get_by_role("checkbox", name="Application", exact=True)
        self.email_checkbox = page.get_by_role("checkbox", name="Email", exact=True)
        # Confirmed live: the real accessible names are "Reset alert
        # configuration" / "Save alert setting", not the plain visible
        # "Reset"/"Save" text.
        self.reset_button = page.get_by_role("button", name=re.compile("Reset", re.I))
        self.save_button = page.get_by_role("button", name=re.compile("Save", re.I))

        self.table = page.get_by_role("table")

    @property
    def unit_select(self) -> Locator:
        return self.combobox_by_visible_label("Unit")

    @property
    def metric_select(self) -> Locator:
        return self.combobox_by_visible_label("Metric")

    @property
    def mode_select(self) -> Locator:
        return self.combobox_by_visible_label("Mode")

    @property
    def protocol_select(self) -> Locator:
        # Confirmed live 2026-09-14: unlike Unit/Metric/Mode, this one
        # isn't wired to its visible label at all -- get_by_role(name=)
        # matches zero elements even though "Protocol" is visibly on
        # screen. A property (not an __init__-time attribute) so the
        # fallback chain runs fresh against the real, loaded DOM each
        # time it's used, not once at construction before the form
        # has rendered.
        return self.combobox_by_visible_label("Protocol")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/settings")
        self.expect_path("/can/settings")
        self.wait_for_visible(self.heading)

    def configured_rule_count(self) -> int:
        return self._read_stable_int(r"(\d+)\s*\nrules")

    def select_protocol(self, protocol_name: str):
        self.safe_click(self.protocol_select)
        self.safe_click(self.custom_option(protocol_name))
        self.wait_for_loading_to_finish()

    def select_first_available_protocol(self) -> str:
        self.safe_click(self.protocol_select)
        option = self.custom_option().first
        self.wait_for_visible(option)
        name = option.inner_text()
        self.safe_click(option)
        self.wait_for_loading_to_finish()
        return name

    def select_unit(self, unit_name: str):
        self.safe_click(self.unit_select)
        self.safe_click(self.custom_option(unit_name))
        self.wait_for_loading_to_finish()

    def select_first_available_unit(self) -> str:
        self.safe_click(self.unit_select)
        option = self.custom_option().first
        self.wait_for_visible(option)
        name = option.inner_text()
        self.safe_click(option)
        self.wait_for_loading_to_finish()
        return name

    def select_metric(self, metric_name: str):
        self.safe_click(self.metric_select)
        self.safe_click(self.custom_option(metric_name))
        self.wait_for_loading_to_finish()

    def select_first_available_metric(self) -> str:
        self.safe_click(self.metric_select)
        option = self.custom_option().first
        self.wait_for_visible(option)
        name = option.inner_text()
        self.safe_click(option)
        self.wait_for_loading_to_finish()
        return name

    def select_mode(self, mode: str):
        self.safe_click(self.mode_select)
        self.safe_click(self.custom_option(mode))
        self.wait_for_loading_to_finish()

    def set_warning_limit(self, value: str):
        self.warning_limit_input.fill(value)

    def set_critical_limit(self, value: str):
        self.critical_limit_input.fill(value)

    def toggle_notify_application(self, check: bool = True):
        if check and not self.application_checkbox.is_checked():
            self.application_checkbox.check()
        elif not check and self.application_checkbox.is_checked():
            self.application_checkbox.uncheck()

    def toggle_notify_email(self, check: bool = True):
        if check and not self.email_checkbox.is_checked():
            self.email_checkbox.check()
        elif not check and self.email_checkbox.is_checked():
            self.email_checkbox.uncheck()

    def is_save_enabled(self) -> bool:
        return self.save_button.is_enabled()

    def save(self):
        self.safe_click(self.save_button)
        self.wait_for_loading_to_finish()

    def reset(self):
        self.safe_click(self.reset_button)
        self.wait_for_loading_to_finish()

    def rows(self) -> Locator:
        return self.table.last.locator("tbody tr")

    def row_count(self) -> int:
        if self.table.count() == 0:
            return 0
        return self.rows().count()

    def row_by_metric(self, metric_name: str) -> Locator:
        return self.rows().filter(has_text=metric_name)

    def row_status_toggle(self, row: Locator) -> Locator:
        return row.get_by_role("switch").or_(row.get_by_role("checkbox"))

    def row_delete_button(self, row: Locator) -> Locator:
        return row.get_by_role("button", name=re.compile("delete", re.I))

    def delete_confirm_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container, [role='dialog']").filter(has_text=re.compile("delete", re.I)).last

    def delete_rule(self, row: Locator):
        self.safe_click(self.row_delete_button(row))
        self.wait_for_visible(self.delete_confirm_dialog())
        self.safe_click(self.delete_confirm_dialog().get_by_role("button", name="Delete", exact=True))
        self.wait_for_dialog_closed()
        self.wait_for_loading_to_finish()

    def cell_values(self, column_index: int, max_rows: int = 20) -> list[str]:
        rows = self.rows()
        count = min(rows.count(), max_rows)
        values = []
        for i in range(count):
            cells = rows.nth(i).locator("td")
            if cells.count() > column_index:
                values.append(cells.nth(column_index).inner_text().strip())
        return values
