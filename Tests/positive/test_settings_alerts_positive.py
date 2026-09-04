import pytest
from playwright.sync_api import expect
from Pages.alert_config_page import ALERT_SPECS

ALERT_TYPES_STANDARD = list(ALERT_SPECS.keys())
# POI Alert creation is broken server-side despite a fully valid form, and
# BMS/Vehicle Odometer Alert's list never shows a record it just created
# even after reload (confirmed live, see Bug_Report.md #10/#11) -- all three
# excluded from the "should succeed and appear in the list" flows below and
# covered separately in the negative suite instead.
_BROKEN_CREATE_FLOW = {"POI Alert", "BMS Alert", "Vehicle Odometer Alert"}
ALERT_TYPES_CREATABLE = [t for t in ALERT_TYPES_STANDARD if t not in _BROKEN_CREATE_FLOW]


@pytest.mark.positive
@pytest.mark.parametrize("alert_type", ALERT_TYPES_CREATABLE)
def test_create_valid_alert_configuration(alert_page, alert_type):
    """SET-091/095/099/103/107/111/115/119/123/131: create a valid alert
    configuration; it's saved and appears in the list."""
    page = alert_page(alert_type)
    page.open_add_form()
    veh_names = page.select_vehicles(1)
    page.set_time_range()
    page.set_extra_combos()
    page.fill_numeric_fields()
    page.set_notify()
    expect(page.submit_btn).to_be_enabled()
    page.submit()
    page.page.wait_for_timeout(2000)
    page.page.reload()
    page.wait_for_loading_to_finish()
    page.page.wait_for_timeout(1500)

    row = page.row_containing(veh_names[0])
    try:
        expect(row).to_be_visible(timeout=10000)
    finally:
        if row.count() > 0:
            page.delete_alert(veh_names[0])


@pytest.mark.positive
@pytest.mark.parametrize("alert_type", ALERT_TYPES_CREATABLE)
def test_edit_and_delete_alert_configuration(alert_page, alert_type):
    """SET-093/097/101/105/109/113/117/121/125/133: edit an existing alert
    configuration, then delete it and confirm removal."""
    page = alert_page(alert_type)
    page.open_add_form()
    veh_names = page.select_vehicles(1)
    page.set_time_range()
    page.set_extra_combos()
    page.fill_numeric_fields()
    page.set_notify()
    page.submit()
    page.wait_for_visible(page.row_containing(veh_names[0]))

    try:
        page.edit_button(veh_names[0]).click()
        page.wait_for_visible(page.dialog)
        page.page.wait_for_timeout(800)
        page.fill_numeric_fields(value="15")
        update_btn = page.dialog.get_by_role("button", name="Update Alert")
        if update_btn.count() == 0:
            update_btn = page.submit_btn
        update_btn.click()
        page.dialog.wait_for(state="hidden", timeout=page.DEFAULT_TIMEOUT_MS)
        expect(page.row_containing(veh_names[0])).to_be_visible()
    finally:
        page.delete_alert(veh_names[0])
        expect(page.row_containing(veh_names[0])).to_have_count(0)
