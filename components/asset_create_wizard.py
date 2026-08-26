from playwright.sync_api import Page


class AssetCreateWizard:

    def __init__(self, page: Page):
        self.page = page

        # Step 1 locators
        self.category = page.locator("mat-select[formcontrolname$='category']")
        self.asset_type = page.locator("mat-select[formcontrolname$='type']")
        self.brand = page.locator("mat-select[formcontrolname$='brand']")
        self.status = page.locator("mat-select[formcontrolname$='status']")
        self.asset_name = page.get_by_label("Asset Name")
        self.serial_number = page.get_by_label("Serial Number")
        # step 1 validation messages
        self.category_error_requrired_text = page.get_by_text("Category is required")
        self.asset_type_error_requrired_text = page.get_by_text("Asset type is required")
        self.asset_name_requrired_error = page.get_by_text("Asset name is required")
        self.asset_name_valid_error = page.get_by_text("Enter a valid asset name")
        self.asset_name_minimum_error = page.get_by_text("Minimum 2 characters required")
        self.serial_number_requrired_error = page.get_by_text("Serial number is required")
        
        # Step 2 locators
        self.add_custom_field_button = page.get_by_role("button", name="add Add Field")
        self.custom_field_input = page.get_by_role("textbox", name="Field Label")
        self.add_button = page.get_by_text("Add", exact=True)
        
        
        # Step 2 validation messages
        self.custom_field_required_error = page.get_by_text("Field label is required")
        
        # Step 3 locators
        self.vendors = page.locator("mat-select[formcontrolname$='vendor']")
        self.unit = page.locator("mat-select[formcontrolname$='unit']")
        

        # Navigation
        self.next_button = page.get_by_role("button", name="arrow_forward Next")
        self.previous_button = page.get_by_role("button", name="arrow_back Previous")
        self.save_button = page.get_by_role(
            "button",
            name="Save"
        )

    def enter_asset_name(self, name: str):
        self.asset_name.fill(name)

    def enter_serial_number(self, serial: str):
        self.serial_number.fill(serial)

    def enter_quantity(self, quantity: int):
        self.quantity.fill(str(quantity))

    def click_next(self):
        self.next_button.click()