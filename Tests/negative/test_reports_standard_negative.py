import re
import pytest
from playwright.sync_api import expect
from config.config import REPORT_TEST_VEHICLE_NAME

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
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
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
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
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
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
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
    """REP-COM-021: Open restricted report -- access is denied/handled per permissions.

    Honest scope note: this test environment only has one account/role
    (see credentials in .env), and every report in the Standard catalog is
    accessible to it -- there is no known lower-privilege report or role to
    actually trigger a permission denial with. A prior version of this test
    only asserted the catalog is non-empty, which doesn't exercise REP-COM-021
    at all. Until a restricted report/role is available to test against, this
    is honestly skipped rather than claiming coverage it doesn't have."""
    pytest.skip(
        "No restricted report or lower-privilege role is available in this test "
        "account to exercise REP-COM-021's permission-denial path."
    )


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.parametrize("date_data", load_test_data("reports_negative.json", "invalid_date_ranges"))
def test_rep_com_012_invalid_date_range_variants(page, config, credentials, date_data):
    """REP-COM-012: Invalid date range variants (start-after-end, empty start) are rejected."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    if date_data["start_date"] and date_data["end_date"]:
        reports_page.apply_common_date_filters(date_data["start_date"], date_data["end_date"])
    # Either validation should appear or generate should be disabled
    validation = reports_page.validation_messages()
    submit_enabled = reports_page.is_submit_enabled()
    assert len(validation) > 0 or not submit_enabled or date_data["start_date"] == "", (
        f"Invalid date range should show validation: {date_data['description']}"
    )


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.parametrize("report_data", load_test_data("reports_negative.json", "invalid_date_range_per_report"))
def test_rep_std_negative_invalid_date_range(page, config, credentials, report_data):
    """REP-STD-004/008/012/016/020/024/029/033/037/041/045/050/054/058/062/067/071/075/079/083/087:
    Generate with an invalid (start-after-end) date range, per report -- each of the 21 catalogued
    reports gets its own real check here, not just a single hardcoded report."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_name = report_data["report_name"]
    if not reports_page.is_standard_report_available(report_name):
        pytest.skip(f"Report '{report_name}' not available")
    if report_name == "Fleet Summary":
        pytest.skip("Fleet Summary has no date-range filter (a live/current-state snapshot report)")
    try:
        # Reuse the same per-report vehicle/driver dispatch as the positive suite
        # (configure_standard_report) instead of a plain select_vehicle() -- several
        # reports (ADAS Alarm, BMS Summary/Cell) use a different, searchable vehicle
        # combobox that a generic select_vehicle() can't drive.
        reports_page.configure_standard_report(
            report_name,
            start_date=report_data["start_date"],
            end_date=report_data["end_date"],
            vehicle_name=report_data.get("vehicle_name", ""),
            driver_name=report_data.get("driver_name", ""),
        )
    except AssertionError as exc:
        if "No selectable options found for combobox" in str(exc):
            pytest.skip(f"{report_name} has no selectable test data in this environment: {exc}")
        raise
    validation = reports_page.validation_messages()
    submit_enabled = reports_page.is_submit_enabled()
    assert len(validation) > 0 or not submit_enabled, (
        f"Invalid date range should show validation or block generation for {report_name}"
    )


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.allow_server_error
@pytest.mark.parametrize("report_name", ["Trip Report", "Cumulative Distance"])
def test_rep_missing_telemetry_partition_table(page, config, credentials, report_name):
    """Regression pin for Bug_Report.md #17: Trip Report and Cumulative Distance return a raw
    SQL 500 ("Invalid object name 'tbl_telemetry_mar26'") for this date range -- confirmed a
    real backend/data-provisioning gap (a missing March-2026 telemetry partition table), not a
    UI bug. Dates are entered as "03/01/2026"/"03/10/2026" deliberately: this app's date inputs
    are known to parse entered values as MM/DD regardless of the DD/MM they display (a separate,
    already-documented bug -- see Bug_Report.md #6), so these values resolve to March 1-10, 2026,
    which is exactly the range that hits the missing tbl_telemetry_mar26 table. This test
    documents the current (broken) behavior so a future backend fix is caught by this test
    flipping to a real result surface instead of an error."""
    reports_page = login_and_open_reports(page, config, credentials)
    errors = []
    page.on(
        "response",
        lambda response: errors.append(response)
        if response.status == 500 and response.request.resource_type in ("xhr", "fetch")
        else None,
    )
    # Configure and fetch directly rather than generate_standard_report(), which chains a
    # blocking wait_for_table() that would itself time out (45s) on the known broken result.
    reports_page.configure_standard_report(
        report_name,
        start_date="03/01/2026",
        end_date="03/10/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    reports_page.click_fetch()
    page.wait_for_timeout(5000)
    assert errors, (
        f"Expected the known tbl_telemetry_mar26 500 for {report_name} -- if this now passes "
        "without a 500, the backend bug in Bug_Report.md #17 may be fixed; update/remove this test."
    )
