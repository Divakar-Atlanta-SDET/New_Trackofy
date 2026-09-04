import re

from playwright.sync_api import Locator, Page, TimeoutError


class BasePage:
    DEFAULT_TIMEOUT_MS = 15000
    SHORT_TIMEOUT_MS = 3000

    def __init__(self, page: Page):
        self.page = page

    def expect_url(self, url: str):
        self.page.wait_for_url(url, timeout=self.DEFAULT_TIMEOUT_MS)
        self.wait_until_ready()

    def expect_path(self, path: str):
        self.page.wait_for_url(re.compile(f".*{re.escape(path.rstrip('/'))}/?$"), timeout=self.DEFAULT_TIMEOUT_MS)
        self.wait_until_ready()

    def current_path(self) -> str:
        return re.sub(r"^https?://[^/]+", "", self.page.url) or "/"

    def is_on_path(self, path: str) -> bool:
        return re.search(f"{re.escape(path.rstrip('/'))}/?$", self.current_path()) is not None

    def wait_until_ready(self):
        self.page.wait_for_load_state("domcontentloaded")
        self.wait_for_visible(self.page.locator("body"))
        self.wait_for_loading_to_finish()

    def wait_for_loading_to_finish(self):
        loading_indicators = self.page.locator(
            ".mat-mdc-progress-spinner, mat-spinner, .spinner, .loading, [aria-busy='true']"
        )
        try:
            loading_indicators.first.wait_for(state="hidden", timeout=self.SHORT_TIMEOUT_MS)
        except TimeoutError:
            pass

    def type_into(self, locator: Locator, text: str, delay: int = 15):
        # Confirmed live: some Angular-bound fields (e.g. the Raise Ticket
        # comment textarea) don't register Playwright's fill() as real
        # input -- the control stays ng-pristine/ng-untouched and the
        # value never sticks, even though it's not disabled/readonly. Real
        # keystrokes via press_sequentially() work correctly.
        locator.click()
        locator.press_sequentially(text, delay=delay)

    def wait_for_visible(self, locator: Locator, timeout: int | None = None):
        locator.wait_for(state="visible", timeout=timeout or self.DEFAULT_TIMEOUT_MS)

    def wait_for_hidden(self, locator: Locator, timeout: int | None = None):
        locator.wait_for(state="hidden", timeout=timeout or self.DEFAULT_TIMEOUT_MS)

    def wait_for_texts(self, texts: list[str], timeout: int | None = None):
        self.page.wait_for_function(
            """expectedTexts => expectedTexts.every(text => document.body.innerText.includes(text))""",
            arg=texts,
            timeout=timeout or self.DEFAULT_TIMEOUT_MS,
        )

    def wait_for_any_text(self, texts: list[str], timeout: int | None = None):
        self.page.wait_for_function(
            """expectedTexts => expectedTexts.some(text => document.body.innerText.includes(text))""",
            arg=texts,
            timeout=timeout or self.DEFAULT_TIMEOUT_MS,
        )

    def wait_for_text_absent(self, text: str, timeout: int | None = None):
        self.page.wait_for_function(
            """unexpectedText => !document.body.innerText.includes(unexpectedText)""",
            arg=text,
            timeout=timeout or self.DEFAULT_TIMEOUT_MS,
        )

    def wait_for_body_pattern(self, pattern: str, timeout: int | None = None):
        self.page.wait_for_function(
            """patternSource => new RegExp(patternSource, 'im').test(document.body.innerText)""",
            arg=pattern,
            timeout=timeout or self.DEFAULT_TIMEOUT_MS,
        )

    def wait_for_dialog_closed(self):
        dialogs = self.page.locator("[role='dialog'], .mat-mdc-dialog-container, mat-dialog-container")
        try:
            dialogs.first.wait_for(state="hidden", timeout=self.DEFAULT_TIMEOUT_MS)
        except TimeoutError:
            pass

    def visible_text(self) -> str:
        self.wait_for_visible(self.page.locator("body"))
        return self.page.locator("body").inner_text()

    def contains_texts(self, texts: list[str]) -> bool:
        try:
            self.wait_for_texts(texts)
        except TimeoutError:
            return False
        body_text = self.visible_text()
        return all(text in body_text for text in texts)

    def contains_any_text(self, texts: list[str]) -> bool:
        try:
            self.wait_for_any_text(texts)
        except TimeoutError:
            return False
        body_text = self.visible_text()
        return any(text in body_text for text in texts)

    def opaque_background_luminance(self, locator: Locator) -> float:
        """Walks up from `locator` until it finds a non-transparent
        background (menus/dialogs/tables are often transparent wrappers
        over an ancestor that actually paints the surface color), and
        returns that color's average RGB channel value -- a cheap
        smoke-check signal for "did the theme actually apply here"
        without hardcoding any specific dark/light color."""
        return locator.evaluate(
            """el => {
                let node = el;
                while (node) {
                    const bg = getComputedStyle(node).backgroundColor;
                    const match = bg.match(/rgba?\\((\\d+), *(\\d+), *(\\d+)(?:, *([\\d.]+))?\\)/);
                    if (match) {
                        const alpha = match[4] === undefined ? 1 : parseFloat(match[4]);
                        if (alpha > 0) {
                            return (parseInt(match[1]) + parseInt(match[2]) + parseInt(match[3])) / 3;
                        }
                    }
                    node = node.parentElement;
                }
                return null;
            }"""
        )

    def validation_messages(self) -> list[str]:
        selectors = [
            "mat-error",
            ".mat-mdc-form-field-error",
            ".invalid-feedback",
            ".error",
            "[role='alert']",
            ".toast",
            ".mat-mdc-snack-bar-label",
        ]
        messages: list[str] = []
        for selector in selectors:
            elements = self.page.locator(selector)
            for index in range(elements.count()):
                element = elements.nth(index)
                if element.is_visible():
                    text = element.inner_text().strip()
                    if text:
                        messages.append(text)
        return list(dict.fromkeys(messages))
