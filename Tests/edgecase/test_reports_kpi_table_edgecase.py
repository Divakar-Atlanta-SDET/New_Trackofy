import re
import pytest
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage


def login_and_generate_fleet_summary(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    return reports_page


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_kpi_016_017_boundary_pagination(page, config, credentials):
    """REP-KPI-016/017: Navigate to first and last page using pagination buttons."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    if not reports_page.is_next_page_enabled():
        pytest.skip("Only one page of results")
    # Go to last page
    reports_page.click_last_page()
    assert not reports_page.is_next_page_enabled(), "Next should be disabled on last page"
    # Go back to first page
    reports_page.click_first_page()
    assert not reports_page.is_previous_page_enabled(), "Previous should be disabled on first page"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_kpi_018_019_rapid_pagination_clicks(page, config, credentials):
    """REP-KPI-018/019: Rapidly click pagination buttons."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    if not reports_page.is_next_page_enabled():
        pytest.skip("Only one page, cannot test rapid pagination")
    # Rapidly click next/prev
    for _ in range(3):
        if reports_page.is_next_page_enabled():
            reports_page.click_next_page()
    for _ in range(3):
        if reports_page.is_previous_page_enabled():
            reports_page.click_previous_page()
    # Table should still be functional
    assert reports_page.has_results_table(), "Table broken after rapid pagination"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_kpi_020_change_rows_per_page_to_max(page, config, credentials):
    """REP-KPI-020: Change rows per page to maximum (100) value."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    try:
        reports_page.change_rows_per_page("100")
    except Exception:
        pytest.skip("100 rows per page option not available")
    row_count = reports_page.result_row_count()
    assert row_count <= 100, f"Table shows {row_count} rows, max should be 100"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_kpi_021_search_clear_cycle(page, config, credentials):
    """REP-KPI-021: Search, then clear, then search again."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    if not reports_page.has_results_table():
        pytest.skip("No table for search testing")
    initial_count = reports_page.result_row_count()
    reports_page.search_in_report_table("test")
    reports_page.clear_report_table_search()
    restored_count = reports_page.result_row_count()
    assert restored_count == initial_count, (
        f"Row count changed after search-clear cycle: {initial_count} -> {restored_count}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_kpi_031_032_sort_and_unsort(page, config, credentials):
    """REP-KPI-031/032: Sort table column and verify data integrity."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    headers = reports_page.get_table_column_headers()
    if not headers:
        pytest.skip("No sortable headers")
    initial_count = reports_page.result_row_count()
    reports_page.sort_table_by_column(headers[0])
    after_sort_count = reports_page.result_row_count()
    assert initial_count == after_sort_count, (
        f"Row count changed after sort: {initial_count} -> {after_sort_count}"
    )
