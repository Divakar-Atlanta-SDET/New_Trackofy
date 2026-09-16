import re

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
        # Confirmed live 2026-09-15: the real submit button reads "Transfer
        # Asset", not "Save" -- matched loosely so it survives minor label
        # tweaks without going stale silently again.
        self.submit_button = page.get_by_role("button", name=re.compile("Transfer Asset|Save", re.I))
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.close_button = page.get_by_role("button", name="Close transfer")
        
    def select_asset(self, asset_name: str):
        '''Select an asset from the dropdown.'''
        self.select_asset_dropdown.click()
        self.page.get_by_role("option", name=asset_name).click()

    def select_first_asset(self) -> str:
        '''Select whichever asset the account actually has first in the
        dropdown, and return its name -- avoids hardcoding a specific
        asset name that may not exist on every environment/account.'''
        self.select_asset_dropdown.click()
        option = self.page.get_by_role("option").first
        option.wait_for(state="visible", timeout=10000)
        name = option.inner_text().strip()
        option.click()
        return name

    def select_transfer_from(self, transfer_from: str):
        '''Select a transfer from vehicle from the dropdown.

        NOTE (2026-09-15): confirmed live that `transfer_from`
        (`mat-select[formcontrolname$='previousVehicleId']`) does not exist
        on the real current form -- the "current vehicle" an asset is
        transferring from is shown as read-only text ("Currently assigned
        to: X"), not a selectable dropdown. This method is stale; read the
        current vehicle from the page instead of calling this.'''
        self.transfer_from.click()
        self.page.get_by_role("option", name=transfer_from).click()

    def current_vehicle_text(self) -> str:
        '''The real replacement for "transfer from": reads the asset's
        current vehicle from the read-only "Currently assigned to: X" text
        shown after selecting an asset (confirmed live 2026-09-15).'''
        text = self.page.locator("text=Currently assigned to:").inner_text()
        return text.split(":")[-1].strip()

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