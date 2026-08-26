from playwright.sync_api import Page


class CreateTransferWizard:
    def __init__(self, page: Page):
        self.page = page

        # Transfer wizard locators
        self.select_asset_dropdown = page.locator("mat-select[formcontrolname$='assetId']")
        self.transfer_from = page.locator("mat-select[formcontrolname$='previousVehicleId']")
        self.transfer_to = page.locator("mat-select[formcontrolname$='newVehicleId']")
        self.transfer_date = page.get_by_label("Transfer Date") #Accepts MM/DD/YYYY format
        self.remarks = page.get_by_label("Remarks")
        
        # Button locators
        self.submit_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.close_button = page.get_by_role("button", name="Close transfer")
        
    def select_asset(self, asset_name: str):
        '''Select an asset from the dropdown.'''
        self.select_asset_dropdown.click()
        self.page.get_by_role("option", name=asset_name).click()
        
    def select_transfer_from(self, transfer_from: str):
        '''Select a transfer from vehicle from the dropdown.'''
        self.transfer_from.click()
        self.page.get_by_role("option", name=transfer_from).click()
        
    def select_transfer_to(self, transfer_to: str):
        '''Select a transfer to vehicle from the dropdown.'''
        self.transfer_to.click()
        self.page.get_by_role("option", name=transfer_to).click()
        
    def enter_transfer_date(self, transfer_date: str):
        '''Enter the transfer date.'''
        self.transfer_date.fill(transfer_date)
        
    def enter_remarks(self, remarks: str):
        '''Enter the remarks.'''
        self.remarks.fill(remarks)
        
    def submit_transfer(self):
        '''Submit the transfer.'''
        self.submit_button.click()
        
    def cancel_transfer(self):
        '''Cancel the transfer.'''
        self.cancel_button.click()
        
    def close_transfer(self):
        '''Close the transfer.'''
        self.close_button.click()
        
    def create_transfer(self, asset_name: str, transfer_from: str, transfer_to: str, transfer_date: str, remarks: str):
        '''Create a new transfer.'''
        self.select_asset(asset_name)
        self.select_transfer_from(transfer_from)
        self.select_transfer_to(transfer_to)
        self.enter_transfer_date(transfer_date)
        self.enter_remarks(remarks)
        self.submit_transfer()