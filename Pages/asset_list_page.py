from playwright.sync_api import Page
from components.search import SearchComponent
from components.pagination import PaginationComponent

class AssetListPage:
    def __init__(self, page: Page, config):
        self.page = page
        self.config = config
        self.search = SearchComponent(page)
        self.pagination = PaginationComponent(page)
        
        # add asset table locators
        self.table_header = page.locator("thead th")
        self.add_asset_button = page.get_by_role("button", name="add New Asset")
        self.view_asset_button = page.get_by_role("button", name="View asset")
        self.assign_asset_button = page.get_by_role("button", name="Assign asset")
        self.edit_asset_button = page.get_by_role("button", name="Edit asset")
        self.delete_asset_button = page.get_by_role("button", name="Delete asset")
        
        self.create_asset_heading = page.get_by_role("heading", name="Create Asset")
        
    def open_asset_list(self):
        self.page.goto(self.config["base_url"] + "/asset-management/assets")
        self.page.wait_for_load_state("networkidle")
        
    

            
        
        