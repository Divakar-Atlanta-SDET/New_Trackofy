from playwright.sync_api import Page

class CreateMaintenanceWizard:
    def __init__(self, page: Page):
        self.page = page
        
        
        # Maintenance Wizard locators
        self.add_maintenance_heading = page.get_by_role("heading", name="Add Maintenance")
        self.select_asset_dropdown = page.locator("mat-select[formcontrolname$='assetId']")
        self.select_vendor_dropdown = page.locator("mat-select[formcontrolname$='vendorId']")
        self.maintenance_type = page.get_by_role("textbox", name="Maintenance Type")
        self.service_date = page.get_by_role("textbox", name="Service Date")
        self.next_service_date = page.get_by_role("textbox", name="Next Due Date")
        self.cost_amount = page.get_by_role("spinbutton", name="Cost Amount")
        self.notes = page.get_by_role("textbox", name="Notes")
        
        
        # validation Error messages
        self.asset_required_error = page.get_by_text("Asset is required")
        self.vendor_required_error = page.get_by_text("Vendor is required")
        self.maintenance_type_required_error = page.get_by_text("Maintenance type is required")
        self.service_date_required_error = page.get_by_text("Service date is required")
        self.cost_amount_required_error = page.get_by_text("Cost amount is required")
        
        # Buttons
        self.submit_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.close_wizard_button = page.get_by_role("button", name="Close maintenance dialog")
        self.update_button = page.get_by_role("button", name="Update")
        
    def close_wizard(self):
        '''
        Close the maintenance wizard dialog
        '''
        self.close_wizard_button.click()
        
        
    def select_asset(self, asset_name: str):
        '''
        Select an asset from the dropdown
        '''
        self.select_asset_dropdown.click()
        self.page.get_by_role("option", name=asset_name).click()
        
    def select_vendor(self, vendor_name: str):
        '''
        Select a vendor from the dropdown
        '''
        self.select_vendor_dropdown.click()
        self.page.get_by_role("option", name=vendor_name).click()
        
    def enter_maintenance_type(self, maintenance_type: str):
        '''
        Enter the maintenance type
        '''
        self.maintenance_type.fill(maintenance_type)
        
    def enter_service_date(self, service_date: str):
        '''
        Enter the service date
        '''
        self.service_date.fill(service_date)
        
    def enter_next_service_date(self, next_service_date: str):
        '''
        Enter the next service date
        '''
        self.next_service_date.fill(next_service_date)
        
    def enter_cost_amount(self, cost_amount: str):
        '''
        Enter the cost amount
        '''
        self.cost_amount.fill(cost_amount)
        
    def enter_notes(self, notes: str):
        '''
        Enter the notes
        '''
        self.notes.fill(notes)
        
    def click_submit(self):
        '''
        Click the submit button
        '''
        self.submit_button.click()
    
    def click_cancel(self):
        '''
        Click the cancel button
        '''
        self.cancel_button.click()
        
    def click_update(self):
        '''
        Click the update button
        '''
        self.update_button.click()
        
    def create_maintenance(self, asset_name: str, vendor_name: str, maintenance_type: str, service_date: str, cost_amount: str, notes: str):
        '''
        Create a maintenance record
        '''
        self.select_asset(asset_name)
        self.select_vendor(vendor_name)
        self.enter_maintenance_type(maintenance_type)
        self.enter_service_date(service_date)
        self.enter_cost_amount(cost_amount)
        self.enter_notes(notes)
        self.click_submit()
        
    
        
        