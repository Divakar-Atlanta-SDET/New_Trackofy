from playwright.sync_api import Page

class Navbar:
    
    def __init__(self,page:Page):
        self.page = page
        
        self.application_icon = page.get_by_text("apps", exact=True).first
        self.asset_management_option = page.locator(":text('Asset Management')").first
        
        # For now only adding asset management will later add more 
    
    def click_application_icon(self):
        self.application_icon.click()
        
    def click_asset_management_option(self):
        self.asset_management_option.click()
        
    def navigate_to_asset_management(self):
        self.click_application_icon()
        self.click_asset_management_option()
        
        
        