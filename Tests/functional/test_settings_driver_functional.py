import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_set_010_driver_list_loads(driver_page):
    """SET-010: Verify Driver list loads without error."""
    expect(driver_page.heading).to_contain_text("Drivers")
    expect(driver_page.table).to_be_visible()


@pytest.mark.functional
def test_set_030_driver_list_columns(driver_page):
    """SET-030: Verify Driver list displays the configured driver information columns."""
    header = driver_page.table.locator("thead")
    for column in ["Name", "DL No", "Assigned Unit", "DL Issued Date", "DL Expiry Date", "DOB", "Email", "Contact No", "Address"]:
        expect(header).to_contain_text(column)


@pytest.mark.functional
def test_set_031_open_create_driver_form(driver_page):
    """SET-031: Open Create Driver form; Personal Information and Driving Licence sections shown."""
    driver_page.open_add_driver_form()
    expect(driver_page.driver_dialog).to_contain_text("Personal Information")
    expect(driver_page.driver_dialog).to_contain_text("Driving Licence")
    expect(driver_page.create_driver_btn).to_be_disabled()
