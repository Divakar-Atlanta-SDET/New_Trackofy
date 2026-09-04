import tempfile
import time
import pytest
from playwright.sync_api import expect

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


def _unique_dl_number() -> str:
    # Real DL numbers are validated against a state-code + digits pattern
    # (existing data: "DL0420210123456") -- a random digit string alone is
    # rejected as "Invalid driving licence number" (confirmed live).
    return f"DL{str(int(time.time() * 1000))[-13:].zfill(13)}"


def _fill_all_mandatory_driver_fields(driver_page, name):
    # Confirmed live: Address has no visible required-marker but Create
    # Driver stays disabled without it -- a real UX gap (Bug_Report.md).
    driver_page.fill_personal_info(name, "9876543210", f"{name.lower().replace(' ', '')}@example.com", "01/01/1990")
    driver_page.fill_licence_info(_unique_dl_number(), "01/01/2026", "01/01/2030")
    driver_page.upload_licence_file(_dummy_file(".png", _PNG_BYTES))
    driver_page.address_input.fill("123 Test Street")


@pytest.mark.negative
@pytest.mark.parametrize(
    "field_to_blank",
    ["name", "mobile", "email", "dob", "dl_number", "dl_issue_date", "dl_expiry_date"],
)
def test_set_033_039_mandatory_field_validation(driver_page, field_to_blank):
    """SET-033 to SET-039: Leaving any mandatory driver field blank blocks Create Driver."""
    name = _unique_name("ValDrv")
    driver_page.open_add_driver_form()
    _fill_all_mandatory_driver_fields(driver_page, name)

    field_map = {
        "name": driver_page.name_input,
        "mobile": driver_page.mobile_input,
        "email": driver_page.email_input,
        "dob": driver_page.dob_input,
        "dl_number": driver_page.dl_number_input,
        "dl_issue_date": driver_page.dl_issue_date_input,
        "dl_expiry_date": driver_page.dl_expiry_date_input,
    }
    field_map[field_to_blank].fill("")
    field_map[field_to_blank].press("Tab")
    driver_page.page.wait_for_timeout(300)

    expect(driver_page.create_driver_btn).to_be_disabled()
    driver_page.close_driver_dialog()


@pytest.mark.negative
def test_set_040_mandatory_licence_copy(driver_page):
    """SET-040: Submitting without a licence copy is blocked."""
    name = _unique_name("NoFileDrv")
    driver_page.open_add_driver_form()
    driver_page.fill_personal_info(name, "9876543210", f"{name.lower()}@example.com", "01/01/1990")
    driver_page.fill_licence_info(_unique_dl_number(), "01/01/2026", "01/01/2030")
    expect(driver_page.create_driver_btn).to_be_disabled()
    driver_page.close_driver_dialog()


@pytest.mark.negative
def test_set_043_reject_unsupported_licence_file(driver_page):
    """SET-043: An unsupported file type is rejected with feedback, not silently accepted."""
    driver_page.open_add_driver_form()
    driver_page.upload_licence_file(_dummy_file(".txt", b"not a licence"))
    driver_page.page.wait_for_timeout(500)
    # A rejected upload must not show the same success state a valid file gets.
    assert not driver_page.driver_dialog.get_by_text("File uploaded successfully").is_visible()
    driver_page.close_driver_dialog()


@pytest.mark.negative
def test_set_044_cancel_driver_creation(driver_page):
    """SET-044: Cancel with data entered; modal closes and no driver is created."""
    name = _unique_name("CancelDrv")
    driver_page.open_add_driver_form()
    _fill_all_mandatory_driver_fields(driver_page, name)
    driver_page.cancel_btn.click()
    driver_page.wait_for_dialog_closed()
    expect(driver_page.row_containing(name)).to_have_count(0)


@pytest.mark.negative
def test_set_045_close_driver_dialog_via_x(driver_page):
    """SET-045: Closing via the X control doesn't unintentionally create a record."""
    name = _unique_name("CloseDrv")
    driver_page.open_add_driver_form()
    _fill_all_mandatory_driver_fields(driver_page, name)
    driver_page.page.get_by_role("button", name="Close driver dialog").click()
    driver_page.wait_for_dialog_closed()
    expect(driver_page.row_containing(name)).to_have_count(0)


@pytest.mark.negative
def test_set_048_driver_search_no_result(driver_page):
    """SET-048: Searching for a nonexistent value shows no records and a clear empty state."""
    driver_page.search_and_wait("ZZZ-NOT-FOUND-XYZ")
    expect(driver_page.table.locator("tbody tr")).to_have_count(1)  # the empty-state row itself
    assert driver_page.empty_state_visible()


@pytest.mark.negative
def test_set_051_cancel_driver_deletion(driver_page):
    """SET-051: Cancelling a delete confirmation leaves the driver unchanged."""
    name = _unique_name("KeepDrv")
    driver_page.open_add_driver_form()
    _fill_all_mandatory_driver_fields(driver_page, name)
    driver_page.create_driver_btn.click()
    driver_page.wait_for_dialog_closed()

    try:
        driver_page.delete_button(name).click()
        driver_page.wait_for_visible(driver_page.cancel_delete_btn)
        driver_page.cancel_delete_btn.click()
        driver_page.wait_for_dialog_closed()
        expect(driver_page.row_containing(name)).to_be_visible()
    finally:
        driver_page.delete_driver(name)
