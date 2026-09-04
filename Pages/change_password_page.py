import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class ChangePasswordPage(BasePage):
    """The two-stage Change Password page (/profile/change-password):
    Stage 1 verifies the current password, Stage 2 (New/Confirm, both
    genuinely `disabled` in the DOM until Stage 1 passes) sets the new one.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_text("Change Password", exact=True)
        # Confirmed live: New Password and Confirm New Password share the
        # SAME placeholder text ("Enter new password") -- their accessible
        # names (from the mat-form-field label) differ, so role+name is
        # the only reliable way to tell them apart.
        self.current_password_input = page.get_by_placeholder("Enter current password")
        self.new_password_input = page.get_by_role("textbox", name="New Password", exact=True)
        self.confirm_password_input = page.get_by_role("textbox", name="Confirm New Password")
        self.verify_button = page.get_by_role("button", name="Verify")
        self.update_button = page.get_by_role("button", name="Update Password")
        # Confirmed live: only the Current Password field's toggle carries
        # a real aria-label ("Toggle password visibility") -- the New/
        # Confirm toggles have none, so they can't be told apart by role
        # name alone. Scoping to each field's own mat-form-field ancestor
        # (structural, not a content selector) is the only way to target
        # them individually without falling back to a raw CSS index guess.
        self.current_password_toggle = page.get_by_role("button", name="Toggle password visibility")
        self.new_password_toggle = self._visibility_toggle_for(self.new_password_input)
        self.confirm_password_toggle = self._visibility_toggle_for(self.confirm_password_input)

    def _visibility_toggle_for(self, field_input: Locator) -> Locator:
        return field_input.locator("xpath=ancestor::mat-form-field[1]").get_by_role("button")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/profile/change-password")
        self.expect_path("/profile/change-password")
        self.wait_for_visible(self.heading)

    def verify_current_password(self, password: str):
        self.type_into(self.current_password_input, password)
        self.verify_button.click()
        self.page.wait_for_timeout(1500)

    def is_stage_two_unlocked(self) -> bool:
        return self.new_password_input.is_enabled()

    def requirement_items(self) -> Locator:
        return self.page.locator("li, div").filter(
            has_text=re.compile(r"^(8\+ characters|Uppercase letter|Lowercase letter|Number|Special character)$")
        )

    def error_toast_text(self) -> str:
        return self.page.locator(".mat-mdc-snack-bar-label, [role='alert'], .toast").first.inner_text()
