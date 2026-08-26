from playwright.sync_api import Page

class ExportComponent:
    def __init__(self, page: Page):
        self.page = page
        
        self.export_button_excel = page.locator("button[mattooltip$='Export to Excel']")
        self.export_button_csv = page.locator("button[mattooltip$='Export to CSV']")
        self.export_button_pdf = page.locator("button[mattooltip$='Export to PDF']")
        
    def export_to_excel(self):
        self.export_button_excel.click()
        
    def export_to_csv(self):
        self.export_button_csv.click()
        
    def export_to_pdf(self):
        self.export_button_pdf.click()
        
    