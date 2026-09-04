import re
from playwright.sync_api import Page
from Pages.settings_page import SettingsListPage

PARAMETERS = [
    "Overspeed Limit",
    "Distance Range",
    "Idle Time Range",
    "Halt Time Range",
    "Harsh Acceleration",
    "Running Time Range",
    "Harsh Braking",
    "Rash Turning",
]


class DriverPerformancePage(SettingsListPage):
    """Driver Performance list + Configure Driver Performance dialog.
    Confirmed live against Settings > Driver Management > Driver Performance.
    """

    def __init__(self, page: Page):
        super().__init__(page, add_button_name="Configure Driver Performance")
        # the real button's accessible name is longer than the CSV's
        # "Configure Driver" shorthand -- match by substring instead.
        self.add_btn = page.get_by_role("button", name=re.compile("Configure Driver", re.I))

        self.dialog = page.get_by_role("dialog").filter(
            has=page.get_by_role("heading", name="Configure Driver Performance")
        )
        self.category_select = self.dialog.get_by_role("combobox", name="Category")
        self.parameter_checkboxes = {
            name: self.dialog.get_by_role("checkbox", name=name, exact=True) for name in PARAMETERS
        }
        self.cancel_btn = self.dialog.get_by_role("button", name="Cancel")
        self.save_btn = self.dialog.get_by_role("button", name="Save Configuration")

    def open_configure_form(self):
        self._wait_for_page_overlay_gone()
        self.add_btn.click()
        self.wait_for_visible(self.category_select)

    def _wait_for_page_overlay_gone(self):
        """A full-page loading overlay (z-100000000) can still be settling
        right after the list first renders (confirmed live -- intercepts
        the add-button click otherwise) and isn't caught by the generic
        spinner selectors wait_for_loading_to_finish() already checks.
        It can appear *after* this is called too, so briefly wait for it to
        show up before waiting for it to go -- not just check-then-skip.
        """
        overlay = self.page.locator("div.absolute.z-100000000, div[class*='z-100000000']")
        try:
            overlay.first.wait_for(state="visible", timeout=1000)
        except Exception:
            return
        overlay.first.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def available_categories(self) -> list[str]:
        self.category_select.click()
        options = [o.strip() for o in self.page.get_by_role("listbox", name="Category").get_by_role("option").all_inner_texts()]
        self.page.keyboard.press("Escape")
        return options

    def delete_configuration(self, category: str):
        """Delete the row for `category`, with a settle beat before
        confirming -- clicking the confirm button the instant it becomes
        visible could land mid dialog-open-animation and miss (confirmed
        live: the click silently no-op'd often enough to strand the
        account with an undeleted test category)."""
        self.delete_button(category).click()
        self.wait_for_visible(self.confirm_delete_btn)
        self.page.wait_for_timeout(400)
        self.confirm_delete_btn.click()
        self.wait_for_dialog_closed()
        self.row_containing(category).wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)

    def select_category(self, category: str):
        self.category_select.click()
        self.page.get_by_role("listbox", name="Category").get_by_role("option", name=category, exact=True).click()

    def select_parameter(self, parameter: str):
        self.parameter_checkboxes[parameter].check()
        self.page.wait_for_timeout(300)

    def deselect_parameter(self, parameter: str):
        self.parameter_checkboxes[parameter].uncheck()
        self.page.wait_for_timeout(300)

    def parameter_article(self, parameter: str):
        """The configuration card for a selected parameter -- matched by its
        visible heading text, which includes a unit suffix, e.g.
        'Overspeed Limit (In KM/H)'."""
        return self.dialog.locator("article").filter(has_text=parameter)

    def configure_parameter(self, parameter: str, **values: str):
        """Fill whichever inputs the parameter's article exposes.
        `values` keys match the real field labels, e.g.
        configure_parameter('Overspeed Limit', Limit='60', Count='2')
        configure_parameter('Distance Range', Minimum='10', Maximum='50').
        """
        article = self.parameter_article(parameter)
        for field_name, value in values.items():
            control = article.get_by_role("textbox", name=field_name).or_(
                article.get_by_role("spinbutton", name=field_name)
            )
            control.fill(str(value))

    def edit_button(self, category: str):
        """The list's Edit/Delete row buttons have no accessible name
        (confirmed live -- plain icon buttons), so they're addressed by
        column position: Edit is the second-to-last cell, Delete the last."""
        return self.row_containing(category).locator("td:nth-last-child(2) button")

    def delete_button(self, category: str):
        return self.row_containing(category).locator("td:last-child button")

    def close_dialog(self):
        if self.dialog.is_visible():
            self.cancel_btn.click()
            self.wait_for_dialog_closed()
