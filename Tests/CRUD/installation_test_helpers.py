import re
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from Pages.asset_installation_page import AssetInstallationPage
from Pages.login_page import LoginPage
from components.create_installation_wizard import CreateInstallationWizard
from components.navbar import Navbar
from components.side_menu_asset_management import SideMenuAssetManagement
from components.toast_notifcations import ToastNotifications


INSTALLATION_DATE = "01/01/2025"


def unique_installed_by(prefix="Installation Test"):
    return f"{prefix} {uuid4().hex[:8]}"


def open_installations(page, config, credentials):
    """Log in and navigate to the installations list using shared POMs."""
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])

    navbar = Navbar(page)
    side_menu = SideMenuAssetManagement(page)
    installation_page = AssetInstallationPage(page)

    navbar.navigate_to_asset_management()
    expect(side_menu.asset_management_side_menu).to_be_visible()
    expect(side_menu.asset_management_heading).to_be_visible()
    expect(page).to_have_url(re.compile(rf"{config['base_url']}/asset-management[/\w]+"))
    side_menu.navigate_to_vehicle_usage_installations()
    expect(installation_page.add_installation_button).to_be_visible()
    return installation_page


def open_wizard(page, config, credentials):
    installation_page = open_installations(page, config, credentials)
    installation_page.open_installation_wizard()
    wizard = CreateInstallationWizard(page)
    expect(wizard.submit_button).to_be_visible()
    return installation_page, wizard, ToastNotifications(page)


def fill_valid_installation(wizard, installed_by=None, remarks=""):
    installed_by = installed_by or unique_installed_by()
    select_available_asset(wizard)
    select_available_vehicle(wizard)
    wizard.enter_installed_on_date(INSTALLATION_DATE)
    wizard.enter_installed_by(installed_by)
    wizard.enter_remarks(remarks)
    return installed_by


def select_available_asset(wizard):
    wizard.open_asset_options()
    options = wizard.page.get_by_role("option")
    if not options.count():
        pytest.skip("No assets are available in the target environment for installation creation.")
    value = options.first.inner_text()
    options.first.click()
    return value


def select_available_vehicle(wizard):
    wizard.open_vehicle_options()
    options = wizard.page.get_by_role("option")
    if not options.count():
        pytest.skip("No vehicles are available in the target environment for installation creation.")
    value = options.first.inner_text()
    options.first.click()
    return value


def remove_matching_installations(installation_page, installed_by):
    """Remove only records found by the unique Installed By test value."""
    installation_page.search_installation(installed_by)
    while installation_page.delete_installation_button.count():
        installation_page.delete_installation()
        expect(installation_page.delete_installation_button).to_have_count(0)
