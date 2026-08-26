from Pages.login_page import LoginPage
from Pages.asset_list_page import AssetListPage
from components.side_menu_asset_management import SideMenuAssetManagement
from components.navbar import Navbar
from playwright.sync_api import expect
import pytest
import re

def test_asset_management_options_visible(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    
    # Click on apps icon and open asset management
    navbar.click_application_icon()
    expect(navbar.asset_management_option).to_be_visible()
  
    


def test_asset_management_opens(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(side_menu.asset_management_heading).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]+"))
    
def test_asset_setup_shows_related_options(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.Asset_setup).to_be_visible()
    side_menu.click_asset_setup()
    expect(side_menu.Categories).to_be_visible()
    expect(side_menu.Asset_Types).to_be_visible()
    expect(side_menu.Asset_Status).to_be_visible()
    expect(side_menu.Units).to_be_visible()
    expect(side_menu.Brands).to_be_visible()
    expect(side_menu.Vendors).to_be_visible()
    expect(side_menu.Document_Types).to_be_visible()
    
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]*"))
    
def test_asset_setup_collapse_do_not_show_other_options(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.Asset_setup).to_be_visible()
    side_menu.click_asset_setup()
    side_menu.click_asset_setup()
    expect(side_menu.Asset_setup).to_have_attribute("aria-expanded", "false")
    
@pytest.mark.parametrize(
    "option, expected_path",
    [
         ("Categories", "asset-management/categories"),
         ("Asset_Types", "asset-management/asset-type"),
         ("Asset_Status", "asset-management/status-master"),
         ("Units", "asset-management/asset-unit"),
         ("Brands", "asset-management/asset-brands"),
         ("Vendors", "asset-management/vendors"),
         ("Document_Types", "asset-management/asset-document"),
    ]
)
def test_asset_setup_options_navigate_correctly(page, config, credentials, option, expected_path):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    
    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    
    # Click on apps icon and open asset management
    navbar.navigate_to_asset_management()
    expect(side_menu.Asset_setup).to_be_visible()
    side_menu.click_asset_setup()
    getattr(side_menu, option).click()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/{expected_path}"))
    
def test_direct_asset_management_navigation(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)

    side_menu = SideMenuAssetManagement(page)
    
    # Navigate directly to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]*"))
    
def test_browser_back_navigation(page,config,credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)

    side_menu = SideMenuAssetManagement(page)
    
    # Navigate directly to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    side_menu.navigate_to_asset_setup_categories()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/categories"))
    
    # Go back
    page.go_back()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]*"))
    
def test_refresh_page_navigation(page,config,credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)

    side_menu = SideMenuAssetManagement(page)
    
    # Navigate directly to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    side_menu.navigate_to_asset_setup_categories()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/categories"))
    
    # Refresh page
    page.reload()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/categories"))
    
def test_asset_management_accesible_after_navigating_away(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)

    side_menu = SideMenuAssetManagement(page)
    
    # Navigate directly to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    side_menu.navigate_to_asset_setup_categories()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/categories"))
    
    # Navigate to another page
    page.goto(f"{config["base_url"]}/asset-management/dashboard")
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/dashboard"))
    
    # Navigate back to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management[/\w]*"))
    

def test_asset_list_table_is_visible(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_timeout(2000)

    side_menu = SideMenuAssetManagement(page)
    
    # Navigate directly to asset management
    page.goto(f"{config["base_url"]}/asset-management")
    expect(side_menu.asset_management_side_menu).to_be_visible()
    side_menu.navigate_to_assets_all_assets()
    expect(page).to_have_url(re.compile(rf"{config["base_url"]}/asset-management/asset-master"))
    
    # Check if asset list table is visible
    asset_list_page = AssetListPage(page, config)
    all_headers = asset_list_page.table_header.all()
    print(f"Found {len(all_headers)} table headers")
    for header in all_headers:
        print(f"Header: {header.inner_text()}")
        
    assert "Asset Name" in [header.inner_text() for header in all_headers]
    

    
