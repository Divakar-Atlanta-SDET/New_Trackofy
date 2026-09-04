import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class ProfilePage(BasePage):
    """My Profile / Account page (/profile). Confirmed live sections:
    identity header (name/email/mobile/account-holder/Change Password),
    Profile Completion, Account Usage (Devices/SMS/Sub Users/Email cards),
    Personal & Preferences, Billing Information.
    """

    USAGE_CATEGORIES = ["Devices", "SMS", "Sub Users", "Email"]

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_text("Profile & Account", exact=True)
        self.change_password_button = page.get_by_role("button", name=re.compile("Change Password"))

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/profile")
        self.expect_path("/profile")
        self.wait_for_visible(self.heading)

    # ------------------------------------------------------------- identity header

    def account_holder_name(self) -> str:
        return self.page.get_by_text("Account holder", exact=True).locator(
            "xpath=preceding-sibling::*[1]"
        ).inner_text().strip()

    def profile_completion_percent(self) -> int:
        match = re.search(r"(\d+)%\s*\n?\s*Profile Completion", self.visible_text())
        return int(match.group(1)) if match else -1

    # ------------------------------------------------------------- account usage

    def usage_card(self, category: str) -> Locator:
        title = self.page.locator(".tx-card-title", has_text=re.compile(f"^{re.escape(category)}$"))
        return title.locator("xpath=ancestor::article[1]")

    def usage_remaining(self, category: str) -> int:
        card = self.usage_card(category)
        text = card.locator(".text-right").inner_text()
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else -1

    def usage_used_text(self, category: str) -> str:
        card = self.usage_card(category)
        return card.get_by_text(re.compile(r"\d+\s*used")).inner_text().strip()

    def usage_progress_percent(self, category: str) -> int:
        card = self.usage_card(category)
        bar = card.locator("[style*='width']").first
        style = bar.get_attribute("style") or ""
        match = re.search(r"width:\s*(\d+(?:\.\d+)?)%", style)
        return int(float(match.group(1))) if match else -1

    # ------------------------------------------------------------- personal & preferences / billing

    def field_value(self, label: str, index: int = 0) -> str:
        """Reads a labelled row's value under Personal & Preferences or
        Billing Information (e.g. field_value('Name'), field_value('Timezone')).

        Confirmed live: each row's value sits as a sibling immediately
        after a `.tx-card-meta` label element. But that label element's
        OWN exact text differs by section: Personal & Preferences' meta
        divs contain only the label text (e.g. "Email"), while Billing
        Information's meta divs also wrap a leading `<mat-icon>` next to a
        `<span>` holding the actual label text (e.g. "Company") -- so the
        div's own full text is "businessCompany", not "Company", and an
        exact match against the div itself fails there. get_by_text(...,
        exact=True) resolves to whichever is the innermost exact match in
        either shape (the bare div in one section, the inner span in the
        other), then walking up to the nearest `.tx-card-meta` ancestor
        (itself included) handles both uniformly. "Address" is the one
        label that legitimately appears twice (Personal & Preferences,
        then Billing Information, in that page order) -- pass index=1 for
        the Billing one.
        """
        candidates = self.page.get_by_text(label, exact=True)
        meta = None
        seen = 0
        for i in range(candidates.count()):
            ancestor = candidates.nth(i).locator("xpath=ancestor-or-self::*[contains(@class,'tx-card-meta')][1]")
            if ancestor.count() == 0:
                continue
            if seen == index:
                meta = ancestor
                break
            seen += 1
        if meta is None:
            return ""
        value_locator = meta.locator("xpath=following-sibling::*[1]")
        # Confirmed live (intermittent): Personal & Preferences / Billing
        # Information populate via a slower, separate call than the page
        # shell -- reading immediately after load occasionally caught a
        # transient "N/A" placeholder or an as-yet-unrendered sibling. Poll
        # briefly for real content instead of trusting the first read.
        last_value = ""
        for _ in range(10):
            if value_locator.count() > 0:
                last_value = value_locator.inner_text(timeout=3000).strip()
                if last_value and last_value != "N/A":
                    return last_value
            self.page.wait_for_timeout(500)
        return last_value
