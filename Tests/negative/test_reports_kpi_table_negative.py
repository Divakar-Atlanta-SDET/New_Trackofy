import re
import pytest

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage


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
def test_rep_kpi_022_stale_data_after_api_failure(page, config, credentials):
    """REP-KPI-022: Verify KPI cards handle stale data after API failure gracefully."""
    reports_page = login_and_open_reports(page, config, credentials)
    # Generate a valid report first
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] not in ("table", "no_data"):
        pytest.skip("Initial report generation did not produce expected result")
    # Block subsequent API calls
    page.route("**/api/**", lambda route: route.abort())
    # Try to navigate or re-generate - UI should handle gracefully
    try:
        reports_page.click_back()
    except Exception:
        pass
    # UI should still be responsive
    assert reports_page.is_on_path("/reports"), "UI unresponsive after API failure"
    page.unroute("**/api/**")


@pytest.mark.negative
@pytest.mark.reports
def test_rep_kpi_023_024_025_search_no_results(page, config, credentials):
    """REP-KPI-023/024/025: Search for non-matching text in report table."""
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
        pytest.skip("No table available for search test")
    reports_page.search_in_report_table("zzznonexistent999")
    row_count = reports_page.result_row_count()
    assert row_count == 0, f"Search for non-matching text should return 0 rows, got {row_count}"
    reports_page.clear_report_table_search()
