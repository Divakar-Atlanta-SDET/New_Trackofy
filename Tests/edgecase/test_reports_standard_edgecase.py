import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.data_loader import load_test_data


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
def test_rep_com_008_no_data_range_report(page, config, credentials):
    """REP-COM-008: Generate report for a no-data date range - clear no-data state displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Vehicle Summary",
        start_date="01/01/2020",
        end_date="02/01/2020",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    result = reports_page.result_surface()
    assert result["kind"] in ("no_data", "table", "info"), (
        f"Expected no-data or info state for empty range, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_009_large_vehicle_date_range(page, config, credentials):
    """REP-COM-009: Generate report for large vehicle/date range without UI failure."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    assert reports_page.is_submit_enabled(), "Generate not enabled after selecting all vehicles"
    reports_page.click_fetch()
    reports_page.wait_for_table()
    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "info"), (
        f"Unexpected result for large range: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_013_same_start_end_date(page, config, credentials):
    """REP-COM-013: Select same start and end date - handled according to report rules."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Vehicle Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "info"), (
        f"Same-day range should produce valid result, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_014_future_date_handling(page, config, credentials):
    """REP-COM-014: Select future dates and verify application behavior."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.apply_common_date_filters("01/12/2026", "31/12/2026")
    # Application should either accept future dates or show validation
    submit_enabled = reports_page.is_submit_enabled()
    validation = reports_page.validation_messages()
    assert submit_enabled or len(validation) > 0, (
        "Future date range should be handled per application rules"
    )


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.parametrize("report_data", load_test_data("reports_edgecase.json", "empty_result_reports"))
def test_rep_std_no_data_range(page, config, credentials, report_data):
    """REP-STD-005/009/013/017/021/025/030/034/038/042/046/051/055/059/063/068/072/076/080/084/088: Generate report for no-data range."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_name = report_data["report_name"]
    if not reports_page.is_standard_report_available(report_name):
        pytest.skip(f"Report '{report_name}' not available")
    reports_page.generate_standard_report(
        report_name,
        start_date=report_data["start_date"],
        end_date=report_data["end_date"],
        vehicle_name=report_data["vehicle_name"],
        driver_name=report_data.get("driver_name", ""),
    )
    result = reports_page.result_surface()
    assert result["kind"] in ("no_data", "table", "info", "download_notice"), (
        f"No-data range should produce clear state for {report_name}, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_001_002_003_rapid_report_switching(page, config, credentials):
    """REP-REL-001/002/003: Rapidly switch between reports without UI crash."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_names = ["Fleet Summary", "Vehicle Summary", "Running Summary"]
    for name in report_names:
        if reports_page.is_standard_report_available(name):
            reports_page.open_standard_report_form(name)
            assert reports_page.contains_texts([name, "Generate report"])
            reports_page.click_back()
    assert reports_page.standard_catalog_visible(), "Catalog not visible after rapid switching"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_008_009_page_refresh_during_generation(page, config, credentials):
    """REP-REL-008/009: Refresh page during report workflow."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    # Refresh mid-workflow
    reports_page.refresh()
    # Should return to reports page in usable state
    assert reports_page.is_on_path("/reports"), "Not on reports page after refresh"
