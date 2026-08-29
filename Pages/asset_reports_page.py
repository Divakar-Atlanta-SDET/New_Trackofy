from components.search import SearchComponent
from components.export import ExportComponent
from components.pagination import PaginationComponent

class AssetReportsPage:
    def __init__(self, page):
        self.page = page
        self.search = SearchComponent(page)
        self.export = ExportComponent(page)
        self.pagination = PaginationComponent(page)
        
        # Reports page locators
        self.table_header = page.locator("thead th")
        
        # Leaving this page for now because its still in development
        