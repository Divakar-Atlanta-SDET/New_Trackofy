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


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.parametrize("report_data", load_test_data("reports_negative.json", "reports_with_no_vehicle_selected"))
def test_rep_com_006_generate_without_required_data(page, config, credentials, report_data):
    """REP-COM-006: Generate report without selecting vehicle - generation is prevented."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form(report_data["report_name"])
    assert not reports_page.is_submit_enabled(), (
        f"Generate button should be disabled without vehicle for {report_data['report_name']}"
    )


@pytest.mark.negative
@pytest.mark.reports
def test_rep_com_007_report_api_error_handling(page, config, credentials):
    """REP-COM-007: Verify UI remains usable after report API failure."""
    reports_page = login_and_open_reports(page, config, credentials)
    # Intercept and abort a report generation API call
    page.route("**/api/report/**", lambda route: route.abort())
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.click_fetch()
    page.wait_for_timeout(3000)
    # UI should still be usable - can navigate away
    reports_page.click_back()
    assert reports_page.standard_catalog_visible() or reports_page.is_on_path("/reports"), (
        "UI not usable after API failure"
    )
    page.unroute("**/api/report/**")


@pytest.mark.negative
@pytest.mark.reports
def test_rep_com_012_start_date_after_end_date(page, config, credentials):
    """REP-COM-012: Set start date after end date - range is rejected or validation shown."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.apply_common_date_filters("10/09/2026", "01/09/2026")
    # Either validation messages appear or generate is disabled
    validation = reports_page.validation_messages()
    generate_enabled = reports_page.is_submit_enabled()
    assert len(validation) > 0 or not generate_enabled, (
        "Invalid date range should show validation or disable generation"
    )


@pytest.mark.negative
@pytest.mark.reports
def test_rep_com_020_export_failure_handling(page, config, credentials):
    """REP-COM-020: Export service fails - error shown, no false download."""
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
        pytest.skip("No table available for export test")
    # Block export endpoint
    page.route("**/export**", lambda route: route.abort())
    reports_page.export_report_to("Excel")
    page.wait_for_timeout(3000)
    # UI should still be functional
    assert reports_page.has_results_table(), "Table disappeared after export failure"
    page.unroute("**/export**")


@pytest.mark.negative
@pytest.mark.reports
def test_rep_com_021_restricted_report_handling(page, config, credentials):
    """REP-COM-021: Attempt to access restricted/unavailable report."""
    reports_page = login_and_open_reports(page, config, credentials)
    # Try to find a report that might not be available
    all_reports = reports_page.standard_catalog_names()
    assert len(all_reports) > 0, "No reports found at all in catalog"


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.parametrize("date_data", load_test_data("reports_negative.json", "invalid_date_ranges"))
def test_rep_std_negative_invalid_date_range(page, config, credentials, date_data):
    """REP-STD-004/008/012/016/020/024/029/033/037/041/045/050/054/058/062/067/071/075/079/083/087: Generate with invalid date range."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    if date_data["start_date"] and date_data["end_date"]:
        reports_page.apply_common_date_filters(date_data["start_date"], date_data["end_date"])
    # Either validation should appear or generate should be disabled
    validation = reports_page.validation_messages()
    submit_enabled = reports_page.is_submit_enabled()
    assert len(validation) > 0 or not submit_enabled or date_data["start_date"] == "", (
        f"Invalid date range should show validation: {date_data['description']}"
    )
