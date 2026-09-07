from playwright.sync_api import Page

from Pages.base_page import BasePage


class AdminDashboardPage(BasePage):
    """/admin/dashboard -- the Admin Panel landing page. Distinct app from
    the main fleet-management SPA: PrimeNG components (p-menubar,
    p-toggleswitch, p-tag), not Angular Material."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: top-level p-menubar items are expandable submenu
        # triggers, not direct <a> links -- child items' real destination
        # hrefs exist in the DOM even while their submenu is collapsed
        # (get_by_role("link", name=...) can locate them), but they aren't
        # click-actionable until the parent is hovered open (see
        # click_nav_link()).

    # Confirmed live: a child link's href is present in the DOM even while
    # its parent submenu is visually collapsed, but it isn't *actionable*
    # (click() times out) until the parent top-level item is opened -- the
    # parent must be hovered first.
    NAV_PARENT = {
        "Manage User": "User",
        "Manage Dealer": "User",
        "Add Device": "Device",
        "UnassignDevice": "Device",
        "Manage Device": "Device",
        "Create Plan": "Plan",
        "Manage Plan": "Plan",
    }

    def nav_link(self, name: str, exact: bool = True):
        return self.page.get_by_role("link", name=name, exact=exact)

    def open_nav_submenu(self, parent_name: str):
        # Confirmed live: unlike child items, the top-level parent trigger
        # has no href, so it doesn't expose an accessible role="link" --
        # get_by_text is the closest role/label-based locator that reaches
        # it (documented exception, not a default to CSS).
        self.page.get_by_text(parent_name, exact=True).first.hover()
        self.page.wait_for_timeout(500)

    def click_nav_link(self, name: str, exact: bool = True):
        parent = self.NAV_PARENT.get(name)
        if parent:
            self.open_nav_submenu(parent)
        self.nav_link(name, exact=exact).click()

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/admin/dashboard")
        self.expect_path("/admin/dashboard")

    def goto_manage_user(self):
        self.click_nav_link("Manage User")
        self.expect_path("/admin/user/manage-user")

    def goto_manage_dealer(self):
        self.click_nav_link("Manage Dealer")
        self.expect_path("/admin/user/manage-dealer")

    def goto_add_device(self):
        self.click_nav_link("Add Device")
        self.expect_path("/admin/device/add-device")

    def goto_unassign_device(self):
        # Confirmed live: this nav link's real accessible name is
        # "UnassignDevice" (no space) -- inconsistent with every other
        # nav item's spaced label (logged as a Minor UI-inconsistency bug).
        self.click_nav_link("UnassignDevice")
        self.expect_path("/admin/device/unassign-device")

    def goto_manage_device(self):
        self.click_nav_link("Manage Device")
        self.expect_path("/admin/device/manage-device")

    def goto_create_plan(self):
        self.click_nav_link("Create Plan")
        self.expect_path("/admin/plan/create-plan")

    def goto_manage_plan(self):
        self.click_nav_link("Manage Plan")
        self.expect_path("/admin/plan/manage-plan")

    def goto_tax(self):
        self.nav_link("Tax", exact=True).click()
        self.expect_path("/admin/tax")
