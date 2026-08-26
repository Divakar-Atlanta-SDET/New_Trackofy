from playwright.sync_api import Page

class PaginationComponent:
    def __init__(self, page: Page):
        self.page = page
        
        self.rows_dropdown = page.locator("select[aria-label$='Rows per page']")
        self.previous_page_button = page.locator("button[mattooltip$='Previous page']")
        self.next_page_button = page.locator("button[mattooltip$='Next page']")
        self.first_page_button = page.locator("button[mattooltip$='First page']")
        self.last_page_button = page.locator("button[mattooltip$='Last page']")
        self.rows = page.locator('table tbody tr')
        
    def go_to_next_page(self):
        self.next_page_button.click()
        
    def go_to_previous_page(self):
        self.previous_page_button.click()
        
    def go_to_first_page(self):
        self.first_page_button.click()
        
    def go_to_last_page(self):
        self.last_page_button.click()
        
    def change_rows_per_page(self, rows: int):
        self.rows_dropdown.select_option(str(rows))
        self.page.wait_for_load_state("networkidle")
        
    def get_row_count(self):
        return self.rows.count()