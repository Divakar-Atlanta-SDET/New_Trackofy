from playwright.sync_api import Page

class CreateInstallationWizard:
    def __init__(self, page: Page):
        self.page = page
        
        # Create Installation Wizard Locators
        self.select_asset_dropdown = page.locator("mat-select[formcontrolname$='assetId']")
        self.vehicle_dropdown = page.locator("mat-select[formcontrolname$='vehicleId']")
        self.installed_on_date_input = page.get_by_label("Installed On")
        self.installed_by_input = page.get_by_label("Installed By")
        self.remarks_input = page.get_by_label("Remarks")
        
        # validation error locators
        self.asset_required_error = page.locator("mat-error:has-text('Asset is required')")
        self.vehicle_required_error = page.locator("mat-error:has-text('Vehicle is required')")
        self.installation_date_required_error = page.locator("mat-error:has-text('Installed date is required')")
        self.installed_by_required_error = page.locator("mat-error:has-text('Installed date is required')")
        
        # Button locators
        self.submit_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.close_button = page.get_by_role("button", name="Close installation")
        
    
    def select_asset(self, asset_name: str):
        '''Select an asset from the dropdown.'''
        self.select_asset_dropdown.click()
        self.page.get_by_role("option", name=asset_name).click()
    
    def select_vehicle(self, vehicle_name: str):
        '''Select a vehicle from the dropdown.'''
        self.vehicle_dropdown.click()
        self.page.get_by_role("option", name=vehicle_name).click()
    
    def enter_installed_on_date(self, installed_on_date: str):
        '''Enter the installed on date.'''
        self.installed_on_date_input.fill(installed_on_date)
    
    def enter_installed_by(self, installed_by: str):
        '''Enter the installed by.'''
        self.installed_by_input.fill(installed_by)
    
    def enter_remarks(self, remarks: str):
        '''Enter the remarks.'''
        self.remarks_input.fill(remarks)
    
    def click_submit(self):
        '''Click the submit button.'''
        self.submit_button.click()
    
    def click_cancel(self):
        '''Click the cancel button.'''
        self.cancel_button.click()
    
    def click_close(self):
        '''Click the close button.'''
        self.close_button.click()
    
    def create_installation(self, asset_name: str, vehicle_name: str, installed_on_date: str, installed_by: str, remarks: str):
        '''Create a new installation.'''
        self.select_asset(asset_name)
        self.select_vehicle(vehicle_name)
        self.enter_installed_on_date(installed_on_date)
        self.enter_installed_by(installed_by)
        self.enter_remarks(remarks)
        self.click_submit()