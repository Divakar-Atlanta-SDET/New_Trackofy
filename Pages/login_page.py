from playwright.sync_api import Page

from Pages.base_page import BasePage


class LoginPage(BasePage):
    """Public login page (/) -- confirmed live structure: split-screen
    layout, right side has the auth form (Username/Password, a Terms &
    Privacy checkbox checked by default, Sign in), Forgot password?,
    Help Center/Contact Support/Release Notes links, and mobile app
    store badges. Google Sign-In does NOT exist in the live app despite
    being described in the design doc -- confirmed with the user, not a
    probe artifact (no "Google" text/button anywhere, though a stray
    Google Identity Services `g_state` cookie is still set, suggesting
    the SDK is still loaded even though the UI entry point was removed).
    """

    def __init__(self, page: Page, config):
        super().__init__(page)
        self.config = config
        # locators
        self.heading = page.get_by_role("heading", name="Sign in to you account")
        self.username_input = page.get_by_placeholder("Enter username or email")
        self.password_input = page.get_by_placeholder("Enter password")
        self.login_btn = page.get_by_role("button", name="Sign in", exact=True)
        # Confirmed live: real aria-label, but tabindex="-1" (Bug #49,
        # Bug_Report.md) makes it unreachable via Tab despite this.
        self.password_toggle_btn = page.get_by_role("button", name="Toggle password visibility")
        self.terms_checkbox = page.get_by_role("checkbox")
        self.forgot_password_link = page.get_by_role("link", name="Forgot password?")
        self.help_center_link = page.get_by_role("link", name="Help Center")
        self.contact_support_link = page.get_by_role("link", name="Contact Support")
        self.release_notes_link = page.get_by_role("link", name="Release Notes")
        self.terms_link = page.get_by_role("link", name="Terms", exact=True).first
        self.privacy_link = page.get_by_role("link", name="Privacy", exact=True).first
        self.google_play_link = page.locator("a:has(img[alt='Google Play'])")
        self.app_store_link = page.locator("a:has(img[alt='App Store'])")

    def open(self):
        self.page.goto(self.config["base_url"])

    def enter_username(self, username: str):
        self.username_input.fill(username)

    def enter_password(self, password: str):
        self.password_input.fill(password)

    def click_login(self):
        self.login_btn.click()

    def login(self, username: str, password: str):
        if "/home" in self.page.url:
            return
        try:
            self.username_input.wait_for(state="visible", timeout=10000)
            self.username_input.fill(username)
            self.password_input.fill(password)
            self.login_btn.click()
        except Exception:
            if "/home" in self.page.url:
                return
            raise

    def is_password_masked(self) -> bool:
        return self.password_input.get_attribute("type") == "password"

    def toggle_password_visibility(self):
        self.password_toggle_btn.click()
        self.page.wait_for_timeout(500)
