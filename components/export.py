from playwright.sync_api import Page

class ExportComponent:
    def __init__(self, page: Page):
        self.page = page
        
        self.export_button_excel = page.get_by_role("button", name="table_view")
        self.export_button_csv = page.get_by_role("button", name="description")
        self.export_button_pdf = page.get_by_role("button", name="picture_as_pdf")
        
    def export_to_excel(self):
        self.export_button_excel.click()
        
    def export_to_csv(self):
        self.export_button_csv.click()
        
    def export_to_pdf(self):
        self.export_button_pdf.click()
        
    