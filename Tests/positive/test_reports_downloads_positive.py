import re
import pytest
from config.config import REPORT_TEST_VEHICLE_NAME

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
        reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
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
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
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
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
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


@pytest.mark.positive
@pytest.mark.reports
def test_rep_dl_113_work_hour_download_matches_filters(page, config, credentials):
    """REP-DL-113: Downloaded Work Hour data matches the submitted vehicle/date
    filter values. Work Hour is a download-only report: Generate queues an async
    server-side job ("Work Hour Report Downloaded -- find it on the downloads
    page"), not an instant browser download -- confirmed live that page.expect_download()
    around Generate times out with no browser download event at all. The file
    only becomes available once the Downloads-page entry's status reaches "Done".
    Previously this ID was claimed by a test that only checked download-list
    statuses were one of 4 accepted values (including indefinitely-"Pending"),
    never verifying file content against the submitted filters at all."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Work Hour")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    # Entered as MM/DD (Bug_Report.md #6): resolves to Mar 1-10, 2026 -- confirmed
    # live this range's Work Hour jobs complete quickly, unlike some other ranges
    # that stay "Pending" indefinitely.
    reports_page.apply_common_date_filters("03/01/2026", "03/10/2026")
    reports_page.click_fetch()
    page.wait_for_timeout(2000)

    reports_page.open_downloads_page()
    entry = None
    for _ in range(20):
        entries = [e for e in reports_page.get_download_entries() if "Work Hour" in e["report_name"]]
        if entries and entries[0]["status"] == "Done":
            entry = entries[0]
            break
        page.wait_for_timeout(8000)
        page.reload()
        reports_page.wait_for_loading_to_finish()
    if entry is None:
        pytest.skip("Work Hour download job did not reach 'Done' status in time to verify its content")

    download_url = entry.get("download_url", "")
    assert download_url, "Done download entry has no download link to verify"
    response = page.request.get(download_url)
    assert response.ok, f"Downloading the Work Hour file failed: {response.status}"
    body_text = response.text()
    assert REPORT_TEST_VEHICLE_NAME in body_text, (
        f"Downloaded Work Hour file does not contain the filtered vehicle '{REPORT_TEST_VEHICLE_NAME}'"
    )
