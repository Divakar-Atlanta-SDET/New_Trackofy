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
    installation_wizard.create_installation("test", "HARSH_test", "01/01/2025", "Test User", "Test Remarks")
    expect(toast.success_toast).to_be_visible() # Expect to see some toast notification saying installation created successfully
    
    # Search for the installation
    page.wait_for_timeout(2000)
    installation_page.search_installation("test user")
    while installation_page.delete_installation_button.count() > 0:
        installation_page.delete_installation()
        print("\nInstallation Deleted")
        page.wait_for_timeout(2000)
        expect(toast.success_toast).to_be_visible()
        page.wait_for_timeout(2000)
    expect(installation_page.delete_installation_button).to_have_count(0)
        
        
    
    
