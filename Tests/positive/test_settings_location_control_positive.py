import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.positive
def test_set_083_create_valid_location(location_control_page):
    """SET-083: Create a valid location; it appears in the list."""
    name = _unique_name("AutoLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    expect(location_control_page.create_btn).to_be_enabled()
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()

    try:
        expect(location_control_page.row_containing(name)).to_be_visible()
    finally:
        location_control_page.delete_location(name)


@pytest.mark.positive
def test_set_087_edit_location(location_control_page):
    """SET-087: Edit a location's name; change persists after refresh."""
    name = _unique_name("EditLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()
    location_control_page.wait_for_visible(location_control_page.row_containing(name))

    try:
        new_name = _unique_name("Renamed")
        location_control_page.open_edit_location_form(name)
        expect(location_control_page.location_input).to_have_value(name)
        location_control_page.location_input.fill(new_name)
        location_control_page.page.wait_for_timeout(300)
        location_control_page.update_btn.click()
        location_control_page.wait_for_dialog_closed()
        location_control_page.wait_for_visible(location_control_page.row_containing(new_name))
        name = new_name

        location_control_page.page.reload()
        location_control_page.wait_for_loading_to_finish()
        expect(location_control_page.row_containing(new_name)).to_be_visible()
    finally:
        location_control_page.delete_location(name)


@pytest.mark.positive
def test_set_088_delete_location(location_control_page):
    """SET-088: Delete a location; it is removed and stays removed after refresh."""
    name = _unique_name("DelLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()
    location_control_page.wait_for_visible(location_control_page.row_containing(name))
    expect(location_control_page.row_containing(name)).to_be_visible()

    location_control_page.delete_location(name)
    location_control_page.page.reload()
    location_control_page.wait_for_loading_to_finish()
    expect(location_control_page.row_containing(name)).to_have_count(0)
