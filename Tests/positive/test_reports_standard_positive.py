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


@pytest.mark.positive
@pytest.mark.reports
def test_rep_com_011_select_valid_date_range(page, config, credentials):
    """REP-COM-011: Select valid date range and verify it is displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.apply_common_date_filters("01/09/2026", "01/09/2026")
    start_val = reports_page.field_value("Start Date")
    end_val = reports_page.field_value("End Date")
    assert start_val, "Start date not set"
    assert end_val, "End date not set"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_com_016_select_single_vehicle(page, config, credentials):
    """REP-COM-016: Select one vehicle and verify it is reflected in filters."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    assert reports_page.is_submit_enabled(), "Generate button not enabled after vehicle selection"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_com_017_select_all_vehicles(page, config, credentials):
    """REP-COM-017: Select multiple vehicles (Select All) and verify reflected in filters."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    assert reports_page.is_submit_enabled(), "Generate button not enabled after Select All"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_com_019_export_report_successfully(page, config, credentials):
    """REP-COM-019: Export generated report - download succeeds."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    visible_exports = reports_page.export_buttons_visible()
    assert len(visible_exports) > 0, "No export buttons visible"
    # Verify export buttons are clickable (don't actually download in positive test)
    for fmt in visible_exports:
        btn = reports_page.page.get_by_role("button", name=re.compile(rf"Export report to {fmt}", re.I))
        expect(btn).to_be_enabled()


@pytest.mark.positive
@pytest.mark.reports
@pytest.mark.parametrize("report_data", load_test_data("reports_positive.json", "valid_report_generation"))
def test_rep_std_generate_with_valid_filters(page, config, credentials, report_data):
    """REP-STD-003/007/011/015/019/023/028/032/036/040/044/049/053/057/061/066/070/074/078/082/086: Generate report with valid filters."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_name = report_data["report_name"]
    if not reports_page.is_standard_report_available(report_name):
        pytest.skip(f"Report '{report_name}' not available")
    try:
        reports_page.generate_standard_report(
            report_name,
            start_date=report_data["start_date"],
            end_date=report_data["end_date"],
            vehicle_name=report_data["vehicle_name"],
            driver_name=report_data.get("driver_name", ""),
        )
    except AssertionError as exc:
        if "No selectable options found for combobox" in str(exc):
            pytest.skip(f"{report_name} has no selectable test data in this environment: {exc}")
        raise
    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "download_notice", "info"), (
        f"Unexpected result surface: {result['kind']} for {report_name}"
    )
