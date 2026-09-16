from datetime import date

from Pages.login_page import LoginPage
from playwright.sync_api import expect
from components.navbar import Navbar
from components.toast_notifcations import ToastNotifications
from Pages.asset_installation_page import AssetInstallationPage
from components.side_menu_asset_management import SideMenuAssetManagement
from components.create_installation_wizard import CreateInstallationWizard
import re


def test_installation_creation(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    installation_page = AssetInstallationPage(page)
    toast = ToastNotifications(page)
    installation_wizard = CreateInstallationWizard(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(side_menu.asset_management_heading).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]+"))
    side_menu.navigate_to_vehicle_usage_installations()
    expect(installation_page.add_installation_button).to_be_visible()
    installation_page.open_installation_wizard()
    page.wait_for_timeout(2000)
    # Selects whichever asset/vehicle the account actually has instead of
    # hardcoded names -- a hardcoded asset/vehicle name is only valid for
    # one specific account/environment and silently breaks (option never
    # found) anywhere else. Specifically picks an asset that ISN'T already
    # installed on another vehicle, so this stays a plain "create a new
    # installation" test rather than also needing to handle the separate
    # reassignment-confirmation flow an already-installed asset triggers.
    # Uses today's date, not a hardcoded past date -- confirmed live
    # 2026-09-15 that the app refuses to delete an installation once it
    # becomes a "historical" record ("Historical installation records
    # cannot be removed."), and a fixed past date (the original hardcoded
    # "01/01/2025") is already historical the moment it's created, making
    # this test's own cleanup permanently impossible and leaving
    # undeletable residue in the account on every run.
    today = date.today().strftime("%m/%d/%Y")
    installation_wizard.select_first_unassigned_asset()
    installation_wizard.select_first_vehicle()
    installation_wizard.enter_installed_on_date(today)
    installation_wizard.enter_installed_by("Test User")
    installation_wizard.enter_remarks("Test Remarks")
    installation_wizard.click_submit()
    # Every installation goes through a second "Confirm Vehicle Assignment"
    # review dialog before it's actually created (confirmed live
    # 2026-09-15, universal -- not specific to reassignment) -- confirm it.
    confirm_button = page.get_by_role("button", name="Assign Asset")
    confirm_button.wait_for(state="visible", timeout=5000)
    confirm_button.click()
    expect(toast.success_toast).to_be_visible() # Expect to see some toast notification saying installation created successfully

    # Search for the installation. Only deletes rows dated today -- the
    # account also has older, genuinely historical "Test User" records
    # (both real usage and residue from days-ago test runs, before this
    # date-hardcoding bug was fixed) that the app will never let anyone
    # delete, so asserting a blanket "0 results" would fail forever
    # regardless of whether this test's own record was cleaned up.
    page.wait_for_timeout(2000)
    installation_page.search_installation("test user")
    page.wait_for_timeout(1000)
    todays_rows = installation_page.table_rows.filter(has_text=today)
    while todays_rows.count() > 0:
        installation_page.delete_installation_in_row(todays_rows.first)
        print("\nInstallation Deleted")
        page.wait_for_timeout(2000)
        expect(toast.success_toast).to_be_visible()
        page.wait_for_timeout(2000)
        installation_page.search_installation("test user")
        page.wait_for_timeout(1000)
    expect(todays_rows).to_have_count(0)
        
        
    
    
