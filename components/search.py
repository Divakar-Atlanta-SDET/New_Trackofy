from playwright.sync_api import Page

class SearchComponent:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.get_by_role("searchbox")
        
    def search(self, query: str):
        self.search_input.fill(query)
        self.page.wait_for_load_state("networkidle")
        
    def clear_search(self):
        self.search_input.clear()
        self.page.wait_for_load_state("networkidle")
        
    
