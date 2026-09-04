import re

from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class HelpCenterPage(BasePage):
    """Help Center (/help-center), reached via the 9-dot app launcher.
    Confirmed live sections: a left "Contents" sidebar (its own mini
    search + Overview/Device/Sensor categories), a main area with
    Quick Links / Popular Sections / Common Issues, and the main
    "Search articles, guides and FAQs..." box.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_text("Help Center", exact=True).first
        self.home_button = page.get_by_role("button", name="Home", exact=True)
        self.main_search_input = page.get_by_placeholder("Search articles, guides and FAQs...")
        self.sidebar_search_input = page.get_by_placeholder("Search contents...")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/help-center")
        self.expect_path("/help-center")
        self.wait_for_visible(self.heading)
        # Confirmed live: the sidebar's Overview/Device/Sensor category
        # list populates via a separate, slightly slower call than the
        # page shell (the same async-loading-race pattern seen elsewhere
        # in this app) -- wait for real category text, not just the
        # heading, before treating the page as ready.
        self.page.get_by_role("button", name="Device", exact=True).wait_for(
            state="visible", timeout=self.DEFAULT_TIMEOUT_MS
        )

    def open_via_launcher(self):
        # Confirmed live: the "apps" grid icon opens a launcher panel that
        # includes a real "Help Center" option (get_by_text, not a role
        # locator -- confirmed live it isn't exposed as a button/link
        # role, only as plain clickable text inside the launcher panel).
        self.page.get_by_text("apps", exact=True).first.click()
        self.page.wait_for_timeout(500)
        self.page.get_by_text("Help Center", exact=False).first.click()
        self.expect_path("/help-center")

    def category_button(self, category: str) -> Locator:
        return self.page.get_by_role("button", name=category, exact=True)

    def quick_link_button(self, label: str) -> Locator:
        return self.page.get_by_role("button", name=label)

    def popular_section_button(self, label: str) -> Locator:
        return self.page.get_by_role("button", name=label)

    def common_issue_button(self, label: str) -> Locator:
        return self.page.get_by_role("button", name=label)

    def search(self, query: str):
        self.main_search_input.click()
        self.page.keyboard.type(query, delay=20)
        # Confirmed live: the "Search Results" panel has a real debounce/
        # network delay before "X found" or "No results found" renders --
        # poll rather than trust a single fixed wait.
        for _ in range(10):
            text = self.visible_text()
            if re.search(r"\d+\s*found", text) or "No results found" in text:
                return
            self.page.wait_for_timeout(500)

    def search_result_count(self) -> int:
        match = re.search(r"(\d+)\s*found", self.visible_text())
        return int(match.group(1)) if match else -1

    def is_no_results_shown(self) -> bool:
        return "No results found" in self.visible_text()

    def open_category_and_wait(self, category: str):
        self.category_button(category).click()
        # Confirmed live: the category's article list shows a "Loading
        # articles..." placeholder before resolving to the real list.
        try:
            self.wait_for_text_absent("Loading articles...", timeout=self.DEFAULT_TIMEOUT_MS)
        except Exception:
            pass
        self.wait_for_any_text(["Available Articles"], timeout=self.DEFAULT_TIMEOUT_MS)
