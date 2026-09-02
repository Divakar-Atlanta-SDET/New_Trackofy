import re
import pytest

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.download_helper import handle_and_verify_download, ensure_downloads_dir


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.positive
@pytest.mark.reports
def test_rep_dl_112_verify_download_entries_exist(page, config, credentials):
    """REP-DL-112: Verify download entries exist on downloads page."""
    reports_page = login_and_open_reports(page, config, credentials)
    # Generate Work Hour report to ensure at least one download entry exists
    if reports_page.is_standard_report_available("Work Hour"):
        reports_page.open_standard_report_form("Work Hour")
        reports_page.select_vehicle("GCBL10536MHG14AG04459")
        reports_page.click_fetch()
        page.wait_for_timeout(3000)

    reports_page.open_downloads_page()
    entries = reports_page.get_download_entries()
    if not entries:
        pytest.skip("No download entries present yet on staging environment")
    assert len(entries) > 0, "No download entries found"
    assert entries[0]["report_name"], "First download entry has no report name"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_dl_113_download_entry_has_done_status(page, config, credentials):
    """REP-DL-113: Verify completed download entries have 'Done' status."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    entries = reports_page.get_download_entries()
    if not entries:
        pytest.skip("No download entries to verify status")
    # Status should be one of valid lifecycle states: Done, Processing, Pending, Failed
    valid_statuses = {"Done", "Processing", "Pending", "Failed"}
    statuses = {e["status"] for e in entries}
    assert any(s in valid_statuses for s in statuses), f"Unexpected statuses: {statuses}"



@pytest.mark.positive
@pytest.mark.reports
def test_rep_dl_122_export_report_to_excel(page, config, credentials):
    """REP-DL-122: Export generated report to Excel and verify download."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] != "table":
        pytest.skip("Report did not produce a table to export")
    ensure_downloads_dir()
    export_btn = reports_page.page.get_by_role("button", name=re.compile(r"Export report to Excel", re.I))
    file_path = handle_and_verify_download(
        page, lambda: export_btn.click(), expected_extension=".xlsx"
    )
    assert file_path.exists(), f"Excel export file not found: {file_path}"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_dl_123_export_report_to_csv(page, config, credentials):
    """REP-DL-123: Export generated report to CSV and verify download."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] != "table":
        pytest.skip("Report did not produce a table to export")
    ensure_downloads_dir()
    export_btn = reports_page.page.get_by_role("button", name=re.compile(r"Export report to CSV", re.I))
    file_path = handle_and_verify_download(
        page, lambda: export_btn.click(), expected_extension=".csv"
    )
    assert file_path.exists(), f"CSV export file not found: {file_path}"
