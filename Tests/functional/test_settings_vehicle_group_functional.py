import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_set_012_vehicle_group_list_loads(vehicle_group_page):
    """SET-012: Verify Vehicle Group list loads without error."""
    expect(vehicle_group_page.table).to_be_visible()


@pytest.mark.functional
def test_set_065_open_create_unit_group_form(vehicle_group_page):
    """SET-065: Open Create Unit Group form; group name and assigned units shown."""
    vehicle_group_page.open_add_group_form()
    expect(vehicle_group_page.group_name_input).to_be_visible()
    expect(vehicle_group_page.units_select).to_be_visible()
    expect(vehicle_group_page.create_group_btn).to_be_disabled()


@pytest.mark.functional
def test_set_070_view_unit_list_of_group(vehicle_group_page):
    """SET-070: View a group's assigned unit list; units are displayed accurately."""
    first_row = vehicle_group_page.table.locator("tbody tr").first
    group_name = first_row.locator("td").nth(1).inner_text().strip()
    if not group_name:
        pytest.skip("No existing group on this account to view")
    vehicle_group_page.view_button(group_name).click()
    vehicle_group_page.wait_for_loading_to_finish()
    expect(vehicle_group_page.page.get_by_text("Assigned Vehicles", exact=True)).to_be_visible()
