from playwright.sync_api import Page
from components.search import SearchComponent

class AssetNotificationsPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)
        
        # page locators
        self.notifcation_filter = page.locator("mat-select[formcontrolname$='filter']")
        self.refresh_button = page.get_by_role("button", name="Refresh notifications")
        self.mark_as_read_button = page.get_by_role("button", name="done  Mark as read")
        self.unread_notification_heading = page.locator(".tx-data-count").first
        self.total_notification_count = page.locator(".tx-data-count").nth(1)
        self.unread_notifications_count = page.locator(".tx-data-count").nth(2)
        self.read_notification_count = page.locator(".tx-data-count").nth(3)
        self.notifications_count_via_filter = page.locator(".tx-data-count").last
        

