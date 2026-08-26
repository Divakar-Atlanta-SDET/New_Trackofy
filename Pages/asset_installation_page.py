from playwright.sync_api import Page
from components.search import SearchComponent

class AssetInstallationPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)

        # Installations page locators
        self.table_header = page.locator("thead th")
        self.add_installation_button = page.get_by_role("button", name="New Installation")
        self.delete_installation_button = page.get_by_role("button", name="Delete installation")
        self.confirm_delete_button = page.get_by_role("button", name="delete")
        
        
    def open_installation_wizard(self):
        '''Open the installation wizard.'''
        self.add_installation_button.click()
        
    def delete_installation(self):
        '''Delete an installation.'''
        self.delete_installation_button.nth(0).click()
        self.confirm_delete_button.last.click()
        
    def search_installation(self, search_term: str):
        '''Search for an installation.'''
        self.search.search_input.fill(search_term)