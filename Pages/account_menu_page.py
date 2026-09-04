import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class AccountMenuPage(BasePage):
    """The global Account menu (avatar icon, top nav) and its 7 items.
    Confirmed live: opening it shows an "Account / Profile & preferences"
    panel with My Profile / Downloads / Support / Change Password
    (each a real role=button), a PREFERENCES section (Appearance /
    Language), and Sign Out.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: the account_circle icon itself is decorative
        # (aria-hidden="true", no tabindex) -- a mouse click on it still
        # works because it bubbles to its real parent, a genuine
        # <button type="button" mattooltip="Account"> with no visible
        # text/aria-label of its own (only a tooltip, which contributes to
        # accessible *description*, not *name*). Since it has no usable
        # accessible name, get_by_role(..., name=...) can't target it by
        # name -- but it IS still a real button, so scoping get_by_role
        # ("button") down to the one containing this icon keeps this
        # role-based rather than falling back to a raw CSS/XPath selector,
        # and (unlike the plain icon) is genuinely focusable/keyboard-
        # operable, which matters for keyboard-navigation tests.
        self.menu_trigger = page.get_by_role("button").filter(
            has=page.locator("mat-icon", has_text="account_circle")
        ).first
        self.my_profile_item = page.get_by_role("button", name=re.compile("My Profile"))
        self.downloads_item = page.get_by_role("button", name=re.compile("Downloads"))
        self.support_item = page.get_by_role("button", name=re.compile("Support"))
        self.change_password_item = page.get_by_role("button", name=re.compile("Change Password"))
        self.appearance_item = page.get_by_role("button", name=re.compile("Appearance"))
        self.language_item = page.get_by_role("button", name=re.compile("Language"))
        self.sign_out_item = page.get_by_role("button", name=re.compile("Sign Out"))

    def open(self):
        # Confirmed intermittent under sustained test-session load (the
        # same staging-server flakiness pattern documented elsewhere this
        # session) -- the menu occasionally doesn't open on the first
        # click. A reload + one retry reliably recovers it.
        self.menu_trigger.click()
        try:
            self.wait_for_visible(self.my_profile_item, timeout=8000)
            return
        except Exception:
            pass
        self.page.reload()
        self.wait_until_ready()
        self.menu_trigger.click()
        self.wait_for_visible(self.my_profile_item)

    def close(self):
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def is_open(self) -> bool:
        return self.my_profile_item.is_visible()

    def open_my_profile(self):
        self.open()
        self.my_profile_item.click()
        self.expect_path("/profile")

    def open_downloads(self):
        self.open()
        self.downloads_item.click()
        self.expect_path("/profile/downloads")

    def open_support(self):
        self.open()
        self.support_item.click()
        self.expect_path("/profile/support")

    def open_change_password(self):
        self.open()
        self.change_password_item.click()
        self.expect_path("/profile/change-password")

    def toggle_appearance(self):
        """Clicking Appearance toggles the theme immediately in place --
        confirmed live, no navigation, no separate dialog."""
        self.open()
        # Appearance sits in the PREFERENCES section, below My Profile/
        # Downloads/Support/Change Password -- confirmed live this can
        # still be rendering when open()'s wait (scoped to My Profile
        # only) resolves, so wait for this specific button too.
        self.wait_for_visible(self.appearance_item)
        self.appearance_item.click()
        self.page.wait_for_timeout(500)

    def current_theme(self) -> str:
        """Confirmed live: the theme class ("light" or "dark") is set
        directly on <html>."""
        html_class = self.page.evaluate("() => document.documentElement.className")
        return "dark" if "dark" in html_class else "light"

    def open_language_dialog(self):
        self.open()
        self.language_item.click()
        self.wait_for_visible(self.language_dialog())

    def language_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(has_text="Choose your preferred language")

    def select_language(self, language: str):
        """Confirmed live: the language control is a genuine native
        <select> (get_by_role("combobox") on it, select_option() to pick
        -- clicking its role="option" children doesn't work, they're not
        individually visible the way mat-option divs are). Selecting sets
        a `googtrans` cookie and adds a translated-ltr/-rtl class to
        <html> (the Google Translate widget's own signature) -- "English"
        is a real option in the list that clears both back to baseline.
        """
        self.open_language_dialog()
        self.language_dialog().get_by_role("combobox").select_option(label=language)
        self.page.wait_for_timeout(2500)

    def is_page_translated(self) -> bool:
        html_class = self.page.evaluate("() => document.documentElement.className")
        return "translated-ltr" in html_class or "translated-rtl" in html_class

    def sign_out(self):
        """Opens the confirmation dialog and confirms -- Sign Out is a
        two-step flow, confirmed live ("Are you sure you want to
        logout?" / Cancel / Logout)."""
        self.open()
        self.sign_out_item.click()
        self.wait_for_visible(self.sign_out_confirm_dialog())
        self.sign_out_confirm_dialog().get_by_role("button", name="Logout", exact=True).click()
        self.page.wait_for_timeout(1000)

    def sign_out_confirm_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(has_text="Are you sure you want to logout")

    def cancel_sign_out(self):
        self.open()
        self.sign_out_item.click()
        self.wait_for_visible(self.sign_out_confirm_dialog())
        self.sign_out_confirm_dialog().get_by_role("button", name="Cancel", exact=True).click()
        self.page.wait_for_timeout(500)
