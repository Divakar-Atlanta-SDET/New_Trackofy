import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.edgecase
def test_set_068_create_group_without_units(vehicle_group_page):
    """SET-068: Create group without selecting any units; app follows its
    defined rule -- either zero-unit group is created or validation blocks it,
    but never an inconsistent assignment."""
    name = _unique_name("EmptyGroup")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    vehicle_group_page.page.wait_for_timeout(300)

    if vehicle_group_page.create_group_btn.is_enabled():
        vehicle_group_page.create_group_btn.click()
        vehicle_group_page.wait_for_dialog_closed()
        expect(vehicle_group_page.row_containing(name)).to_be_visible()
        vehicle_group_page.delete_group(name)
    else:
        vehicle_group_page.close_dialog()
