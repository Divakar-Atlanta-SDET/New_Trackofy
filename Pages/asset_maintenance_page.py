from playwright.sync_api import Page
from components.search import SearchComponent
from components.export import ExportComponent
from components.pagination import PaginationComponent

class AssetMaintenancePage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)
        self.export = ExportComponent(page)
        self.pagination = PaginationComponent(page)
        
        # Maintenance page locators
        self.table_header = page.locator("thead th")
        self.add_maintenance_button = page.get_by_role("button", name="New Maintenance")
        self.edit_maintenace_button = page.get_by_role("button", name="Edit maintenance")
        
        
        
    def open_maintenance_wizard(self):
        '''Open the maintenance wizard.'''
        self.add_maintenance_button.click()
        
    def edit_maintenance(self):
        '''Edit a maintenance.'''
        self.edit_maintenace_button.click()
        
    def export_to_excel(self):
        '''Export the maintenance table to Excel.'''
        self.export.export_to_excel()
        
    def export_to_csv(self):
        '''Export the maintenance table to CSV.'''
        self.export.export_to_csv()
        
    def export_to_pdf(self):
        '''Export the maintenance table to PDF.'''
        self.export.export_to_pdf()
        
    def search_maintenance(self, search_text: str):
        '''Search for a maintenance.'''
        self.search.search(search_text)
        