import re
import tempfile
import time
import pytest
from playwright.sync_api import expect

# Cross-cutting Settings resilience/security/data-integrity concerns
# (SET-176-200), verified once against representative entities (Driver,
# Vehicle Group, BMS Alert) per the module plan, rather than duplicated
# across all 19 Settings entities. SET-186-189 (permission-restricted UI
# and direct unauthorized-API calls) are out of scope: they need a
# restricted-permission test account / raw API credentials this suite
# doesn't have -- not fabricated here. SET-192-194 (vehicle group/location/
# route <-> unit consistency) are already exercised by each module's own
# assignment tests (e.g. test_set_070_view_assigned_vehicles,
# test_set_086 location assignment, route Assign Unit flow) and are not
# repeated here. SET-179 (stale search response race) and SET-182
# (pagination validity after deletion) are not covered -- reliably forcing
# a delayed/out-of-order response or a multi-page dataset adds significant
# setup for lower-confidence payoff given everything else in this file.
# SET-200 (large-dataset performance) has no test-data generator in this
# suite and is not simulated.

_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a4944415478da6360000002000155aabb7b0000000049454e44ae426082"
)


def _dummy_file(suffix: str = ".png") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(_PNG_BYTES)
        return f.name


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


def _fill_valid_driver_form(driver_page, name: str):
    driver_page.fill_personal_info(name, "9876543210", f"{name.lower().replace(' ', '')}@example.com", "01/01/1990")
    driver_page.fill_licence_info(f"DL{str(int(time.time() * 1000))[-13:].zfill(13)}", "01/01/2026", "01/01/2030")
    driver_page.upload_licence_file(_dummy_file())
    driver_page.address_input.fill("123 Test Street")


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_set_176_failed_save_not_shown_as_success(driver_page):
    """SET-176: a forced 500 on the create-driver API must not show a
    success state or a phantom record in the list."""
    name = _unique_name("FailSaveDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)

    driver_page.page.route(
        "**/api/**", lambda route: route.fulfill(status=500, body='{"message":"Internal Server Error"}')
    )
    driver_page.create_driver_btn.click()
    driver_page.page.wait_for_timeout(2000)

    toast = driver_page.page.locator("app-toast")
    if toast.count() > 0 and toast.is_visible():
        assert "success" not in toast.inner_text().lower()

    driver_page.page.unroute("**/api/**")
    driver_page.page.reload()
    driver_page.wait_for_loading_to_finish()
    driver_page.search_and_wait(name)
    expect(driver_page.row_containing(name)).to_have_count(0)


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_set_177_network_failure_during_save(driver_page):
    """SET-177: a network failure during save fails safely -- no phantom
    record, and the app doesn't hang indefinitely."""
    name = _unique_name("NetFailDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)

    driver_page.page.route("**/api/**", lambda route: route.abort("failed"))
    driver_page.create_driver_btn.click()
    driver_page.page.wait_for_timeout(2000)

    driver_page.page.unroute("**/api/**")
    driver_page.page.reload()
    driver_page.wait_for_loading_to_finish()
    driver_page.search_and_wait(name)
    expect(driver_page.row_containing(name)).to_have_count(0)


@pytest.mark.negative
def test_set_178_prevent_duplicate_submission(driver_page):
    """SET-178: rapidly clicking Create Driver twice must only create one record."""
    name = _unique_name("DblClickDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)

    driver_page.create_driver_btn.click(click_count=2, delay=50)
    driver_page.wait_for_dialog_closed()
    driver_page.page.wait_for_timeout(1000)

    try:
        driver_page.search_and_wait(name)
        expect(driver_page.row_containing(name)).to_have_count(1)
    finally:
        driver_page.clear_search_and_wait()
        driver_page.delete_driver(name)


@pytest.mark.negative
def test_set_195_deleting_group_with_assigned_units(vehicle_group_page):
    """SET-195: deleting a Vehicle Group that has units assigned succeeds
    (confirmed live -- no block/warning beyond the standard delete
    confirmation) rather than leaving an orphaned or half-deleted state."""
    name = _unique_name("RefGrp")
    vehicle_group_page.open_add_group_form()
    vehicle_group_page.group_name_input.fill(name)
    vehicle_group_page.select_units(1)
    if vehicle_group_page.units_listbox.is_visible():
        vehicle_group_page.page.keyboard.press("Escape")
    vehicle_group_page.page.wait_for_timeout(500)
    vehicle_group_page.create_group_btn.click()
    vehicle_group_page.wait_for_dialog_closed()
    vehicle_group_page.wait_for_visible(vehicle_group_page.row_containing(name))

    vehicle_group_page.delete_group(name)
    vehicle_group_page.page.reload()
    vehicle_group_page.wait_for_loading_to_finish()
    vehicle_group_page.page.wait_for_timeout(1000)
    expect(vehicle_group_page.row_containing(name)).to_have_count(0)


@pytest.mark.negative
def test_set_196_duplicate_vehicle_group_name_not_prevented(vehicle_group_page):
    """SET-196: creating a second Vehicle Group with an identical name
    succeeds with no validation error -- confirmed live, same product-wide
    gap as Location Control (Bug_Report.md #8). Documents the real
    behavior rather than asserting a rejection the app doesn't perform.
    """
    name = _unique_name("DupGrp")
    for _ in range(2):
        vehicle_group_page.open_add_group_form()
        vehicle_group_page.group_name_input.fill(name)
        vehicle_group_page.select_units(1)
        if vehicle_group_page.units_listbox.is_visible():
            vehicle_group_page.page.keyboard.press("Escape")
        vehicle_group_page.page.wait_for_timeout(500)
        vehicle_group_page.create_group_btn.click()
        vehicle_group_page.wait_for_dialog_closed()
        vehicle_group_page.page.wait_for_timeout(500)

    vehicle_group_page.page.reload()
    vehicle_group_page.wait_for_loading_to_finish()
    vehicle_group_page.page.wait_for_timeout(1000)
    expect(vehicle_group_page.row_containing(name)).to_have_count(2)

    while vehicle_group_page.row_containing(name).count() > 0:
        vehicle_group_page.delete_button(name).first.click()
        vehicle_group_page.wait_for_visible(vehicle_group_page.confirm_delete_btn)
        vehicle_group_page.page.wait_for_timeout(400)
        vehicle_group_page.confirm_delete_btn.click()
        vehicle_group_page.wait_for_dialog_closed()
        vehicle_group_page.page.wait_for_timeout(800)


@pytest.mark.negative
def test_set_197_whitespace_handling_in_driver_name(driver_page):
    """SET-197: leading/trailing whitespace in the Name field is trimmed,
    rejected, or otherwise handled without creating an accidental
    duplicate/malformed record."""
    # Keep the name (and therefore the derived email) short -- names/emails
    # over ~30 chars hit an unrelated backend column-length bug (see
    # Bug_Report.md #12c) that this test isn't meant to exercise.
    raw_name = f"  {_unique_name('WsDrv')}  "
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, raw_name.strip())
    driver_page.name_input.fill(raw_name)
    driver_page.page.wait_for_timeout(300)

    if driver_page.create_driver_btn.is_disabled():
        driver_page.close_driver_dialog()
        return

    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()
    try:
        row = driver_page.row_containing(raw_name.strip())
        expect(row).to_be_visible(timeout=10000)
        displayed_name = row.locator("td").nth(1).inner_text()
        assert displayed_name == displayed_name.strip(), (
            f"expected whitespace to be trimmed in the stored/displayed name, got {displayed_name!r}"
        )
    finally:
        driver_page.delete_driver(raw_name.strip())


@pytest.mark.negative
def test_set_198_numeric_field_rejects_invalid_characters(alert_page):
    """SET-198: a numeric threshold field rejects alphabetic/special input
    (native browser number-input behavior)."""
    page = alert_page("BMS Alert")
    page.open_add_form()
    page.select_vehicles(1)
    page.set_extra_combos()
    field = page.dialog.locator("input[formcontrolname='temp']")
    field.click()
    field.press_sequentially("abc@@12", delay=50)
    value = field.input_value()
    assert value == "12", f"expected only numeric characters to be accepted, got {value!r}"
    page.close_dialog()


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_set_190_session_expiry_during_save(driver_page):
    """SET-190: a 401 on the create-driver API (simulating an expired
    session) rejects the operation safely -- either a login redirect/prompt
    appears, or at minimum no success toast/dialog-closed state is shown
    for what is actually a rejected request."""
    name = _unique_name("SessExpDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)

    driver_page.page.route(
        "**/api/**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}')
    )
    driver_page.create_driver_btn.click()
    driver_page.page.wait_for_timeout(2500)

    redirected_to_login = bool(re.search(r"login|signin|sign-in", driver_page.page.url, re.I))
    if not redirected_to_login:
        toast = driver_page.page.locator("app-toast")
        if toast.count() > 0 and toast.is_visible():
            assert "success" not in toast.inner_text().lower(), (
                "an expired-session (401) submit must not be shown as a success"
            )
    driver_page.page.unroute("**/api/**")
    driver_page.close_driver_dialog()


@pytest.mark.negative
def test_set_199_driver_licence_expiry_before_issue_rejected(driver_page):
    """SET-199: setting DL Expiry Date before DL Issue Date is rejected
    (Create Driver stays disabled or a validation error is shown)."""
    name = _unique_name("BadDateDrv")
    driver_page.open_add_driver_form()
    driver_page.fill_personal_info(name, "9876543210", f"{name.lower().replace(' ', '')}@example.com", "01/01/1990")
    driver_page.fill_licence_info(
        f"DL{str(int(time.time() * 1000))[-13:].zfill(13)}", issue_date="10/08/2026", expiry_date="01/08/2026"
    )
    driver_page.upload_licence_file(_dummy_file())
    driver_page.address_input.fill("123 Test Street")
    driver_page.page.wait_for_timeout(300)

    if driver_page.create_driver_btn.is_enabled():
        driver_page.create_driver_btn.click()
        driver_page.page.wait_for_timeout(1500)
        # If the app allowed it anyway, at minimum don't leave a phantom
        # dialog-closed-but-nothing-created state -- verify what actually happened.
        created = driver_page.row_containing(name).count() > 0
        if created:
            driver_page.search_and_wait(name)
            driver_page.delete_driver(name)
            pytest.fail("Driver was created with DL Expiry Date before DL Issue Date -- expected rejection")
    driver_page.close_driver_dialog()
