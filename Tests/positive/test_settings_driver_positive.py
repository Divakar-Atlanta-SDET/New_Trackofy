import tempfile
import time
import pytest
from playwright.sync_api import expect

# Minimal valid 1x1 PNG (67 bytes) -- enough for the app to accept as a real image upload.
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a4944415478da6360000002000155aabb7b0000000049454e44ae426082"
)


def _dummy_file(suffix: str, content: bytes = b"dummy") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def _unique_name(prefix: str) -> str:
    # Real Name-field validation is alphabets-and-spaces only (confirmed
    # live) -- digits are rejected, so the "unique" part has to be letters.
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


def _unique_dl_number(prefix: str = "DL") -> str:
    # Real DL numbers are validated against a state-code + digits pattern
    # (existing data: "DL0420210123456") -- a random digit string alone is
    # rejected as "Invalid driving licence number" (confirmed live).
    return f"{prefix}{str(int(time.time() * 1000))[-13:].zfill(13)}"


def _fill_valid_driver_form(driver_page, name: str):
    """Fill every field Create Driver actually requires to enable.
    Confirmed live: Address has no visible required-marker in the UI but the
    button stays disabled without it -- a real UX gap (flagged in
    Bug_Report.md), not something to design the test around silently."""
    driver_page.fill_personal_info(name, "9876543210", f"{name.lower().replace(' ', '')}@example.com", "01/01/1990")
    driver_page.fill_licence_info(_unique_dl_number(), "01/01/2026", "01/01/2030")
    driver_page.upload_licence_file(_dummy_file(".png", _PNG_BYTES))
    driver_page.address_input.fill("123 Test Street")


@pytest.mark.positive
def test_set_032_create_driver_with_valid_data(driver_page):
    """SET-032: Create driver with valid mandatory data; driver appears in the list."""
    name = _unique_name("AutoDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)
    expect(driver_page.create_driver_btn).to_be_enabled()
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()

    try:
        expect(driver_page.row_containing(name)).to_be_visible()
    finally:
        driver_page.delete_driver(name)


@pytest.mark.positive
@pytest.mark.parametrize("suffix", [".pdf", ".jpg", ".jpeg", ".png"])
def test_set_041_042_upload_supported_licence_formats(driver_page, suffix):
    """SET-041, SET-042: Upload each supported licence file format; file is accepted."""
    driver_page.open_add_driver_form()
    driver_page.upload_licence_file(_dummy_file(suffix, _PNG_BYTES))
    expect(driver_page.driver_dialog).to_contain_text("File uploaded successfully")
    driver_page.close_driver_dialog()


@pytest.mark.positive
def test_set_046_driver_search_exact_match(driver_page):
    """SET-046: Search with an exact existing driver name; matching driver is displayed."""
    first_row_name = driver_page.table.locator("tbody tr").first.locator("td").nth(1).inner_text().strip()
    if not first_row_name:
        pytest.skip("No existing driver to search for on this account")
    driver_page.search_and_wait(first_row_name)
    expect(driver_page.row_containing(first_row_name)).to_be_visible()


@pytest.mark.positive
def test_set_047_driver_search_partial_match(driver_page):
    """SET-047: Search with a partial driver name; matching records are displayed."""
    first_row_name = driver_page.table.locator("tbody tr").first.locator("td").nth(1).inner_text().strip()
    if len(first_row_name) < 2:
        pytest.skip("No existing driver name long enough to test a partial search")
    driver_page.search_and_wait(first_row_name[: len(first_row_name) // 2])
    expect(driver_page.row_containing(first_row_name)).to_be_visible()


@pytest.mark.positive
def test_set_049_edit_driver(driver_page):
    """SET-049: Edit a driver; only intended values change and changes persist after refresh."""
    name = _unique_name("EditDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()

    try:
        new_contact = "9123456780"
        driver_page.open_edit_driver_form(name)
        original_email = driver_page.email_input.input_value()
        driver_page.mobile_input.fill(new_contact)
        driver_page.update_driver_btn.click()
        driver_page.wait_for_dialog_closed()

        driver_page.page.reload()
        driver_page.wait_for_loading_to_finish()
        driver_page.search_and_wait(name)
        row = driver_page.row_containing(name)
        expect(row).to_contain_text(new_contact)
        expect(row).to_contain_text(original_email)  # unrelated field untouched
    finally:
        driver_page.clear_search_and_wait()
        driver_page.delete_driver(name)


@pytest.mark.positive
def test_set_050_delete_driver(driver_page):
    """SET-050: Delete a driver; it is removed and stays removed after refresh."""
    name = _unique_name("DelDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()
    expect(driver_page.row_containing(name)).to_be_visible()

    driver_page.delete_driver(name)
    driver_page.page.reload()
    driver_page.wait_for_loading_to_finish()
    driver_page.search_and_wait(name)
    expect(driver_page.row_containing(name)).to_have_count(0)


@pytest.mark.positive
def test_set_053_change_driver_assigned_unit(driver_page):
    """SET-053: Change a driver's assigned unit; driver is associated with the new unit."""
    name = _unique_name("ReassignDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()

    try:
        driver_page.assign_unit_button(name).click()
        driver_page.wait_for_visible(driver_page.assignment_vehicle_select)
        driver_page.assignment_vehicle_select.click()
        options = driver_page.page.get_by_role("option")
        if options.count() < 2:
            pytest.skip("Fewer than 2 vehicles available on this account to test reassignment")
        first_vehicle = options.nth(0).inner_text().strip()
        options.nth(0).click()
        driver_page._submit_assignment_if_needed()

        driver_page.assign_unit_button(name).click()
        driver_page.wait_for_visible(driver_page.assignment_vehicle_select)
        driver_page.assignment_vehicle_select.click()
        options = driver_page.page.get_by_role("option")
        second_vehicle = None
        for i in range(options.count()):
            text = options.nth(i).inner_text().strip()
            if text != first_vehicle:
                second_vehicle = text
                options.nth(i).click()
                break
        if second_vehicle is None:
            pytest.skip("No other vehicle available on this account to reassign to")
        driver_page._submit_assignment_if_needed()

        driver_page.page.reload()
        driver_page.wait_for_loading_to_finish()
        driver_page.search_and_wait(name)
        expect(driver_page.row_containing(name)).to_contain_text(second_vehicle)
    finally:
        driver_page.clear_search_and_wait()
        driver_page.delete_driver(name)


@pytest.mark.positive
def test_set_052_assign_driver_to_unit(driver_page):
    """SET-052: Assign a driver to a unit; assignment persists after refresh."""
    name = _unique_name("AssignDrv")
    driver_page.open_add_driver_form()
    _fill_valid_driver_form(driver_page, name)
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()

    try:
        driver_page.assign_unit_button(name).click()
        driver_page.wait_for_visible(driver_page.assignment_vehicle_select)
        driver_page.assignment_vehicle_select.click()
        first_option = driver_page.page.get_by_role("option").first
        if first_option.count() == 0:
            pytest.skip("No vehicles available on this account to assign")
        vehicle_name = first_option.inner_text().strip()
        first_option.click()
        driver_page._submit_assignment_if_needed()

        driver_page.page.reload()
        driver_page.wait_for_loading_to_finish()
        driver_page.search_and_wait(name)
        expect(driver_page.row_containing(name)).to_contain_text(vehicle_name)
    finally:
        driver_page.clear_search_and_wait()
        driver_page.delete_driver(name)
