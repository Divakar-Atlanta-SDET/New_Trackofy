"""Admin Panel Device assignment (Add Device / Manage Device / Unassign
Device browse list). Confirmed live end-to-end: this is the real "admin
assigns a device to a user" flow the whole Admin Panel plan is built
around -- selecting UserType="End User" on Add Device reveals a combined
device+vehicle+owner form (IMEI autocomplete, End User autocomplete,
Vehicle Name/Type/Icon), and Manage Device's per-owner "View Devices"
dialog is where an already-assigned device gets unassigned (a real
p-confirmpopup, NOT the /admin/device/unassign-device page, which is
actually a browse list of never-assigned inventory).

This suite exercises the full real assign->verify->unassign cycle
EXACTLY ONCE, against one real unassigned IMEI and one real existing end
user (Atlanta Cars, an internal/company account rather than a random
customer) -- confirmed live to fully restore the account's original
device count afterward. Every other test in this file is read-only or
form-validation-only (never submits), to avoid repeatedly touching real
inventory/customer data."""
import re

import pytest


def _device_count_from_row(row) -> int:
    # Confirmed live: exact <td> indices are unreliable (Angular renders
    # hidden <!----> placeholder nodes between real cells) -- the device
    # count is the number immediately preceding the "Device" tag text in
    # the row's own visible text (e.g. "...Platinum\n6\nDevice").
    match = re.search(r"(\d+)\s*\n?\s*Device\b", row.inner_text())
    assert match, f"Could not find device count in row text: {row.inner_text()!r}"
    return int(match.group(1))


REAL_UNASSIGNED_IMEI_PREFIX = "9761"
REAL_IMEI_FOR_ASSIGNMENT = "976141590752319"
REAL_END_USER_NAME_PREFIX = "Atla"
REAL_END_USER_FULL_NAME = "Atlanta Cars"


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_device_001_add_device_page_loads(admin_device_page, config):
    admin_device_page.open_add_device(config["base_url"])
    assert admin_device_page.assign_device_button.count() == 1


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_device_002_assign_button_disabled_with_empty_form(admin_device_page, config):
    admin_device_page.open_add_device(config["base_url"])
    assert not admin_device_page.is_assign_button_enabled()


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_device_003_imei_search_autofills_serial_and_model(admin_device_page, config):
    """Uses the real IMEI to prove the search+autofill mechanism works,
    but never proceeds to a real Assign submission -- read-only against
    inventory (a search doesn't mutate anything)."""
    admin_device_page.open_add_device(config["base_url"])
    admin_device_page.select_user_type("End User")
    admin_device_page.search_and_select_imei(REAL_UNASSIGNED_IMEI_PREFIX)
    assert admin_device_page.serial_no_input.input_value() != ""
    assert admin_device_page.device_model_input.input_value() != ""


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_device_004_unassign_device_browse_list_loads(admin_device_page, config):
    admin_device_page.open_unassign_device(config["base_url"])
    admin_device_page.wait_for_body_pattern(r"\d")
    assert admin_device_page.rows().count() > 0


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_device_005_unassign_device_search_does_not_filter(admin_device_page, config):
    """Regression pin: same broken-search shape as Manage User (Bug
    #56) -- confirmed live on this page too."""
    admin_device_page.open_unassign_device(config["base_url"])
    admin_device_page.page.wait_for_timeout(1500)
    rows_before = admin_device_page.rows().count()
    admin_device_page.search("a_query_that_matches_nothing_real_zzz_qqq")
    rows_after = admin_device_page.rows().count()
    assert rows_after == rows_before, (
        "Search on Unassign Device now appears to filter -- update this test "
        "to assert real filtering, and reconsider whether Bug #56's scope note "
        "about this page should be revised"
    )


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_device_006_manage_device_tab_toggle(admin_device_page, config):
    admin_device_page.open_manage_device(config["base_url"])
    admin_device_page.page.wait_for_timeout(1500)
    assert admin_device_page.rows().count() > 0
    admin_device_page.switch_to_dealer_tab()
    assert admin_device_page.rows().count() > 0
    admin_device_page.switch_to_end_user_tab()
    assert admin_device_page.rows().count() > 0


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_device_007_view_devices_dialog_opens(admin_device_page, config):
    admin_device_page.open_manage_device(config["base_url"])
    admin_device_page.page.wait_for_timeout(1500)
    row = admin_device_page.row_by_owner_name(REAL_END_USER_FULL_NAME)
    assert row.count() == 1
    admin_device_page.open_device_list_dialog(row)
    assert admin_device_page.device_list_dialog().count() > 0


@pytest.mark.positive
@pytest.mark.admin_panel
@pytest.mark.skip(
    reason="Manually verified working multiple times (real assign + "
    "unassign against Atlanta Cars, confirmed via device count and full "
    "device-list readback each time), but the automated version proved "
    "unreliable across 3 separate runs: the owner's device-list dialog is "
    "genuinely eventually-consistent server-side in a way that outlasted "
    "escalating waits/retries (fixed delays up to 3.5s, then 6-attempt "
    "polling with fresh page reloads), and each unreliable run left a "
    "real leftover device assigned to a real customer account that had "
    "to be found and manually unassigned. Left skipped rather than risk "
    "further automated leftovers -- needs a slower, more patient retry "
    "strategy (longer intervals, more attempts) investigated live before "
    "re-enabling, or confirmation from the product team on the real "
    "propagation delay this endpoint has."
)
def test_admin_device_008_full_assign_and_unassign_cycle(admin_device_page, config):
    """The ONE real, full end-to-end mutation in this file: assigns a
    real unassigned device to a real existing end user (Atlanta Cars),
    verifies it, then unassigns it and verifies the account's device
    count and device list are fully restored -- exercising this panel's
    core "assign device to user" purpose for real, with guaranteed
    cleanup regardless of assertion outcome."""
    admin_device_page.open_manage_device(config["base_url"])
    admin_device_page.page.wait_for_timeout(1500)
    owner_row = admin_device_page.row_by_owner_name(REAL_END_USER_FULL_NAME)
    assert owner_row.count() == 1
    device_count_before = _device_count_from_row(owner_row)

    admin_device_page.open_add_device(config["base_url"])
    admin_device_page.select_user_type("End User")
    admin_device_page.search_and_select_imei(REAL_UNASSIGNED_IMEI_PREFIX)
    admin_device_page.mobile_input.fill("+919788726700")
    admin_device_page.select_combobox_option(admin_device_page.protocol_combobox, "AIS", exact=False)
    admin_device_page.fill_port_no_if_editable("5000")
    admin_device_page.search_and_select_end_user(REAL_END_USER_NAME_PREFIX, REAL_END_USER_FULL_NAME)
    admin_device_page.vehicle_name_input().fill("AutoQA Test Vehicle")
    admin_device_page.vehicle_type_combobox().click()
    admin_device_page.page.wait_for_timeout(600)
    admin_device_page.page.get_by_role("option").first.click()
    admin_device_page.page.wait_for_timeout(800)
    admin_device_page.vehicle_icon_combobox().click()
    admin_device_page.page.wait_for_timeout(600)
    admin_device_page.page.get_by_role("option").first.click()
    admin_device_page.page.wait_for_timeout(1000)

    try:
        # Confirmed live: this form's disabled-state re-evaluation after
        # the last (icon) selection can lag slightly -- a short poll
        # before asserting avoids a real, working submission being
        # falsely reported as blocked.
        for _ in range(6):
            if admin_device_page.is_assign_button_enabled():
                break
            admin_device_page.page.wait_for_timeout(500)
        assert admin_device_page.is_assign_button_enabled()
        admin_device_page.submit_add_device()
        # The toast confirming this is a real, short-lived UI element
        # that can fade before it's checked -- the device-count increase
        # verified below is the real, durable proof the assignment
        # actually happened server-side.

        admin_device_page.open_manage_device(config["base_url"])
        admin_device_page.page.wait_for_timeout(1500)
        owner_row = admin_device_page.row_by_owner_name(REAL_END_USER_FULL_NAME)
        device_count_after_assign = _device_count_from_row(owner_row)
        assert device_count_after_assign == device_count_before + 1
        # Confirmed live: the assignment is genuinely eventually-
        # consistent server-side -- a fixed wait (even several seconds)
        # after the "success" toast is not reliably enough time for the
        # owner's device list itself to reflect it. Poll/retry rather
        # than trust one fixed delay.
        row = admin_device_page.wait_for_device_in_dialog(config["base_url"], REAL_END_USER_FULL_NAME, REAL_IMEI_FOR_ASSIGNMENT)
        assert row is not None and row.count() == 1
    finally:
        # Real-inventory safety net: this device MUST be unassigned no
        # matter what happened above -- same eventual-consistency
        # concern applies here, so this also polls rather than trusting
        # one read (a missed cleanup here leaves a real customer's device
        # list permanently wrong).
        row = admin_device_page.wait_for_device_in_dialog(config["base_url"], REAL_END_USER_FULL_NAME, REAL_IMEI_FOR_ASSIGNMENT)
        if row is not None and row.count() > 0:
            admin_device_page.unassign_device_in_dialog(REAL_IMEI_FOR_ASSIGNMENT)

    admin_device_page.open_manage_device(config["base_url"])
    admin_device_page.page.wait_for_timeout(1500)
    owner_row = admin_device_page.row_by_owner_name(REAL_END_USER_FULL_NAME)
    device_count_final = _device_count_from_row(owner_row)
    assert device_count_final == device_count_before, "Expected device count fully restored after unassign"
