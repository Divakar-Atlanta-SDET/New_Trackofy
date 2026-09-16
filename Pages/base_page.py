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
        self.hide_feedback_widget()

    def wait_for_skeleton_rows_to_clear(self, timeout_ms: int = 15000):
        """Admin Panel's PrimeNG tables render `.p-skeleton` placeholder
        rows while real data loads -- confirmed live on Manage User (which
        has accumulated 26,000+ rows from repeated test-data creation
        across this whole engagement) a table refresh/pagination click can
        leave skeleton rows on screen for 5+ seconds, well past a short
        fixed wait. Reading row text while skeletons are still showing
        returns blank cells, which looks like "record not found" even
        though the record is really there -- wait on this instead.

        Confirmed live 2026-09-16: skeleton rows don't render immediately
        on click (measured ~100ms delay) -- waiting for state="hidden"
        alone, called right after the click, sees zero matching elements
        and returns instantly (Playwright treats "no element" as already
        hidden), missing the real loading window entirely. Wait for them
        to actually appear first (a quick, best-effort check -- if the
        table responds fast enough that skeletons never show, that's fine
        too), then wait for them to clear."""
        skeleton = self.page.locator(".p-skeleton")
        try:
            skeleton.first.wait_for(state="visible", timeout=500)
        except TimeoutError:
            return
        try:
            skeleton.first.wait_for(state="hidden", timeout=timeout_ms)
        except TimeoutError:
            pass
        # Confirmed live: an immediate interaction right as the last
        # skeleton clears can still hit one more Angular re-render (e.g.
        # a delete-icon click reporting "element was detached from the
        # DOM, retrying" until it times out) -- a short settle wait avoids
        # racing that final paint.
        self.page.wait_for_timeout(400)

    def hide_feedback_widget(self):
        """Bug_Report.md #76: a fixed-position "FEEDBACK" widget (present on
        at least Dashboard, Unit, and Settings) can sit on top of real row
        controls that happen to render near 40% viewport height, blocking
        real clicks with no visual indication anything is in the way --
        confirmed live it blocks Settings row action buttons (Location,
        Vehicle Performance, Alert Configuration) whenever a target row
        lands there. force=True does not help (Playwright still reports the
        widget as the actionability blocker). A one-shot hide isn't enough
        -- Angular can re-render the widget later in the same page's life --
        so this installs a MutationObserver (once per page/navigation, via
        an id guard) that keeps re-hiding it. Called from
        wait_for_loading_to_finish(), already invoked before nearly every
        interaction across the framework, so this fixes every call site at
        once instead of patching each one individually.

        NOT applied on /profile/* pages: confirmed live this exact widget
        is the legitimate Feedback-prompt trigger there (Pages/feedback_page.py),
        not a stray overlay -- hiding it there would silently break a real
        feature instead of fixing a bug.
        """
        if "/profile" in self.page.url:
            return
        try:
            self.page.evaluate(
                """
                () => {
                    if (document.getElementById('__qa_hide_feedback_widget')) return;
                    const marker = document.createElement('meta');
                    marker.id = '__qa_hide_feedback_widget';
                    document.head.appendChild(marker);
                    const hideIt = () => {
                        document.querySelectorAll('div.fixed').forEach(el => {
                            const cls = el.className || '';
                            if (cls.includes('top-[40vh]') && cls.includes('right-0')) {
                                el.style.display = 'none';
                            }
                        });
                    };
                    hideIt();
                    new MutationObserver(hideIt).observe(document.body, {childList: true, subtree: true});
                }
                """
            )
        except Exception:
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
