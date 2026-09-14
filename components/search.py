from playwright.sync_api import Page

class SearchComponent:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.get_by_role("searchbox")

    def _wait_for_loading_to_finish(self):
        # Confirmed live (2026-09-13): wait_for_load_state("networkidle")
        # reliably times out (30s) on this app -- the shell has continuous
        # background polling (live tracking/alerts) that never goes fully
        # idle, so networkidle is the wrong signal here regardless of
        # whether the search itself completed instantly. Same
        # loading-indicator-based wait already used throughout
        # Pages/base_page.py's wait_for_loading_to_finish().
        loading_indicators = self.page.locator(
            ".mat-mdc-progress-spinner, mat-spinner, .spinner, .loading, [aria-busy='true']"
        )
        try:
            loading_indicators.first.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass

    def search(self, query: str):
        self.search_input.fill(query)
        self._wait_for_loading_to_finish()

    def clear_search(self):
        self.search_input.clear()
        self._wait_for_loading_to_finish()
        
    
