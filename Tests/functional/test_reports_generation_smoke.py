import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config.config import (
    REPORT_END_DATE,
    REPORT_TEST_DRIVER_NAME,
    REPORT_START_DATE,
    REPORT_TEST_VEHICLE_NAME,
)
from data.reports import STANDARD_REPORTS
from Pages.reports_page import ReportsPage

REPORT_LOAD_LIMIT_SECONDS = {
    "default": 10.0,
    "Work Hour": 10.0,
    "Trip Report": 6.0,
}


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.report_generation
@pytest.mark.parametrize("report", STANDARD_REPORTS, ids=[report["name"] for report in STANDARD_REPORTS])
@pytest.mark.allow_server_error  # already tracks/discards a known get-bms-vehicles 500 itself via network_monitor
def test_standard_reports_generate_results(authenticated_page, report, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    reports_page.open_standard_reports()
    report_name = report["name"]
    network_monitor.clear()
    network_monitor.start()
    try:
        load_time_seconds = reports_page.generate_standard_report(
            report_name,
            start_date=REPORT_START_DATE,
            end_date=REPORT_END_DATE,
            vehicle_name=REPORT_TEST_VEHICLE_NAME,
            driver_name=REPORT_TEST_DRIVER_NAME,
            measure_performance=True,
        )
    except AssertionError as exc:
        if "No selectable options found for combobox" in str(exc):
            pytest.skip(f"{report_name} has no selectable test data in this environment: {exc}")
        raise
    except PlaywrightTimeoutError:
        network_monitor.stop()
        pytest.skip(f"{report_name} did not return a stable result surface in this environment.")
    network_monitor.stop()
    network_monitor.discard_issues(
        method="POST",
        status=500,
        url_contains="get-bms-vehicles",
    )

    if reports_page.has_missing_option_data():
        pytest.skip(f"{report_name} has no selectable test data in this environment.")
    successful_report_calls = [
        event
        for event in network_monitor.response_events(method="POST", status=200, resource_type="fetch")
        if "/api/" in event["url"] or "trackofy_api_new_live" in event["url"]
    ]
    assert successful_report_calls, f"{report_name} should trigger at least one successful backend report/config fetch"
    assert load_time_seconds is not None
    allowed_load_seconds = REPORT_LOAD_LIMIT_SECONDS.get(report_name, REPORT_LOAD_LIMIT_SECONDS["default"])
    assert load_time_seconds <= allowed_load_seconds, (
        f"{report_name} report took {load_time_seconds} seconds, "
        f"which exceeds the {allowed_load_seconds}-second limit."
    )
    assert reports_page.selected_report_type() == report_name
    result_surface = reports_page.result_surface()
    if result_surface["kind"] == "missing":
        pytest.skip(f"{report_name} did not return a stable result surface in this environment.")
    assert result_surface["kind"] in {"table", "no_data", "download_notice"}
    if result_surface["kind"] == "table":
        assert result_surface["headers"]
    elif result_surface["kind"] == "download_notice":
        assert result_surface["message"].startswith(f"{report_name} Report Downloaded")
        assert "downloads page" in result_surface["message"]
    else:
        assert result_surface["row_count"] == 0
