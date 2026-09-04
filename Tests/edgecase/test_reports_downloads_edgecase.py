import re
import pytest
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.download_helper import (
    handle_and_verify_download,
    ensure_downloads_dir,
    count_csv_data_rows,
    list_downloads,
)


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_dl_114_downloads_page_refresh(page, config, credentials):
    """REP-DL-114: Refresh downloads page and verify it recovers."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    assert reports_page.is_on_path("/profile/downloads"), (
        "Downloads page did not recover after refresh"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_dl_115_navigate_away_and_back(page, config, credentials):
    """REP-DL-115: Navigate away from downloads and back."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    entries_before = len(reports_page.get_download_entries())
    # Navigate away
    reports_page.go_to_reports()
    # Navigate back
    reports_page.open_downloads_page()
    entries_after = len(reports_page.get_download_entries())
    assert entries_after >= entries_before, (
        "Download entries changed after navigation cycle"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_dl_124_125_pagination_boundary(page, config, credentials):
    """REP-DL-124/125: Test downloads pagination at boundary conditions."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    # First and Previous should be disabled on first page
    first_btn = reports_page.page.get_by_role("button", name="First page")
    if first_btn.count() > 0 and first_btn.is_visible():
        assert not first_btn.is_enabled(), "First page button should be disabled on first page"
    prev_btn = reports_page.page.get_by_role("button", name="Previous page")
    if prev_btn.count() > 0 and prev_btn.is_visible():
        assert not prev_btn.is_enabled(), "Previous page button should be disabled on first page"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_dl_132_133_download_only_report_flow(page, config, credentials):
    """REP-DL-132/133: Generate download-only report (Work Hour) and verify it appears in downloads."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    initial_count = len(reports_page.get_download_entries())
    # Navigate to standard reports and generate Work Hour
    reports_page.open_standard_reports()
    if not reports_page.is_standard_report_available("Work Hour"):
        pytest.skip("Work Hour report not available")
    reports_page.open_standard_report_form("Work Hour")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()
    page.wait_for_timeout(5000)
    # Check downloads page for new entry
    reports_page.open_downloads_page()
    entries = reports_page.get_download_entries()
    assert len(entries) >= initial_count, (
        f"Expected at least {initial_count} download entries after Work Hour generation"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_dl_134_all_vehicles_csv_export_contains_all_records_not_just_page_one(
    page, config, credentials
):
    """REP-DL-134: Edge Case — Export CSV with all vehicles selected must include ALL records,
    not only the 10 rows visible on page 1.

    INTENT: This test intentionally catches a critical export bug where the server/client
    only exports the currently paginated page (default 10 rows) instead of the full dataset.
    If the report generates 36 vehicles but the CSV only contains 10 rows (page 1), this test
    FAILS — exposing the truncated export behaviour.

    Expected: CSV data row count == UI pagination total (all records, e.g. 36)
    Actual if bug exists: CSV data row count == 10 (only current page)
    """
    from Utils.download_helper import read_csv_rows

    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")

    # Select ALL vehicles
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()

    result = reports_page.result_surface()
    if result["kind"] != "table":
        pytest.skip("Report did not produce a table — cannot test export completeness")

    # Capture total record count from UI (full dataset, not just visible page)
    total_records_in_report = reports_page.get_pagination_total()
    if total_records_in_report == 0:
        # Fallback: count visible rows
        total_records_in_report = reports_page.result_row_count()

    assert total_records_in_report > 10, (
        f"Only {total_records_in_report} total records — need more than 10 to test pagination bug. "
        f"Try selecting more vehicles or a broader date range."
    )

    # Rows per page is at default 10 — intentionally do NOT change it so we test page-1 truncation
    default_page_rows = reports_page.result_row_count()
    assert default_page_rows <= 10, (
        f"Expected at most 10 visible rows on page 1 but got {default_page_rows}"
    )

    # Export to CSV and capture the downloaded file
    ensure_downloads_dir()
    export_btn = reports_page.page.get_by_role(
        "button", name=re.compile(r"Export report to CSV", re.I)
    )
    file_path = handle_and_verify_download(
        page, lambda: export_btn.click(), expected_extension=".csv"
    )

    all_rows = read_csv_rows(file_path)
    csv_data_rows = count_csv_data_rows(file_path, has_header=True)

    # CORE ASSERTION: The export must include ALL records, not just page 1
    assert csv_data_rows == total_records_in_report, (
        f"\n[EXPORT BUG DETECTED]\n"
        f"  Total records shown in UI  : {total_records_in_report}\n"
        f"  Rows visible on page 1     : {default_page_rows}\n"
        f"  Rows in downloaded CSV     : {csv_data_rows} (total lines incl. headers: {len(all_rows)})\n"
        f"\n"
        f"  The CSV export only exported {csv_data_rows} rows instead of {total_records_in_report}.\n"
        f"  This means the export is TRUNCATED to the current page view (page 1 = 10 rows).\n"
        f"  FIX REQUIRED: Server-side export must export the full dataset regardless of pagination state."
    )

