import time
import pytest
from playwright.sync_api import expect
from Utils.download_helper import handle_and_verify_download

# Cross-cutting Settings CRUD behavior (SET-174-200), verified once against
# representative entities (Driver, Vehicle Group) rather than duplicated
# across all 19 Settings entities -- per-entity CRUD/persistence/unrelated-
# field-untouched checks already exist in each module's own test files
# (e.g. test_set_049_edit_driver covers SET-174/175, test_set_048 covers
# SET-183, test_set_051 covers part of SET-180) and are not repeated here.


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.functional
def test_set_181_search_clearing_restores_list(driver_page):
    """SET-181: clearing a search restores the full applicable list."""
    all_rows_before = driver_page.table.locator("tbody tr").count()
    first_name = driver_page.table.locator("tbody tr").first.locator("td").nth(1).inner_text().strip()
    if not first_name:
        pytest.skip("No existing driver to search for on this account")

    driver_page.search_and_wait(first_name)
    expect(driver_page.row_containing(first_name)).to_be_visible()

    driver_page.clear_search_and_wait()
    expect(driver_page.table.locator("tbody tr")).to_have_count(all_rows_before)


@pytest.mark.functional
def test_set_184_export_contains_correct_data(driver_page, cleanup_downloads):
    """SET-184: exporting the driver list produces a real file with correct
    driver data -- the downloaded filename itself reads "Unit_List_..."
    rather than anything Driver-related (see Bug_Report.md #12b), so this
    checks the file's actual content, not its name.
    """
    file_path = handle_and_verify_download(
        driver_page.page, lambda: driver_page.export_csv_btn.click(), expected_extension=".csv"
    )
    assert file_path.stat().st_size > 0
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    assert "DL No" in content and "Assigned Unit" in content, (
        "expected driver-specific columns in the exported CSV"
    )


@pytest.mark.functional
def test_set_185_print_output(driver_page):
    """SET-185: the print action opens a print view without error (no crash,
    no unhandled dialog left blocking the page)."""
    with driver_page.page.expect_event("popup", timeout=5000) as popup_info:
        driver_page.print_btn.click()
    popup = popup_info.value
    popup.wait_for_load_state("load", timeout=10000)
    popup.wait_for_timeout(1000)
    body_text = popup.locator("body").inner_text()
    assert body_text.strip(), "expected the print view to render real table content"
    popup.close()
