import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage

PARAMETERS = ["distance", "halt time", "idle time", "running time"]


class VehiclePerformancePage(SettingsListPage):
    """Vehicle Performance list + Create/Update Unit Performance dialog.
    Confirmed live against Settings > Vehicle Management > Vehicle Performance.
    All four range parameters (Distance/Halt/Idle/Running Time) are always
    present with live default values -- unlike Driver Performance there is
    no parameter checklist to select first.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Configure Unit Performance")
        self.add_btn = page.get_by_role("button", name=re.compile("Configure Unit", re.I))

        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name="Create Unit Performance").or_(
                page.get_by_role("heading", name="Update Unit Performance")
            )
        )
        self.category_select = self.dialog.get_by_role("combobox", name="Category")
        self.min_sliders = {p: self.dialog.get_by_role("slider", name=f"Minimum {p}") for p in PARAMETERS}
        self.max_sliders = {p: self.dialog.get_by_role("slider", name=f"Maximum {p}") for p in PARAMETERS}
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")
        self.create_btn = self.dialog.get_by_role("button", name="Create Performance")
        self.update_btn = self.dialog.get_by_role("button", name="Update Performance")

    def open_configure_form(self):
        self.add_btn.click()
        self.wait_for_visible(self.category_select)

    def available_categories(self) -> list[str]:
        self.category_select.click()
        options = [
            o.strip()
            for o in self.page.get_by_role("listbox", name="Category").get_by_role("option").all_inner_texts()
        ]
        self.page.keyboard.press("Escape")
        return options

    def select_category(self, category: str):
        self.category_select.click()
        self.page.get_by_role("listbox", name="Category").get_by_role("option", name=category, exact=True).click()

    def _set_slider(self, slider, value: int):
        # Native range input sits visually hidden under Material's custom
        # slider UI (same as confirmed on the Tracking module) -- .fill()
        # fails the visibility check, so set the value via JS instead.
        slider.evaluate(
            "(el, value) => { "
            "const proto = Object.getPrototypeOf(el); "
            "Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, String(value)); "
            "el.dispatchEvent(new Event('input', {bubbles: true})); "
            "el.dispatchEvent(new Event('change', {bubbles: true})); }",
            value,
        )

    def read_slider_value(self, slider) -> int:
        return int(slider.get_attribute("aria-valuetext"))

    def read_slider_bounds(self, slider) -> tuple[int, int]:
        return int(slider.get_attribute("min")), int(slider.get_attribute("max"))

    def read_true_bounds(self, parameter: str) -> tuple[int, int]:
        """Each thumb's own `max`/`min` HTML attribute is dynamically capped
        by the *other* thumb's current position (confirmed live -- reading
        the min thumb's `max` returned 400, not the true 1000 upper bound
        shown in the UI hint text) -- the true fixed range is the min
        thumb's `min` paired with the max thumb's `max`."""
        true_min = int(self.min_sliders[parameter].get_attribute("min"))
        true_max = int(self.max_sliders[parameter].get_attribute("max"))
        return true_min, true_max

    def set_range(self, parameter: str, minimum: int, maximum: int):
        """Set a dual-thumb range slider. The min thumb's max attribute is
        capped by the current max thumb value (and vice versa) -- confirmed
        live -- so widen the far thumb first to avoid an invalid interim state."""
        if maximum >= self.read_slider_value(self.max_sliders[parameter]):
            self._set_slider(self.max_sliders[parameter], maximum)
            self._set_slider(self.min_sliders[parameter], minimum)
        else:
            self._set_slider(self.min_sliders[parameter], minimum)
            self._set_slider(self.max_sliders[parameter], maximum)

    def edit_button(self, category: str):
        """No accessible name on these row buttons (confirmed live, same as
        Driver Performance) -- addressed by column position."""
        return self.row_containing(category).locator("td:nth-last-child(2) button")

    def delete_button(self, category: str):
        return self.row_containing(category).locator("td:last-child button")

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()

    def delete_configuration(self, category: str):
        self.delete_button(category).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.page.wait_for_timeout(400)  # let the confirm dialog's open animation settle
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        self.row_containing(category).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
