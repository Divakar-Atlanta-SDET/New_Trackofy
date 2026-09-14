import re

from playwright.sync_api import Locator, Page

from Pages.can_page import CanBasePage


class CanTrendsPage(CanBasePage):
    """CAN > Trends (/can/trends) -- Data & Chart Settings form, the
    single-metric "Metric Trend (multi-unit)" chart, and the
    "Multi Parameter Comparison (multi-unit)" chart.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="CAN Trends", exact=True)
        self.settings_heading = page.get_by_role("heading", name="Data & Chart Settings", exact=True)
        self.metric_trend_heading = page.get_by_role("heading", name="Metric Trend (multi-unit)", exact=True)
        self.multi_param_heading = page.get_by_role("heading", name="Multi Parameter Comparison (multi-unit)", exact=True)

        self.show_markers_checkbox = page.get_by_role("checkbox", name=re.compile("Show Markers"))
        self.normalize_checkbox = page.get_by_role("checkbox", name=re.compile("Normalize"))
        self.apply_button = page.get_by_role("button", name=re.compile(r"^Apply"))

        self.from_date_calendar_button = page.get_by_role("button", name="Open calendar").first
        self.to_date_calendar_button = page.get_by_role("button", name="Open calendar").last
        self.from_time_button = page.get_by_role("button", name="Open timepicker options").first
        self.to_time_button = page.get_by_role("button", name="Open timepicker options").last

        self.smart_default_button = page.get_by_role("button", name="Smart Default")
        self.draw_comparison_button = page.get_by_role("button", name="Draw Comparison")

    @property
    def protocol_select(self) -> Locator:
        # Confirmed live 2026-09-14: not wired to its visible label at
        # all -- get_by_role(name=) matches zero elements. A property
        # (not an __init__-time attribute) so this -- and units_select/
        # metric_select below -- resolve against the real, loaded Trends
        # page each time, not once at construction time, which in this
        # class happens BEFORE open() navigates here at all.
        return self.combobox_by_visible_label("Protocol")

    @property
    def chart_type_select(self) -> Locator:
        # Confirmed live 2026-09-14: same missing-label-wiring gap as
        # Protocol/Units/Metric.
        return self.combobox_by_visible_label("Chart Type")

    @property
    def units_select(self) -> Locator:
        return self.combobox_by_visible_label("Units")

    @property
    def metric_select(self) -> Locator:
        return self.combobox_by_visible_label("Metric")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/can/trends")
        self.expect_path("/can/trends")
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

    def toggle_unit(self, unit_name: str):
        self.safe_click(self.custom_option(unit_name))
        self.page.wait_for_timeout(300)

    def close_units_dropdown(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def select_units(self, unit_names: list[str]):
        self.open_units_dropdown()
        for unit_name in unit_names:
            self.toggle_unit(unit_name)
        self.close_units_dropdown()

    def selected_unit_count(self) -> int:
        match = re.search(r"(\d+)\s+selected", self.units_select.inner_text())
        return int(match.group(1)) if match else 0

    def select_metric(self, metric_name: str):
        self.safe_click(self.metric_select)
        self.safe_click(self.custom_option(metric_name))
        self.wait_for_loading_to_finish()

    def select_chart_type(self, chart_type: str):
        self.safe_click(self.chart_type_select)
        self.safe_click(self.custom_option(chart_type))
        self.wait_for_loading_to_finish()

    def apply(self):
        self.safe_click(self.apply_button)
        self.wait_for_loading_to_finish()

    def metric_trend_placeholder_text(self) -> str:
        return self.contains_texts(["Select at least one unit and a metric"]) and "Select at least one unit and a metric" or ""

    def click_smart_default(self):
        self.safe_click(self.smart_default_button)
        self.wait_for_loading_to_finish()

    def click_draw_comparison(self):
        self.safe_click(self.draw_comparison_button)
        self.wait_for_loading_to_finish()

    def is_apply_enabled(self) -> bool:
        return self.apply_button.is_enabled()
