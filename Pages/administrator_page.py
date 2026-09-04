import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from Pages.base_page import BasePage


class AdministratorPage(BasePage):
    GENERAL_PERMISSION_CATEGORIES = [
        "Driver",
        "Driver Management",
        "Route Management",
        "User",
        "Sensor Configuration",
        "Alert Configuration",
        "Vehicle Group",
        "Video Telematics",
    ]
    UNIT_PERMISSIONS = ["Change Advanced Settings", "Change Icon", "Manage Services"]

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: get_by_role works cleanly for this one.
        self.admin_nav_link = page.get_by_role("link", name="Administrator", exact=True)
        # Confirmed live: this button's visible text is "Add User" but its
        # real accessible name is "Create new user" -- get_by_role(name="Add User")
        # returns 0 matches for exactly that reason.
        self.add_user_button = page.get_by_role("button", name="Create new user")
        self.search_input = page.get_by_role("searchbox")
        # Confirmed live: this is a genuine native <select aria-label="Rows
        # per page">, not a custom Material overlay -- get_by_label +
        # select_option() is the right tool, not click-based option
        # selection (which resolves to the native <option> but reports it
        # as "not visible", since native select options render outside the
        # normal DOM layout).
        self.rows_per_page_select = page.get_by_label("Rows per page")
        self.next_page_button = page.get_by_role("button", name="Next page")
        self.previous_page_button = page.get_by_role("button", name="Previous page")
        self.first_page_button = page.get_by_role("button", name="First page")
        self.last_page_button = page.get_by_role("button", name="Last page")

    # ------------------------------------------------------------- navigation

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/home")
        self.wait_until_ready()
        # The generic wait_until_ready() (domcontentloaded + spinner-hidden)
        # isn't enough to guarantee the Angular SPA's nav bar is fully
        # hydrated yet -- clicking immediately after can silently miss
        # (confirmed live: the click landed on nothing, page stayed on
        # /home). Wait for the link itself to be actionable first.
        self.wait_for_visible(self.admin_nav_link)
        self.admin_nav_link.click()
        self.page.wait_for_url(re.compile(r"/administrator"), timeout=self.DEFAULT_TIMEOUT_MS)
        self.wait_until_ready()

    # ------------------------------------------------------------- user list

    def user_count_text(self) -> str:
        match = re.search(r"(\d+)\s*users?\b", self.visible_text())
        return match.group(1) if match else ""

    def user_rows(self) -> Locator:
        # Confirmed live: the "No users found" empty state also renders as
        # a <tr> inside tbody -- exclude it so an empty search doesn't
        # count as "1 result".
        return self.page.locator("table tbody tr").filter(has_not_text="No users found")

    def user_row(self, username: str) -> Locator:
        return self.user_rows().filter(has_text=username).first

    def row_username(self, row: Locator) -> str:
        # Confirmed live cell order: Sr No, User Name, Password, Status,
        # Created At, Permissions, Edit, Delete.
        return row.locator("td").nth(1).inner_text().strip()

    def open_add_user_wizard(self):
        self.add_user_button.click()
        self.wait_for_visible(self.wizard_dialog())

    def search(self, query: str):
        # Confirmed live: fill() alone does not trigger filtering (the
        # list stayed fully unfiltered with no error) -- an actual Enter
        # keypress is required.
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def clear_search(self):
        self.search_input.fill("")
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def matching_record_count(self) -> int:
        match = re.search(r"(\d+)\s*matching record", self.visible_text())
        return int(match.group(1)) if match else 0

    # Confirmed live: these row-action icon buttons DO have clean,
    # descriptive aria-labels -- "Show password", "Manage user
    # permissions", "Edit user", "Delete user".
    def permissions_button(self, username: str) -> Locator:
        return self.user_row(username).get_by_role("button", name="Manage user permissions")

    def edit_button(self, username: str) -> Locator:
        return self.user_row(username).get_by_role("button", name="Edit user")

    def delete_button(self, username: str) -> Locator:
        return self.user_row(username).get_by_role("button", name="Delete user")

    def toggle_password_visibility(self, username: str):
        # Confirmed live: this click/locator occasionally stalls for a
        # reason not fully isolated (reproduces intermittently even with
        # an otherwise-identical fresh page state) -- a full reload plus
        # one retry has reliably recovered it, and this is a one-off
        # interaction, not a behavior worth failing the whole test over.
        button = self.user_row(username).get_by_role("button", name="Show password")
        try:
            button.click(timeout=8000)
            return
        except PlaywrightTimeoutError:
            pass
        self.page.reload()
        self.wait_until_ready()
        self.user_row(username).get_by_role("button", name="Show password").click(timeout=15000)

    def password_cell_text(self, username: str) -> str:
        # Confirmed live cell order: Sr No, User Name, Password, ...
        cells = self.user_row(username).locator("td")
        return cells.nth(2).inner_text()

    def change_rows_per_page(self, value: str):
        self.rows_per_page_select.select_option(label=value)
        self.page.wait_for_timeout(800)

    def edit_units_dialog(self) -> Locator:
        # Confirmed live (Bug #28): this dialog's title is meant to be
        # "Edit Units for <clicked username>" but is currently bound to the
        # wrong user's data regardless of which row's Edit button is
        # clicked.
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(has_text="Edit Units for")

    # ------------------------------------------------------------- Permissions action (Edit menu/general/unit permission)

    def permissions_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(has_text="Permission Settings")

    def permissions_dialog_tab(self, tab_name: str) -> Locator:
        # Confirmed live: plain get_by_text(tab_name) is ambiguous here (it
        # also matches a "General permission"-labelled panel elsewhere in
        # the same overlay) -- the tab itself is a real role=button.
        return self.permissions_dialog().get_by_role("button", name=tab_name)

    def open_permissions_general_tab(self):
        self.permissions_dialog_tab("General permission").click()
        self.page.wait_for_timeout(800)

    def open_permissions_unit_tab(self):
        self.permissions_dialog_tab("Unit permission").click()
        self.page.wait_for_timeout(800)

    def permissions_dialog_select_menu_group(self, group_name: str):
        self.permissions_dialog().get_by_text(group_name, exact=True).first.click()
        self.page.wait_for_timeout(800)

    def save_permissions_dialog(self):
        self.permissions_dialog().get_by_role("button", name="Save", exact=True).click()
        self.wait_for_loading_to_finish()
        try:
            self.permissions_dialog().wait_for(state="hidden", timeout=10000)
        except PlaywrightTimeoutError:
            pass
        self.page.wait_for_timeout(1000)

    def permissions_expand_category(self, category: str):
        # Unlike the Create User wizard, this dialog's Unit Permission tab
        # doesn't always wrap its checkboxes in a collapsed accordion --
        # confirmed live the header sometimes isn't present at all (a flat
        # checkbox list instead). Only expand if a genuine accordion header
        # for this category actually exists; no-op otherwise.
        header = self.permissions_dialog().locator("mat-expansion-panel-header").filter(has_text=category)
        if header.count() > 0:
            header.first.locator(".mat-expansion-indicator").click()
            self.page.wait_for_timeout(600)

    def permissions_category_checkbox(self, category: str) -> Locator:
        return self.permissions_dialog().get_by_text(category, exact=True).first.locator(
            "xpath=ancestor::mat-checkbox[1]"
        )

    def permissions_open_vehicle_dropdown(self):
        self.permissions_dialog().get_by_role("combobox").first.click()
        self.page.wait_for_timeout(600)

    def permissions_select_vehicle(self, vehicle_id: str):
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()
        self.page.wait_for_timeout(500)

    def permissions_unit_permission_checkbox(self, permission_label: str) -> Locator:
        return self.permissions_dialog().get_by_text(permission_label, exact=True).first.locator(
            "xpath=ancestor::mat-checkbox[1]"
        )

    def close_permissions_dialog(self):
        close_btn = self.permissions_dialog().get_by_role("button", name="Close", exact=True)
        if close_btn.count() > 0:
            close_btn.click()
        else:
            self.permissions_dialog().locator("button").filter(has_text="close").first.click()
        self.page.wait_for_timeout(800)

    def close_edit_units_dialog(self):
        dialog = self.edit_units_dialog()
        cancel_btn = dialog.get_by_role("button", name="Cancel", exact=True)
        if cancel_btn.count() > 0:
            cancel_btn.click()
        else:
            dialog.locator("button").filter(has_text="close").first.click()
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------- delete confirm

    def delete_confirm_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text=re.compile(r"[Dd]elete"))

    def confirm_delete(self):
        self.delete_confirm_dialog().get_by_role("button", name="Delete", exact=True).click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def cancel_delete(self):
        self.delete_confirm_dialog().get_by_role("button", name="Cancel", exact=True).click()
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------- wizard shell

    def wizard_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text="Create User")

    def close_wizard(self):
        # Confirmed live: this icon-only button's "close" text comes from
        # an aria-hidden icon font ligature, so it has no computed
        # accessible name at all (get_by_role(name=...) matches 0
        # regardless of pattern) -- a genuine case where role-based
        # querying isn't possible, so this falls back to matching the
        # icon's literal text content directly.
        self.wizard_dialog().locator("button").filter(has_text="close").first.click()

    def cancel_wizard(self):
        self.wizard_dialog().get_by_role("button", name="Cancel", exact=True).click()

    def click_next_step(self):
        self.wizard_dialog().get_by_role("button", name="Next Step").click()
        # Step 1->2 makes a real save_subuser API call before advancing
        # (confirmed live) -- give it time rather than assuming an
        # instant client-side-only transition.
        self.page.wait_for_timeout(2000)

    def click_back(self):
        self.wizard_dialog().get_by_role("button", name="Back").click()
        self.page.wait_for_timeout(500)

    def click_submit(self):
        self.wizard_dialog().get_by_role("button", name="Submit").click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1500)

    def wizard_step_button(self, step_name: str) -> Locator:
        return self.wizard_dialog().get_by_role("button").filter(has_text=step_name)

    def wizard_error_toast_text(self) -> str:
        toasts = self.page.locator(".toast, .mat-mdc-snack-bar-label, [role='alert']")
        for i in range(toasts.count()):
            text = toasts.nth(i).inner_text()
            if text.strip():
                return text
        return ""

    # ------------------------------------------------------------- Step 1: Personal Info

    def vehicles_select(self) -> Locator:
        return self.wizard_dialog().get_by_role("combobox").first

    def open_vehicles_dropdown(self):
        self.vehicles_select().click()
        self.page.wait_for_timeout(600)

    def select_vehicle(self, vehicle_id: str):
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()

    def close_vehicles_dropdown(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def username_input(self) -> Locator:
        return self.wizard_dialog().get_by_placeholder("Enter user name")

    def password_input(self) -> Locator:
        return self.wizard_dialog().get_by_placeholder("Enter password")

    def confirm_password_input(self) -> Locator:
        return self.wizard_dialog().get_by_placeholder("Confirm password")

    def arm_disarm_radio(self, value: str) -> Locator:
        # value: "Yes" or "No"
        return self.wizard_dialog().get_by_role("radio", name=value, exact=True)

    def select_arm_disarm(self, value: str):
        self.arm_disarm_radio(value).click()

    def fill_step1(
        self,
        username: str,
        password: str,
        vehicle_ids: list[str],
        arm_disarm: str = "No",
    ):
        for vehicle_id in vehicle_ids:
            self.open_vehicles_dropdown()
            self.select_vehicle(vehicle_id)
        self.close_vehicles_dropdown()
        self.username_input().fill(username)
        self.password_input().fill(password)
        self.confirm_password_input().fill(password)
        self.select_arm_disarm(arm_disarm)
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------- Step 2: Menu Access

    def available_group(self, group_name: str) -> Locator:
        return self.wizard_dialog().get_by_text(group_name, exact=True).first

    def select_menu_group(self, group_name: str):
        self.available_group(group_name).click()
        self.page.wait_for_timeout(800)

    def add_group_button(self) -> Locator:
        return self.wizard_dialog().locator(":text-is('Add Group')").first.locator("xpath=ancestor::button[1]")

    def selected_group_menu_count(self) -> int:
        match = re.search(r"(\d+)\s*menus?\b", self.wizard_dialog().inner_text())
        return int(match.group(1)) if match else 0

    def add_group_dialogs(self) -> Locator:
        # Confirmed live (Bug #26): opening has an unindicated multi-second
        # delay, and each extra click before it appears stacks another
        # independent overlay-pane instance of this dialog -- filtering on
        # .cdk-overlay-pane (not the outer .cdk-overlay-container, which is
        # a single shared element) is what lets each stacked instance be
        # counted/closed individually.
        return self.page.locator(".cdk-overlay-pane").filter(has_text="Add New Menu Group")

    def close_add_group_dialog(self, index: int = 0):
        self.add_group_dialogs().nth(index).get_by_role("button", name="Cancel", exact=True).click()

    # ------------------------------------------------------------- Step 3: General Permission

    def permission_category_header(self, category: str) -> Locator:
        return self.wizard_dialog().get_by_text(category, exact=True).first

    def expand_permission_category(self, category: str):
        # Confirmed live (DOM dump): the category name text is actually the
        # *label of the category's own mat-checkbox*, nested inside the
        # mat-expansion-panel-header. Clicking that text toggles the
        # checkbox instead of expanding the panel (they only visually look
        # like one clickable row) -- the genuine expand/collapse trigger is
        # the chevron (.mat-expansion-indicator) elsewhere in the same
        # header row.
        self.wizard_dialog().locator("mat-expansion-panel-header").filter(
            has_text=category
        ).first.locator(".mat-expansion-indicator").click()
        self.page.wait_for_timeout(600)

    def permission_category_checkbox(self, category: str) -> Locator:
        # Confirmed live: role=checkbox matches the bare native <input>,
        # which has no descendant label text to filter/name by (get_by_role
        # name= and .filter(has_text=) both return 0 matches) -- the
        # wrapping <mat-checkbox> is where the label text actually lives,
        # so this uses get_by_text (exact, to avoid "Driver" also matching
        # "Driver Management") and walks up to the checkbox component.
        return self.wizard_dialog().get_by_text(category, exact=True).first.locator(
            "xpath=ancestor::mat-checkbox[1]"
        )

    def permission_item_checkbox(self, permission_label: str) -> Locator:
        return self.wizard_dialog().get_by_text(permission_label, exact=True).first.locator(
            "xpath=ancestor::mat-checkbox[1]"
        )

    def permission_category_count(self, category: str) -> int:
        header_text = self.permission_category_header(category).locator("xpath=..").inner_text()
        match = re.search(r"(\d+)\s*permissions?", header_text)
        return int(match.group(1)) if match else 0

    def is_checkbox_checked(self, checkbox: Locator) -> bool:
        # Confirmed live: <mat-checkbox> is a custom component, not a real
        # checkbox -- .is_checked() errors with "Not a checkbox or radio
        # button". Its checked state is reliably reflected in its own
        # class list instead ("mat-mdc-checkbox-checked").
        classes = checkbox.get_attribute("class") or ""
        return "mat-mdc-checkbox-checked" in classes

    # ------------------------------------------------------------- Step 4: Unit Permission

    def units_select(self) -> Locator:
        return self.wizard_dialog().get_by_role("combobox").first

    def open_units_dropdown(self):
        self.units_select().click()
        self.page.wait_for_timeout(600)

    def select_unit(self, vehicle_id: str):
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()

    def close_units_dropdown(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def unit_permission_checkbox(self, permission_label: str) -> Locator:
        return self.wizard_dialog().get_by_text(permission_label, exact=True).first.locator(
            "xpath=ancestor::mat-checkbox[1]"
        )

    # ------------------------------------------------------------- high-level orchestration

    def create_user(
        self,
        username: str,
        password: str,
        vehicle_ids: list[str],
        arm_disarm: str = "No",
        menu_group: str | None = None,
        toggle_general_permissions: list[str] | None = None,
        unit_ids: list[str] | None = None,
        toggle_unit_permissions: list[str] | None = None,
    ):
        """Drives the full 4-step Create User wizard and submits.
        Uses a fixed, known-good default (menu_group='example21') when not
        specified, matching the minimal-valid-path Phase 0 confirmed live.

        Confirmed live (isolated probe, zero prior clicks): General
        Permission and Unit Permission checkboxes start UNCHECKED by
        default for a new user (an opt-in model) -- `toggle_general_permissions`/
        `toggle_unit_permissions` are lists of names to CLICK, which GRANTS
        them (since they start denied), not revokes. An earlier version of
        this docstring claimed the opposite (checked-by-default); that was
        a false positive caused by a since-fixed bug in
        `expand_permission_category()`, which used to click the category's
        own checkbox (mistaking its label for an expand trigger) instead of
        genuinely expanding the accordion -- see that method's comment.
        """
        self.open_add_user_wizard()
        self.fill_step1(username, password, vehicle_ids, arm_disarm)
        self.click_next_step()

        self.select_menu_group(menu_group or "example21")
        self.click_next_step()

        for category in toggle_general_permissions or []:
            self.expand_permission_category(category)
            # mat-checkbox is a wrapping custom component, not a real
            # checkbox itself -- .check()/.uncheck() don't recognize it,
            # a plain .click() toggles it correctly.
            self.permission_category_checkbox(category).click()
        self.click_next_step()

        for vehicle_id in unit_ids or vehicle_ids:
            self.open_units_dropdown()
            self.select_unit(vehicle_id)
        self.close_units_dropdown()
        if toggle_unit_permissions:
            # The 3 unit-permission checkboxes live inside the collapsed
            # "Unit" accordion body -- unlike the category-level checkbox
            # above, these require genuine expansion to become clickable.
            self.expand_permission_category("Unit")
        for permission in toggle_unit_permissions or []:
            self.unit_permission_checkbox(permission).click()

        self.click_submit()
