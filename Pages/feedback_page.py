import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class FeedbackPage(BasePage):
    """The "Using New Trackofy?" feedback prompt and the full Feedback
    form dialog behind its "Give Feedback" link. Confirmed live: reached
    via a persistent floating "FEEDBACK" nav button present on /profile/*
    pages (not on /home) -- clicking it reliably surfaces the prompt on
    demand, rather than relying on an unknown/unobserved auto-trigger
    condition.
    """

    POSITIVE_TAGS = [
        "Faster loading", "Better UI/UX", "Dashboard improved",
        "Reports improved", "Tracking improved", "Settings easier",
    ]
    NEGATIVE_TAGS = [
        "Missing features", "Confusing flow", "Slow / lag",
        "Bugs / errors", "Map issues", "Report mismatch",
    ]

    def __init__(self, page: Page):
        super().__init__(page)
        self.feedback_nav_button = page.get_by_role("button", name=re.compile("FEEDBACK"))

    def open_prompt(self):
        self.feedback_nav_button.first.click()
        self.wait_for_visible(self.prompt())

    def prompt(self) -> Locator:
        # Confirmed live: unlike the full form, this small prompt is NOT
        # a CDK overlay dialog -- it's a plain fixed-position widget
        # (<p>/<div> text, no button/dialog roles at all) anchored near
        # the FEEDBACK nav trigger. With no role/label to key off of for
        # the whole card, walk up one level from its own heading text
        # (structural, not a raw class selector) to get a scoped
        # container for visibility/dismiss checks.
        return self.page.get_by_text("Using New Trackofy?", exact=True).locator("xpath=..")

    def dismiss_prompt(self):
        # "Dismiss" and "Give Feedback" render as plain text (a <p>), not
        # role=button -- get_by_text is the correct locator here, not a
        # role fallback.
        self.prompt().get_by_text("Dismiss", exact=True).click()

    def open_form_from_prompt(self):
        self.prompt().get_by_text("Give Feedback", exact=True).click()
        self.wait_for_visible(self.form())
        # Confirmed live: Mobile/Email pre-populate from the account
        # profile via a separate, slightly slower call than the dialog
        # shell (the same async-loading-race pattern seen elsewhere in
        # this app) -- poll briefly for the real value instead of
        # trusting the dialog's own visibility as "ready".
        for _ in range(10):
            if self.mobile_input().input_value().strip():
                break
            self.page.wait_for_timeout(300)

    def form(self) -> Locator:
        return self.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(has_text="Share your experience")

    def open_form(self):
        """Convenience: open the prompt, then go straight to the form."""
        self.open_prompt()
        self.open_form_from_prompt()

    def close_form_via_x(self):
        self.form().get_by_role("button", name="Close", exact=True).click()

    def version_button(self, version: str) -> Locator:
        return self.form().get_by_role("button", name=version, exact=True)

    def is_version_selected(self, version: str) -> bool:
        # Confirmed live: the selected version button carries the
        # mat-sys-primary border/background classes; unselected ones
        # carry mat-sys-outline-variant/surface-container-lowest instead.
        classes = self.version_button(version).get_attribute("class") or ""
        return "mat-sys-primary" in classes

    def star_button(self, n: int) -> Locator:
        return self.form().get_by_role("button", name=f"Set rating to {n}", exact=True)

    def set_rating(self, n: int):
        self.star_button(n).click()
        self.page.wait_for_timeout(300)

    def current_rating(self) -> int:
        # Confirmed live: clicking star N fills stars 1..N -- a filled
        # star's icon text is "star", an empty one is "star_border".
        count = 0
        for n in range(1, 6):
            if self.star_button(n).locator("mat-icon").inner_text().strip() == "star":
                count += 1
        return count

    def tag_button(self, label: str) -> Locator:
        return self.form().get_by_role("button", name=label, exact=True)

    def is_tag_selected(self, label: str) -> bool:
        # Confirmed live: a selected POSITIVE tag gets "tx-status-success"
        # (green); a selected NEGATIVE tag gets "tx-status-danger" (red)
        # instead -- check for either.
        classes = self.tag_button(label).get_attribute("class") or ""
        return "tx-status-success" in classes or "tx-status-danger" in classes

    def suggestions_textarea(self) -> Locator:
        return self.form().get_by_placeholder("What should we improve?")

    def suggestions_counter_text(self) -> str:
        match = re.search(r"(\d+)/(\d+)", self.form().inner_text())
        return match.group(0) if match else ""

    def attachment_file_input(self) -> Locator:
        return self.form().locator("input[type='file']")

    def choose_file_button(self) -> Locator:
        return self.form().get_by_role("button", name="Choose File")

    def mobile_input(self) -> Locator:
        return self.form().get_by_placeholder("10-digit number")

    def email_input(self) -> Locator:
        return self.form().get_by_placeholder("name@example.com")

    def cancel_button(self) -> Locator:
        return self.form().get_by_role("button", name="Cancel", exact=True)

    def submit_button(self) -> Locator:
        return self.form().get_by_role("button", name="Submit")
