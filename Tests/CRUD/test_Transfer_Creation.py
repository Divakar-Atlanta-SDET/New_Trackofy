import pytest
from Pages.login_page import LoginPage
from playwright.sync_api import expect
from components.navbar import Navbar
from components.toast_notifcations import ToastNotifications
from Pages.asset_transfer_page import AssetTransferPage
from components.side_menu_asset_management import SideMenuAssetManagement
from components.create_transfer_wizard import CreateTransferWizard
import re


@pytest.mark.skip(
    reason=(
        "Confirmed live 2026-09-15: this test's premise no longer matches the real form. "
        "(1) The 'Transfer To Vehicle' dropdown already excludes the asset's current vehicle, "
        "so 'select the same vehicle for from/to' is not reachable through the UI at all -- the "
        "'can't transfer to same vehicle' toast this test checks for can never fire this way. "
        "(2) The real form has required fields never modeled here (Transfer Reason, and for "
        "tyre-type assets: Removal Reason, Condition After Removal, New Axle, New Tyre Position) -- "
        "submitting without them shows 'Please complete all required fields' before any vehicle "
        "validation is even reached. This needs a real redesign (what should this test actually "
        "verify now?), not a data-hardcoding fix -- flagging for a scoped follow-up rather than "
        "guessing at the intended behavior."
    )
)
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
    # Selects whichever asset the account actually has (first in the
    # dropdown) instead of a hardcoded name -- a hardcoded name is only
    # valid for one specific account/environment and silently breaks
    # (option never found) anywhere else.
    transfer_wizard.select_first_asset()
    same_vehicle = transfer_wizard.current_vehicle_text()
    transfer_wizard.select_transfer_to(same_vehicle)
    transfer_wizard.enter_transfer_date("01/01/2025")
    transfer_wizard.enter_remarks("Test Remarks")
    transfer_wizard.submit_transfer()
    expect(toast.info_toast).to_be_visible() # Expect to see some toast notification saying previous and transfer to vehicle can't be same
