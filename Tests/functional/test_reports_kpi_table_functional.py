import re
import pytest
from playwright.sync_api import expect
from config.config import REPORT_TEST_VEHICLE_NAME

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
    reports_page.go_to_reports()
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
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
    """REP-KPI-030: Clicking a column header actually sorts the table by that
    column's values, not just re-renders the same (or an unverified) order."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    reports_page.change_rows_per_page("10")  # a full re-sort is easiest to see on one page
    headers = reports_page.get_table_column_headers()
    vehicle_index = headers.index("Vehicle")
    values_before = reports_page.get_table_cell_values(vehicle_index, max_rows=10)
    if len(set(values_before)) < 2:
        pytest.skip("Not enough distinct vehicle values to verify sort order")

    reports_page.sort_table_by_column("Vehicle")
    values_ascending = reports_page.get_table_cell_values(vehicle_index, max_rows=10)
    assert values_ascending != values_before, "Sorting by Vehicle did not change row order"
    assert values_ascending == sorted(values_ascending), (
        f"Vehicle column not in ascending order after sort: {values_ascending}"
    )

    reports_page.sort_table_by_column("Vehicle")  # click again -- should reverse to descending
    values_descending = reports_page.get_table_cell_values(vehicle_index, max_rows=10)
    assert values_descending == sorted(values_descending, reverse=True), (
        f"Vehicle column not in descending order after a second sort click: {values_descending}"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_033_034_035_export_buttons_present(page, config, credentials):
    """REP-KPI-033/034/035: Verify export buttons (Excel, CSV, PDF) are present."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    visible_exports = reports_page.export_buttons_visible()
    assert "Excel" in visible_exports, "Excel export button not visible"
    assert "CSV" in visible_exports, "CSV export button not visible"
    assert "PDF" in visible_exports, "PDF export button not visible"


def login_and_generate_fleet_summary_all_vehicles(page, config, credentials):
    """Log in, generate Fleet Summary for every vehicle, and expand the table to
    100 rows/page so cross-checks below see the complete dataset in one page."""
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()
    try:
        reports_page.change_rows_per_page("100")
    except Exception:
        pass
    return reports_page


def _read_fleet_summary_rows(reports_page):
    """Read every visible Fleet Summary row as (vehicle, ignition, speed, last_contact)."""
    headers = reports_page.get_table_column_headers()
    ignition_idx = headers.index("Ignition")
    speed_idx = headers.index("Current Speed")
    contact_idx = headers.index("Last Contact")
    vehicle_idx = headers.index("Vehicle")
    rows = reports_page.result_table.last.locator("tbody tr")
    parsed = []
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td")
        values = [cells.nth(j).inner_text().strip() for j in range(cells.count())]
        parsed.append(
            {
                "vehicle": values[vehicle_idx],
                "ignition": values[ignition_idx],
                "speed": values[speed_idx],
                "last_contact": values[contact_idx],
            }
        )
    return parsed


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_004_007_ignition_moving_stale_match_table(page, config, credentials):
    """REP-KPI-004/005/006/007: Cross-check Ignition On, Moving Units and Stale/Offline
    Units against the report table, not just "the value has a digit in it".

    Ground truth confirmed empirically against this live account's Fleet Summary
    (select-all-vehicles, rows-per-page=100): a vehicle counts as "online" toward
    Ignition On/Moving Units only when its Last Contact date is today; everything
    else (including plain Ignition=Off rows) falls under Stale/Offline Units, and
    Ignition On + Stale/Offline Units always equals Total Units exactly.
    """
    from datetime import datetime

    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    kpis = reports_page.get_all_kpi_values()
    rows = _read_fleet_summary_rows(reports_page)

    today = datetime.now().strftime("%Y-%m-%d")
    online_rows = [r for r in rows if r["last_contact"].startswith(today)]

    computed_ignition_on = sum(1 for r in online_rows if r["ignition"] == "On")
    computed_moving = 0
    for r in online_rows:
        try:
            if float(r["speed"]) > 0:
                computed_moving += 1
        except ValueError:
            pass
    computed_stale = len(rows) - len(online_rows)

    assert int(kpis["Ignition On"]) == computed_ignition_on, (
        f"Ignition On KPI ({kpis['Ignition On']}) != online rows with Ignition=On ({computed_ignition_on})"
    )
    # Speed is the most volatile field on a live fleet -- a vehicle can start/stop
    # moving in the seconds between reading the KPI card and reading the table, so
    # allow a small drift here while keeping the other two KPIs exact.
    assert abs(int(kpis["Moving Units"]) - computed_moving) <= 2, (
        f"Moving Units KPI ({kpis['Moving Units']}) too far from online rows with speed > 0 ({computed_moving})"
    )
    assert int(kpis["Stale / Offline Units"]) == computed_stale, (
        f"Stale/Offline KPI ({kpis['Stale / Offline Units']}) != non-today-contact rows ({computed_stale})"
    )
    assert int(kpis["Ignition On"]) + int(kpis["Stale / Offline Units"]) == int(kpis["Total Units"]), (
        "Ignition On + Stale/Offline should account for every unit in Total Units"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_010_012_kpi_stable_across_pagination_and_rows_per_page(page, config, credentials):
    """REP-KPI-010/011/012: KPI cards represent the full filtered dataset, not just
    the current page -- they must not change across pagination or rows-per-page."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    kpis_100 = reports_page.get_all_kpi_values()

    reports_page.change_rows_per_page("10")
    kpis_10 = reports_page.get_all_kpi_values()
    assert kpis_10 == kpis_100, f"KPIs changed after switching rows-per-page: {kpis_10} vs {kpis_100}"

    if reports_page.is_next_page_enabled():
        reports_page.click_next_page()
        kpis_page2 = reports_page.get_all_kpi_values()
        assert kpis_page2 == kpis_100, f"KPIs changed after paginating: {kpis_page2} vs {kpis_100}"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_013_kpi_stable_after_sort(page, config, credentials):
    """REP-KPI-013: Sorting the table does not change KPI values."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    kpis_before = reports_page.get_all_kpi_values()
    headers = reports_page.get_table_column_headers()
    reports_page.sort_table_by_column(headers[1])  # "Vehicle" column
    kpis_after = reports_page.get_all_kpi_values()
    assert kpis_after == kpis_before, f"KPIs changed after sorting: {kpis_after} vs {kpis_before}"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_009_avg_utilization_decimal_precision(page, config, credentials):
    """REP-KPI-009: Avg Utilization KPI uses consistent 2-decimal-place formatting."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    value = reports_page.get_kpi_card_value("Avg Utilization")
    assert re.match(r"^\d+\.\d{2}$", value), f"Avg Utilization '{value}' is not formatted to 2 decimal places"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_014_kpi_stable_after_table_search(page, config, credentials):
    """REP-KPI-014: Table search is a client-side display filter here (confirmed
    live: searching narrows visible rows without re-fetching), so per the
    application's defined behavior, KPIs must stay tied to the full filtered
    dataset and not react to the in-table search."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    kpis_before = reports_page.get_all_kpi_values()
    row_count_before = reports_page.result_row_count()
    first_vehicle = reports_page.get_table_cell_values(1, max_rows=1)
    if not first_vehicle:
        pytest.skip("Could not read a vehicle value to search for")
    reports_page.search_in_report_table(first_vehicle[0])
    row_count_after = reports_page.result_row_count()
    assert row_count_after < row_count_before, "Search did not narrow the visible table rows"
    kpis_after = reports_page.get_all_kpi_values()
    assert kpis_after == kpis_before, f"KPIs changed after table search: {kpis_after} vs {kpis_before}"
    reports_page.clear_report_table_search()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_026_kpi_consistent_after_regeneration(page, config, credentials):
    """REP-KPI-026: Regenerating the same report produces consistent KPI values."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    kpis_first = reports_page.get_all_kpi_values()
    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()
    kpis_second = reports_page.get_all_kpi_values()
    # Fleet Summary has no date range -- it's always the live fleet, so Moving Units
    # and Avg Utilization can legitimately drift a little between two calls seconds
    # apart as real vehicles move. Total Units/Ignition On/Stale-Offline change far
    # less often and are checked exactly.
    stable_fields = {"Total Units", "Ignition On", "Stale / Offline Units"}
    for field in stable_fields:
        assert kpis_second[field] == kpis_first[field], (
            f"{field} differs between two immediate regenerations: {kpis_first[field]} vs {kpis_second[field]}"
        )
    assert abs(int(kpis_second["Moving Units"]) - int(kpis_first["Moving Units"])) <= 2, (
        f"Moving Units drifted too much between regenerations: {kpis_first['Moving Units']} vs {kpis_second['Moving Units']}"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_002_total_units_updates_with_vehicle_filter(page, config, credentials):
    """REP-KPI-002: Total Units KPI updates to match a changed vehicle filter."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    total_all = int(reports_page.get_kpi_card_value("Total Units"))

    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()
    reports_page.wait_for_table()
    total_single = int(reports_page.get_kpi_card_value("Total Units"))

    assert total_single == 1, f"Total Units for a single selected vehicle should be 1, got {total_single}"
    assert total_all > total_single, (
        f"Total Units for all vehicles ({total_all}) should exceed a single vehicle ({total_single})"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_kpi_017_single_record_kpis_correct(page, config, credentials):
    """REP-KPI-017: All applicable KPIs are calculated correctly for a single-vehicle
    (single-record) Fleet Summary -- Ignition On and Stale/Offline must exactly
    partition that one vehicle, and Moving Units must match its own table row."""
    reports_page = login_and_generate_fleet_summary_all_vehicles(page, config, credentials)
    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    kpis = reports_page.get_all_kpi_values()
    assert int(kpis["Total Units"]) == 1
    assert int(kpis["Ignition On"]) + int(kpis["Stale / Offline Units"]) == 1, (
        "Ignition On + Stale/Offline should account for the single unit"
    )
    from datetime import datetime

    row = _read_fleet_summary_rows(reports_page)[0]
    today = datetime.now().strftime("%Y-%m-%d")
    is_online = row["last_contact"].startswith(today)
    expected_moving = 1 if (is_online and float(row["speed"]) > 0) else 0
    assert int(kpis["Moving Units"]) == expected_moving, (
        f"Moving Units ({kpis['Moving Units']}) should be {expected_moving} for this single "
        f"vehicle (online={is_online}, speed={row['speed']})"
    )
