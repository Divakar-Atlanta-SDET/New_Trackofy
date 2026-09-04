import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.negative
def test_set_067_group_name_mandatory(vehicle_group_page):
    """SET-067: Leaving the group name blank blocks Create Group."""
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.select_units(1)
    expect(vehicle_group_page.create_group_btn).to_be_disabled()
    vehicle_group_page.close_dialog()


@pytest.mark.negative
def test_set_073_cancel_group_deletion(vehicle_group_page):
    """SET-073: Cancelling a delete confirmation leaves the group unchanged."""
    name = _unique_name("KeepGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    vehicle_group_page.select_units(1)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()

    try:
        vehicle_group_page.delete_button(name).click()
        vehicle_group_page.wait_for_visible(vehicle_group_page.cancel_delete_btn)
        vehicle_group_page.cancel_delete_btn.click()
        vehicle_group_page.wait_for_dialog_closed()
        expect(vehicle_group_page.row_containing(name)).to_be_visible()
    finally:
        vehicle_group_page.delete_group(name)
