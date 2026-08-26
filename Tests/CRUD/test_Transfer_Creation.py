from Pages.login_page import LoginPage
from playwright.sync_api import expect
from components.navbar import Navbar
from components.toast_notifcations import ToastNotifications
from Pages.asset_transfer_page import AssetTransferPage
from components.side_menu_asset_management import SideMenuAssetManagement
from components.create_transfer_wizard import CreateTransferWizard
import re

def test_transfer_creation(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    transfer_page = AssetTransferPage(page)
    toast = ToastNotifications(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(side_menu.asset_management_heading).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]+"))
    side_menu.navigate_to_vehicle_usage_vehicle_transfers()
    expect(transfer_page.add_new_transfer).to_be_visible()
    transfer_page.open_transfer_wizard()
    transfer_wizard = CreateTransferWizard(page)
    page.wait_for_timeout(2000)
    transfer_wizard.create_transfer("test", "HARSH_test", "HARSH_test", "01/01/2025", "Test Remarks")
    expect(toast.info_toast).to_be_visible() # Expect to see some toast notification saying previous and transfer to vehicle can't be same
    