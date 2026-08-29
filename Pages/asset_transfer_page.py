from playwright.sync_api import Page
from components.search import SearchComponent

class AssetTransferPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)
        self.export = ExportComponent(page)
        self.pagination = PaginationComponent(page)
        
        # Transfer page locators
        self.table_header = page.locator("thead th")
        self.add_new_transfer = page.get_by_role("button", name="New Transfer")
        
        
    def open_transfer_wizard(self):
        '''Open the transfer creation wizard.'''
        self.add_new_transfer.click()