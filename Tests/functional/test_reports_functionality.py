from datetime import datetime

import pytest

from config.config import REPORT_END_DATE, REPORT_START_DATE, REPORT_TEST_VEHICLE_NAME
from Pages.reports_page import ReportsPage
from Tests.functional._network_assertions import assert_successful_backend_fetches


def _normalize_report_date(value: str) -> str:
    month, day, year = value.split("/")
    return f"{day}/{month}/{year}"


def _accepted_report_date_formats(value: str) -> set[str]:
    return {value, _normalize_report_date(value)}


def _today_report_date() -> str:
    return datetime.now().strftime("%d/%m/%Y")


@pytest.mark.functional
def test_reports_catalog_and_first_report_form(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    network_monitor.clear()
    network_monitor.start()
    reports_page.go_to_reports()
    reports_page.wait_for_reports_page()
    network_monitor.stop()
    tabs_state = reports_page.report_tabs_state()
    assert all(tabs_state.values()), f"Expected all report tabs to be visible, got: {tabs_state}"
    assert reports_page.standard_catalog_visible() is True, "Expected Standard reports catalog to be visible"

    reports_page.select_report(1)
    assert reports_page.is_submit_enabled() is False, "Generate button should be disabled before required filters are selected"
    reports_page.click_back()
    reports_page.wait_for_reports_page()


@pytest.mark.functional
@pytest.mark.reports
def test_standard_report_submit_requires_filters_and_reset_clears_them(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    network_monitor.clear()
    network_monitor.start()
    reports_page.open_standard_reports()
    reports_page.open_standard_report_form("Work Hour")
    network_monitor.stop()
    assert_successful_backend_fetches(network_monitor, context="Work Hour report form load")

    assert reports_page.is_submit_enabled() is False, "Generate button should be disabled before filters are selected"

    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.apply_common_date_filters(REPORT_START_DATE, REPORT_END_DATE)

    assert reports_page.is_submit_enabled() is True, "Generate button should be enabled after vehicle and dates are selected"
    assert reports_page.field_value("Start Date") in _accepted_report_date_formats(REPORT_START_DATE), "Start Date should keep the selected value"
    assert reports_page.field_value("End Date") in _accepted_report_date_formats(REPORT_END_DATE), "End Date should keep the selected value"

    reports_page.reset_form()

    today = _today_report_date()
    assert reports_page.is_submit_enabled() is False, "Generate button should be disabled after reset clears vehicle selection"
    assert reports_page.field_value("Start Date") == today, "Start Date should reset to today's date"
    assert reports_page.field_value("End Date") == today, "End Date should reset to today's date"


@pytest.mark.functional
@pytest.mark.reports
def test_work_hour_report_submission_preserves_filters_and_returns_a_valid_result_surface(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    reports_page.open_standard_reports()
    reports_page.open_standard_report_form("Work Hour")

    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.apply_common_date_filters(REPORT_START_DATE, REPORT_END_DATE)
    network_monitor.clear()
    network_monitor.start()
    reports_page.click_fetch()
    reports_page.wait_for_table()
    network_monitor.stop()

    assert reports_page.selected_report_type() == "Work Hour", "Selected report type should remain Work Hour after execution"
    assert reports_page.field_value("Start Date") in _accepted_report_date_formats(REPORT_START_DATE), "Start Date should persist after report execution"
    assert reports_page.field_value("End Date") in _accepted_report_date_formats(REPORT_END_DATE), "End Date should persist after report execution"
    assert_successful_backend_fetches(network_monitor, context="Work Hour report execution")
    result_surface = reports_page.result_surface()
    assert result_surface["kind"] != "missing", f"Expected a table, empty state, or download notice; got: {result_surface}"

    if result_surface["kind"] == "table":
        headers = result_surface["headers"]
        assert {"Date Time", "Location", "Distance(KM)", "Status"}.issubset(set(headers))
    elif result_surface["kind"] == "download_notice":
        assert result_surface["message"].startswith("Work Hour Report Downloaded")
        assert "downloads page" in result_surface["message"]
    else:
        assert result_surface["row_count"] == 0
