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
    """SET-085: Regression pin for Bug_Report.md #8 (Location Control side).
    Reverified live (2026-09-13): this is now FIXED -- creating a second
    Location with an identical name is rejected with a "Location name
    already exists" message, and only the original record remains.
    Confirmed 3x live prior to updating this test.
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
        body = location_control_page.page.inner_text("body")
        assert "already exist" in body.lower(), (
            "Expected a 'Location name already exists' message -- if this fails, Bug #8 "
            "(duplicate location names silently accepted) may have regressed."
        )
        try:
            location_control_page.close_dialog()
        except Exception:
            pass
        location_control_page.page.reload(); location_control_page.reopen()
        location_control_page.wait_for_loading_to_finish()
        expect(location_control_page.row_containing(name)).to_have_count(1)
    finally:
        location_control_page.delete_location(name)


@pytest.mark.negative
def test_set_086_assign_unit_button_stays_disabled(location_control_page):
    """SET-086: Regression pin for Bug_Report.md #9. Reverified live
    (2026-09-13): this is now FIXED -- picking a vehicle from the "Select
    Vehicles" multi-select correctly updates the dialog's "X selected"
    counter and enables the Assign Units button, and the full assignment
    completes successfully. Confirmed 3x live prior to updating this test.
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
        expect(location_control_page.assign_units_btn).to_be_enabled()
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
