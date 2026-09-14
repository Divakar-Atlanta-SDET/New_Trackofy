import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanReportPage(CanBasePage):
    """CAN > Reports (/can/report) -- Report Settings form (Protocol,
    Units/Devices, date/time range) and the generated report table.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Report", exact=True)
        self.settings_heading = page.get_by_role("heading", name="Report Settings", exact=True)
        self.generate_button = page.get_by_role("button", name=re.compile(r"Generate Report", re.I))
        self.from_date_calendar_button = page.get_by_role("button", name="Open calendar").first
        self.to_date_calendar_button = page.get_by_role("button", name="Open calendar").last
        self.from_time_button = page.get_by_role("button", name="Open timepicker options").first
        self.to_time_button = page.get_by_role("button", name="Open timepicker options").last
        self.result_table = page.get_by_role("table")
        self.no_data_text = page.get_by_text("No data", exact=False)

    @property
    def protocol_select(self) -> Locator:
        # Confirmed live 2026-09-14: not wired to its visible label at
        # all -- get_by_role(name=) matches zero elements. A property
        # (not an __init__-time attribute) so this -- and units_select
        # below -- resolve against the real, loaded Report page each
        # time, not once at construction time (which happens BEFORE
        # open() navigates here at all).
        return self.combobox_by_visible_label("Protocol")

    @property
    def units_select(self) -> Locator:
        return self.combobox_by_visible_label("Units")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/report")
        self.expect_path("/can/report")
        self.wait_for_visible(self.heading)

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

    def open_units_dropdown(self):
        self.safe_click(self.units_select)
        self.page.wait_for_timeout(400)

    def select_all_units(self):
        self.open_units_dropdown()
        select_all = self.page.get_by_role("checkbox", name=re.compile("Select All", re.I))
        if select_all.count() > 0:
            select_all.first.check()
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def select_units(self, unit_names: list[str]):
        self.open_units_dropdown()
        for unit_name in unit_names:
            self.safe_click(self.custom_option(unit_name))
            self.page.wait_for_timeout(300)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def is_generate_enabled(self) -> bool:
        return self.generate_button.is_enabled()

    def generate(self):
        self.safe_click(self.generate_button)
        result = self.result_table.or_(self.no_data_text)
        result.first.wait_for(state="visible", timeout=45000)

    def has_results_table(self) -> bool:
        return self.result_table.count() > 0 and self.result_table.first.is_visible()

    def has_no_data_message(self) -> bool:
        return self.no_data_text.count() > 0 and self.no_data_text.first.is_visible()

    def result_row_count(self) -> int:
        if not self.has_results_table():
            return 0
        return self.result_table.last.locator("tbody tr").count()

    def result_headers(self) -> list[str]:
        if not self.has_results_table():
            return []
        headers = self.result_table.last.locator("thead th")
        return [headers.nth(i).inner_text().strip() for i in range(headers.count()) if headers.nth(i).inner_text().strip()]
