import pytest
from playwright.sync_api import expect


@pytest.mark.positive
def test_set_076_create_valid_unit_performance(vehicle_performance_page):
    """SET-076: Create a valid unit performance configuration; appears in the list."""
    vehicle_performance_page.open_configure_form()
    categories = vehicle_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    vehicle_performance_page.select_category(category)
    vehicle_performance_page.set_range("distance", 50, 200)
    expect(vehicle_performance_page.create_btn).to_be_enabled()
    vehicle_performance_page.create_btn.click()
    vehicle_performance_page.wait_for_dialog_closed()
    vehicle_performance_page.wait_for_visible(vehicle_performance_page.row_containing(category))

    try:
        expect(vehicle_performance_page.row_containing(category)).to_be_visible()
    finally:
        vehicle_performance_page.delete_configuration(category)


@pytest.mark.positive
def test_set_080_edit_vehicle_performance(vehicle_performance_page):
    """SET-080: Edit a vehicle performance configuration's range; update persists after refresh."""
    vehicle_performance_page.open_configure_form()
    categories = vehicle_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    vehicle_performance_page.select_category(category)
    vehicle_performance_page.set_range("distance", 50, 200)
    vehicle_performance_page.create_btn.click()
    vehicle_performance_page.wait_for_dialog_closed()
    vehicle_performance_page.wait_for_visible(vehicle_performance_page.row_containing(category))

    try:
        vehicle_performance_page.edit_button(category).click()
        vehicle_performance_page.wait_for_visible(vehicle_performance_page.dialog)
        vehicle_performance_page.page.wait_for_timeout(1000)  # dialog populates async, confirmed live
        vehicle_performance_page.set_range("distance", 75, 250)
        vehicle_performance_page.page.wait_for_timeout(300)
        vehicle_performance_page.update_btn.click()
        vehicle_performance_page.wait_for_dialog_closed()

        vehicle_performance_page.page.reload()
        vehicle_performance_page.wait_for_loading_to_finish()
        vehicle_performance_page.wait_for_visible(vehicle_performance_page.row_containing(category))
        row = vehicle_performance_page.row_containing(category)
        expect(row).to_contain_text("75")
        expect(row).to_contain_text("250")
    finally:
        vehicle_performance_page.delete_configuration(category)


@pytest.mark.positive
def test_set_081_delete_vehicle_performance(vehicle_performance_page):
    """SET-081: Delete a vehicle performance configuration; removed from the list."""
    vehicle_performance_page.open_configure_form()
    categories = vehicle_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    vehicle_performance_page.select_category(category)
    vehicle_performance_page.set_range("distance", 50, 200)
    vehicle_performance_page.create_btn.click()
    vehicle_performance_page.wait_for_dialog_closed()
    vehicle_performance_page.wait_for_visible(vehicle_performance_page.row_containing(category))
    expect(vehicle_performance_page.row_containing(category)).to_be_visible()

    vehicle_performance_page.delete_configuration(category)
    expect(vehicle_performance_page.row_containing(category)).to_have_count(0)
