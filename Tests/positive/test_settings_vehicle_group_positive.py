import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.positive
def test_set_066_create_group_with_valid_data(vehicle_group_page):
    """SET-066: Create a unit group with a valid name and units; appears in the list."""
    name = _unique_name("AutoGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    vehicle_group_page.select_units(2)
    expect(vehicle_group_page.create_group_btn).to_be_enabled()
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()

    try:
        expect(vehicle_group_page.row_containing(name)).to_be_visible()
    finally:
        vehicle_group_page.delete_group(name)


@pytest.mark.positive
def test_set_069_assign_multiple_units_to_group(vehicle_group_page):
    """SET-069: Assign multiple units to a group; all selected units are assigned correctly."""
    name = _unique_name("MultiGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    unit_names = vehicle_group_page.select_units(3)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()

    try:
        row = vehicle_group_page.row_containing(name)
        expect(row).to_be_visible()
        vehicle_group_page.view_button(name).click()
        vehicle_group_page.wait_for_loading_to_finish()
        for unit in unit_names:
            expect(vehicle_group_page.page.get_by_text(unit)).to_be_visible()
        vehicle_group_page.page.keyboard.press("Escape")
    finally:
        vehicle_group_page.delete_group(name)


@pytest.mark.positive
def test_set_071_edit_group(vehicle_group_page):
    """SET-071: Edit a group's name; change persists and other data is untouched."""
    name = _unique_name("EditGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    unit_names = vehicle_group_page.select_units(1)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()

    try:
        new_name = _unique_name("Renamed")
        vehicle_group_page.open_edit_group_form(name)
        vehicle_group_page.group_name_input.fill(new_name)
        vehicle_group_page.page.wait_for_timeout(300)
        vehicle_group_page.update_group_btn.click()
        vehicle_group_page.wait_for_dialog_closed()
        vehicle_group_page.wait_for_visible(vehicle_group_page.row_containing(new_name))
        name = new_name  # cleanup must target the renamed row from here on,
        # regardless of whether the assertions below pass

        vehicle_group_page.page.reload()
        vehicle_group_page.wait_for_loading_to_finish()
        vehicle_group_page.page.wait_for_timeout(1500)
        expect(vehicle_group_page.row_containing(new_name)).to_be_visible()

        # unrelated data (the assigned unit) must survive a name-only edit
        vehicle_group_page.view_button(new_name).click()
        vehicle_group_page.wait_for_loading_to_finish()
        expect(vehicle_group_page.page.get_by_text(unit_names[0], exact=True)).to_be_visible()
        vehicle_group_page.page.keyboard.press("Escape")
    finally:
        vehicle_group_page.delete_group(name)


@pytest.mark.positive
def test_set_072_delete_group(vehicle_group_page):
    """SET-072: Delete a group; it is removed and stays removed after refresh."""
    name = _unique_name("DelGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    vehicle_group_page.select_units(1)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()
    expect(vehicle_group_page.row_containing(name)).to_be_visible()

    vehicle_group_page.delete_group(name)
    vehicle_group_page.page.reload()
    vehicle_group_page.wait_for_loading_to_finish()
    expect(vehicle_group_page.row_containing(name)).to_have_count(0)


@pytest.mark.positive
def test_set_074_group_assignment_persists_after_refresh(vehicle_group_page):
    """SET-074: Unit assignments remain correct after refresh."""
    name = _unique_name("PersistGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    unit_names = vehicle_group_page.select_units(2)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()

    try:
        vehicle_group_page.page.reload()
        vehicle_group_page.wait_for_loading_to_finish()
        vehicle_group_page.view_button(name).click()
        vehicle_group_page.wait_for_loading_to_finish()
        for unit in unit_names:
            expect(vehicle_group_page.page.get_by_text(unit)).to_be_visible()
        vehicle_group_page.page.keyboard.press("Escape")
    finally:
        vehicle_group_page.delete_group(name)
