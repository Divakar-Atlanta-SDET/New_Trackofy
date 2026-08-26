from playwright.sync_api import Page


class ToastNotifications:
    def __init__(self, page: Page):
        self.page = page
        self.success_toast = page.locator("div.toast.success")
        self.error_toast = page.locator("div.toast.error")
        self.warning_toast = page.locator("div.toast.warning")
        self.info_toast = page.locator("div.toast.info")
        
    def get_toast_text(self):
        """Get the text content of the first visible toast message"""
        return (self.success_toast.text_content() or 
                self.error_toast.text_content() or 
                self.warning_toast.text_content() or 
                self.info_toast.text_content())
