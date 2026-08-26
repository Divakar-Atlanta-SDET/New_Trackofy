from playwright.sync_api import Page
from components.search import SearchComponent

class AssetCategoryPage:
    def __init__(self, page: Page,config):
        self.page = page
        self.config = config
        self.search = SearchComponent(page)
        
        # Category form locators
        self.add_category_button = page.get_by_role("button", name="add New Category")
        self.category_name_input = page.get_by_placeholder("Enter category name")
        self.category_name_required_validation_error = page.get_by_text("Category name is required.")
        self.category_name_length_validation_error = page.get_by_text("Minimum 3 characters required.")
        
        self.category_description_input = page.get_by_placeholder("Enter description")
        self.active_radio_button = page.get_by_label("Active")
        self.inactive_radio_button = page.get_by_label("Inactive")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.save_button = page.get_by_role("button", name="Save")
        # table locators
        self.edit_button = page.get_by_role("button", name="Edit category")
        self.delete_button = page.get_by_role("button", name="Delete category")
        self.confirm_delete_button = page.get_by_role("button", name="Delete").last


        
        
        
        
        
        
    def open_categories(self):
        self.page.goto(self.config["base_url"] + "/asset-management/categories")
        
    def create_category(self, name: str, description: str = "", active: bool = True):
        self.add_category_button.click()
        self.category_name_input.fill(name)
        self.category_description_input.fill(description)
        if active:
            self.active_radio_button.check()
        else:
            self.inactive_radio_button.check()
        self.save_button.click()
        
    
