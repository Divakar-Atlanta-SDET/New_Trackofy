"""Supplementary Reports-module coverage beyond both source CSVs
(reports_module_all_automation_test_cases.csv, reports_kpi_table_validation_test_cases.csv),
added per the audit plan's Phase 6."""
import re
import pytest
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.download_helper import ensure_downloads_dir, handle_and_verify_download


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.functional
@pytest.mark.reports
def test_supp_excel_export_contains_all_records_not_just_page_one(page, config, credentials):
    """Extends REP-DL-134's CSV-truncation check to Excel: an all-vehicles Fleet
    Summary export to .xlsx must include every record, not just the first page."""
    import openpyxl

    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()

    result = reports_page.result_surface()
    if result["kind"] != "table":
        pytest.skip("Report did not produce a table -- cannot test export completeness")

    total_records = reports_page.get_pagination_total() or reports_page.result_row_count()
    if total_records <= 10:
        pytest.skip(f"Only {total_records} records -- need more than 10 to exercise pagination truncation")

    ensure_downloads_dir()
    export_btn = page.get_by_role("button", name=re.compile(r"Export report to Excel", re.I))
    file_path = handle_and_verify_download(page, lambda: export_btn.click(), expected_extension=".xlsx")

    workbook = openpyxl.load_workbook(file_path, read_only=True)
    sheet = workbook.active
    data_row_count = max(sheet.max_row - 1, 0)  # minus header row
    workbook.close()

    assert data_row_count == total_records, (
        f"Excel export has {data_row_count} data rows but the UI shows {total_records} total "
        f"records -- export looks truncated to the current page, same bug class as REP-DL-134"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_supp_distance_consistent_between_distance_chart_and_cumulative_distance(page, config, credentials):
    """Cross-report data consistency: the same vehicle/date range's total
    distance should agree between Distance Chart's "Total(km)" and Cumulative
    Distance's "Total Distance(km)" -- both explicitly date-ranged reports that
    should be reading the same underlying telemetry, just presented differently.
    (Fleet Summary was tried first as a comparison point but its "Distance"
    column is a live/current-state value -- Fleet Summary has no date filter at
    all -- so it isn't a valid comparison against a date-ranged total; confirmed
    live it reads 0 for a range that both date-ranged reports agree is 55.13km.)"""
    reports_page = login_and_open_reports(page, config, credentials)
    # Entered as MM/DD (Bug_Report.md #6): resolves to Aug 20-28, 2026 -- a range
    # already confirmed live to have real telemetry data for this vehicle.
    reports_page.generate_standard_report(
        "Distance Chart",
        start_date="08/20/2026",
        end_date="08/28/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] != "table" or result["row_count"] == 0:
        pytest.skip("Distance Chart did not return a row for this vehicle to compare")
    dc_headers = reports_page.get_table_column_headers()
    dc_index = dc_headers.index("Total(km)")
    distance_chart_total = float(reports_page.get_table_cell_values(dc_index, max_rows=1)[0])

    reports_page.click_back()
    reports_page.generate_standard_report(
        "Cumulative Distance",
        start_date="08/20/2026",
        end_date="08/28/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] != "table" or result["row_count"] == 0:
        pytest.skip("Cumulative Distance did not return a row for this vehicle to compare")
    cd_headers = reports_page.get_table_column_headers()
    cd_index = cd_headers.index("Total Distance(km)")
    cumulative_distance_total = float(reports_page.get_table_cell_values(cd_index, max_rows=1)[0])

    assert abs(distance_chart_total - cumulative_distance_total) <= max(0.5, distance_chart_total * 0.05), (
        f"Distance Chart's Total(km) ({distance_chart_total}) and Cumulative Distance's Total "
        f"Distance(km) ({cumulative_distance_total}) disagree for the same vehicle/date range "
        "by more than a small tolerance -- these should be reading the same underlying telemetry"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_supp_report_catalog_cards_keyboard_activatable(page, config, credentials):
    """Extends REP-REL-011 (which only covers the Standard/Custom/Schedule tabs)
    to the report catalog cards themselves: a report card reachable by keyboard
    Tab can be opened with Enter, not just a mouse click."""
    reports_page = login_and_open_reports(page, config, credentials)
    fleet_summary_card = page.get_by_role("button", name=re.compile(r"\bFleet Summary\b"))
    reports_page.wait_for_visible(fleet_summary_card.first)
    fleet_summary_card.first.focus()
    focused_text = page.evaluate("() => document.activeElement ? document.activeElement.textContent : ''")
    assert "Fleet Summary" in focused_text, "Fleet Summary report card did not receive keyboard focus"

    page.keyboard.press("Enter")
    reports_page.wait_for_visible(page.get_by_text("Configure report filters", exact=False).first)
    assert reports_page.contains_texts(["Fleet Summary", "Configure report filters"]), (
        "Enter on a keyboard-focused report card should open its configuration form"
    )
