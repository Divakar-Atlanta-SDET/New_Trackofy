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

    def go_to(self, module_name: str):
        """Navigate to a top-level module (Home/Dashboard/Unit/Tracking/
        Reports/Settings/Administrator) via its header nav-bar link.

        Confirmed live 2026-09-11: a direct page.goto() to a module's own
        URL -- or a plain in-place browser refresh while already on it --
        silently bounces back to /home instead of loading the module, on
        every module checked so far (Dashboard, Unit). This is an app-wide
        SPA routing defect, not one module's bug (see retest_bug_report.md,
        NEW-1). The only reliable way to reach any module is a real in-app
        nav-link click, so every Page Object's open_*() should route
        through this shared method instead of goto() -- keeps the
        workaround in one place instead of duplicated per module.
        """
        link = self.page.get_by_role("link", name=module_name, exact=True)
        link.wait_for(state="visible", timeout=15000)
        link.click()
        
        
        