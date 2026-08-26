from playwright.sync_api import Page
import re

class SideMenuAssetManagement:
    def __init__(self, page: Page):
        self.page = page
        
        self.asset_management_side_menu = page.locator("aside[aria-label$='Asset Management navigation']")
        self.asset_management_heading = page.get_by_text("Asset Management")
        self.dashboard = page.locator("span").filter(has_text="Dashboard").last
        
        # Asset Setup and all sub locators
        self.Asset_setup = page.get_by_role("button", name=re.compile(r"Asset Setup"))
        self.Categories = page.locator("a[title='Categories']")
        self.Asset_Types = page.locator("a[title='Asset Types']")
        self.Asset_Status = page.locator("a[title='Asset Status']")
        self.Units = page.locator("a[title='Units']")
        self.Brands = page.locator("a[title='Brands']")
        self.Vendors = page.locator("a[title='Vendors']")
        self.Document_Types = page.locator("a[title='Document Types']")
        
        # Assets Table
        self.Assets_Menu = page.locator("span").filter(has_text="Assets").first
        self.All_Assets = page.locator("a[title='All Assets']")
        
        # Vehicle Usage
        self.Vehicle_Usage = page.get_by_text("Vehicle Usage")
        self.Installations = page.get_by_text("Installations")
        self.Vehicle_Transfers = page.get_by_title("Vehicle Transfers")
        self.Maintenance = page.locator("span").filter(has_text="Maintenance").first
        
        # Asset Records
        self.Asset_Records = page.locator("span:has-text('Asset Records')")
        self.Warranty = page.locator("a[title='Warranty']")
        
        # Notifications
        self.Notifications = page.locator("span").filter(has_text="Notifications").nth(1)
        
        # Insights
        self.Insights = page.get_by_text("Insight")
        self.Reports = page.locator("a[title='Reports']")
        
        
    def navigate_to_dashboard(self):
        '''Navigate to the dashboard page.'''
        self.dashboard.click()
        
    def click_asset_setup(self):
        '''Click on the asset setup menu item.'''
        self.Asset_setup.click()
        
    def navigate_to_asset_setup_categories(self):
        '''Click on Asset Setup -> Categories'''
        self.click_asset_setup()
        self.Categories.click()
        
    def navigate_to_asset_setup_asset_types(self):
        '''Click on Asset Setup -> Asset Types'''
        self.click_asset_setup()
        self.Asset_Types.click()
        
    def navigate_to_asset_setup_asset_status(self):
        '''Click on Asset Setup -> Asset Status'''
        self.click_asset_setup()
        self.Asset_Status.click()
        
    def navigate_to_asset_setup_units(self):
        '''Click on Asset Setup -> Units'''
        self.click_asset_setup()
        self.Units.click()
        
    def navigate_to_asset_setup_brands(self):
        '''Click on Asset Setup -> Brands'''
        self.click_asset_setup()
        self.Brands.click()
        
    def navigate_to_asset_setup_vendors(self):
        '''Click on Asset Setup -> Vendors'''
        self.click_asset_setup()
        self.Vendors.click()
        
    def navigate_to_asset_setup_document_types(self):
        '''Click on Asset Setup -> Document Types'''
        self.click_asset_setup()
        self.Document_Types.click()
        
    def click_asset_menu(self):
        '''Click on the asset menu item.'''
        self.Assets_Menu.click()
        
    def navigate_to_assets_all_assets(self):
        '''Click on the all assets menu -> All Assets.'''
        self.click_asset_menu()
        self.All_Assets.click()
    
    def click_vehicle_usage(self):
        '''Click on the vehicle usage menu item.'''
        self.Vehicle_Usage.click()
        
    def navigate_to_vehicle_usage_installations(self):
        '''Click on the Vehicle Usage -> Installations.'''
        self.click_vehicle_usage()
        self.Installations.click()
        
    def navigate_to_vehicle_usage_vehicle_transfers(self):
        '''Click on the Vehicle Usage -> Vehicle Transfers.'''
        self.click_vehicle_usage()
        self.Vehicle_Transfers.click()
        
    def navigate_to_vehicle_usage_maintenance(self):
        '''Click on the Vehicle Usage -> Maintenance.'''
        self.click_vehicle_usage()
        self.Maintenance.click()
    
    def click_asset_records(self):
        '''Click on the asset records menu item.'''
        self.Asset_Records.click()
        
    def navigate_to_asset_records_warranty(self):
        '''Click on the asset records -> Warranty.'''
        self.click_asset_records()
        self.Warranty.click()
        
    def click_notifications(self):
        '''Click on the notifications menu item.'''
        self.Notifications.click()
        
    def click_insights(self):
        '''Click on the insights menu item.'''
        self.Insights.click()
        
    def navigate_to_insights_reports(self):
        '''Click on the insights -> Reports.'''
        self.click_insights()
        self.Reports.click()

        
    
        