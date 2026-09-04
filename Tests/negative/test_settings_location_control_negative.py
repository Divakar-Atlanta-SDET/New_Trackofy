import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.negative
def test_set_084_location_name_mandatory(location_control_page):
    """SET-084: Location name is mandatory; Create stays disabled when blank."""
    location_control_page.open_add_location_form()
    expect(location_control_page.create_btn).to_be_disabled()
    location_control_page.location_input.fill("temp")
    expect(location_control_page.create_btn).to_be_enabled()
    location_control_page.location_input.fill("")
    expect(location_control_page.create_btn).to_be_disabled()


@pytest.mark.negative
def test_set_085_duplicate_location_name_not_prevented(location_control_page):
    """SET-085: Creating a location with a name that already exists.

    Confirmed live: the app does NOT enforce name uniqueness -- creating a
    second location with an identical name succeeds and produces two
    separate rows. Flagged as a real data-integrity gap (see Bug_Report.md)
    rather than asserted as a false "rejected" expectation.
    """
    name = _unique_name("DupLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()
    location_control_page.wait_for_visible(location_control_page.row_containing(name))

    try:
        location_control_page.open_add_location_form()
        location_control_page.location_input.fill(name)
        location_control_page.create_btn.click()
        location_control_page.page.wait_for_timeout(1000)
        location_control_page.close_dialog()
        location_control_page.page.reload()
        location_control_page.wait_for_loading_to_finish()
        expect(location_control_page.row_containing(name)).to_have_count(2)
    finally:
        location_control_page.delete_location(name)


@pytest.mark.negative
def test_set_086_assign_unit_button_stays_disabled(location_control_page):
    """SET-086: Assign a unit to a location.

    Confirmed live: this is broken, not just flaky -- picking a vehicle from
    the "Select Vehicles" multi-select updates the option's own aria-selected
    state and the select's displayed value, but the dialog's "X selected"
    counter never leaves "0 selected" and the Assign Units button never
    enables, across repeated single/double/triple clicks and different
    vehicles. See Bug_Report.md #9. This test documents the real (broken)
    behavior rather than asserting a successful assignment that the UI
    cannot currently perform.
    """
    name = _unique_name("AssignLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()
    location_control_page.wait_for_visible(location_control_page.row_containing(name))

    try:
        location_control_page.open_assign_unit_dialog(name)
        location_control_page.assign_vehicles_select.click()
        location_control_page.wait_for_visible(location_control_page.assign_vehicle_options.first)
        location_control_page.assign_vehicle_options.first.click()
        location_control_page.page.wait_for_timeout(500)
        expect(location_control_page.assign_units_btn).to_be_disabled()
    finally:
        location_control_page.delete_location(name)


@pytest.mark.negative
def test_set_089_cancel_deletion_keeps_location(location_control_page):
    """SET-089: Cancelling a delete confirmation leaves the location intact."""
    name = _unique_name("CancelDelLoc")
    location_control_page.open_add_location_form()
    location_control_page.location_input.fill(name)
    location_control_page.create_btn.click()
    location_control_page.wait_for_dialog_closed()
    location_control_page.wait_for_visible(location_control_page.row_containing(name))

    try:
        location_control_page.delete_button(name).click()
        location_control_page.wait_for_visible(location_control_page.cancel_delete_btn)
        location_control_page.page.wait_for_timeout(400)
        location_control_page.cancel_delete_btn.click()
        location_control_page.wait_for_dialog_closed()
        expect(location_control_page.row_containing(name)).to_be_visible()
    finally:
        location_control_page.delete_location(name)
