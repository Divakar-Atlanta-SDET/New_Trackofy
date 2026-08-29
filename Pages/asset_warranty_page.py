from playwright.sync_api import Page
from components.search import SearchComponent
from components.export import ExportComponent
from components.pagination import PaginationComponent

class AssetWarrantyPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)
        self.export = ExportComponent(page)
        self.pagination = PaginationComponent(page)
        
        # Warranty page locators
        self.table_header = page.locator("thead th")
        self.add_warranty_button = page.get_by_role("button", name="New Warranty")
        self.edit_warranty_button = page.get_by_role("button", name="Edit warranty")
        self.view_warranty_button = page.get_by_role("button", name="View warranty")
        
        # Warranty form locators
        self.select_asset_dropdown = page.locator("mat-select[formcontrolname$='assetId']")
        self.asset_name = page.get_by_role("textbox", name="Asset Name")
        self.warranty_number = page.get_by_role("textbox", name="Warranty Number")
        self.warranty_provider = page.get_by_role("textbox", name="Warranty Provider")
        # self.warranty_start_date = ()
        # self.warranty_expiry_date = () 
        
        # form buttons
        self.submit_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.close_button = page.get_by_role("button", name="Close warranty")
        self.update_button = page.get_by_role("button", name="Update")
        

        
        
    
    def open_warranty_wizard(self):
        '''Open the warranty creation wizard.'''
        self.add_warranty_button.click()
        
    def edit_warranty(self):
        '''Edit an existing warranty.'''
        self.edit_warranty_button.click()
        
    def view_warranty(self):
        '''View an existing warranty.'''
        self.view_warranty_button.click()
        
    def press_submit_warranty_button(self):
        '''Submit the warranty form.'''
        self.submit_button.click()
        
    def select_asset(self, asset_name: str):
        '''Select an asset from the dropdown.'''
        self.select_asset_dropdown.click()
        self.page.get_by_role("option", name=asset_name).click()
        
    def enter_warranty_number(self, warranty_number: str):
        '''Enter the warranty number.'''
        self.warranty_number.fill(warranty_number)
        
    def enter_warranty_provider(self, warranty_provider: str):
        '''Enter the warranty provider.'''
        self.warranty_provider.fill(warranty_provider)
        
    def enter_warranty_start_date(self, warranty_start_date: str):
        '''Enter the warranty start date.'''
        self.warranty_start_date.fill(warranty_start_date)
        
    def enter_warranty_expiry_date(self, warranty_expiry_date: str):
        '''Enter the warranty expiry date.'''
        self.warranty_expiry_date.fill(warranty_expiry_date)
        
    def press_cancel_warranty_button(self):
        '''Cancel the warranty form.'''
        self.cancel_button.click()
        
    def press_close_warranty_button(self):
        '''Close the warranty form.'''
        self.close_button.click()
        
    def press_update_warranty_button(self):
        '''Update the warranty form.'''
        self.update_button.click()
        
    