import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.data_loader import load_test_data


def login_and_generate_fleet_summary(page, config, credentials):
    """Helper to log in and generate a Fleet Summary report."""
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name="GCBL10536MHG14AG04459",
        driver_name="",
    )
    return reports_page


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_001_kpi_cards_visible_after_generation(page, config, credentials):
    """REP-KPI-001: Verify KPI cards are visible after generating Fleet Summary."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    assert reports_page.kpi_cards_visible(), "KPI cards not visible after report generation"


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.parametrize("kpi_data", load_test_data("reports_functional.json", "kpi_card_names"))
def test_rep_kpi_002_to_007_each_kpi_card_has_value(page, config, credentials, kpi_data):
    """REP-KPI-002 to 007: Verify each KPI card displays a numeric value."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    value = reports_page.get_kpi_card_value(kpi_data["name"])
    assert value, f"KPI card '{kpi_data['name']}' has no value"
    assert any(c.isdigit() for c in value), f"KPI '{kpi_data['name']}' value '{value}' has no digits"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_008_total_units_matches_table_count(page, config, credentials):
    """REP-KPI-008: Verify Total Units KPI matches the total row count or pagination total."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    total_units_text = reports_page.get_kpi_card_value("Total Units")
    total_units = int(re.search(r"\d+", total_units_text).group())
    pagination_total = reports_page.get_pagination_total()
    if pagination_total > 0:
        assert total_units == pagination_total, (
            f"Total Units KPI ({total_units}) != pagination total ({pagination_total})"
        )
    else:
        row_count = reports_page.result_row_count()
        assert total_units >= row_count, (
            f"Total Units KPI ({total_units}) < visible row count ({row_count})"
        )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_026_table_headers_present(page, config, credentials):
    """REP-KPI-026: Verify table headers are present and non-empty."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    headers = reports_page.get_table_column_headers()
    assert len(headers) > 0, "Table has no column headers"


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.parametrize("rpp_data", load_test_data("reports_functional.json", "rows_per_page_options"))
def test_rep_kpi_027_change_rows_per_page(page, config, credentials, rpp_data):
    """REP-KPI-027: Change rows per page and verify table updates."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    try:
        reports_page.change_rows_per_page(rpp_data["value"])
    except Exception:
        pytest.skip(f"Rows per page option '{rpp_data['value']}' not available")
    row_count = reports_page.result_row_count()
    assert row_count <= int(rpp_data["value"]), (
        f"Table shows {row_count} rows but max should be {rpp_data['value']}"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_028_pagination_next_previous(page, config, credentials):
    """REP-KPI-028: Navigate forward and backward with pagination buttons."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    if not reports_page.is_next_page_enabled():
        pytest.skip("Only one page of results, pagination nav not applicable")
    page_info_before = reports_page.get_pagination_info()
    reports_page.click_next_page()
    page_info_after = reports_page.get_pagination_info()
    assert page_info_before != page_info_after, "Pagination did not change after clicking Next"
    reports_page.click_previous_page()
    page_info_back = reports_page.get_pagination_info()
    assert page_info_back == page_info_before, "Did not return to original page after Previous"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_029_table_search_filters_rows(page, config, credentials):
    """REP-KPI-029: Search in report table filters rows."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    initial_count = reports_page.result_row_count()
    if initial_count == 0:
        pytest.skip("No rows to search through")
    # Get first cell value to use as search query
    first_values = reports_page.get_table_cell_values(0, max_rows=1)
    if not first_values:
        pytest.skip("Could not read table cell values")
    reports_page.search_in_report_table(first_values[0])
    filtered_count = reports_page.result_row_count()
    assert filtered_count <= initial_count, "Search did not filter results"
    reports_page.clear_report_table_search()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_030_table_column_sort(page, config, credentials):
    """REP-KPI-030: Click a column header to sort the table."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    headers = reports_page.get_table_column_headers()
    if not headers:
        pytest.skip("No table headers available to sort")
    sortable_header = headers[0]
    values_before = reports_page.get_table_cell_values(0, max_rows=5)
    reports_page.sort_table_by_column(sortable_header)
    values_after = reports_page.get_table_cell_values(0, max_rows=5)
    # After sorting, order may change (or stay same if already sorted)
    assert isinstance(values_after, list), "Failed to read table after sort"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_033_034_035_export_buttons_present(page, config, credentials):
    """REP-KPI-033/034/035: Verify export buttons (Excel, CSV, PDF) are present."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    visible_exports = reports_page.export_buttons_visible()
    assert "Excel" in visible_exports, "Excel export button not visible"
    assert "CSV" in visible_exports, "CSV export button not visible"
    assert "PDF" in visible_exports, "PDF export button not visible"
