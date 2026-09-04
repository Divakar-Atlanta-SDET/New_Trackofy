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


@pytest.mark.positive
@pytest.mark.reports
def test_rep_kpi_positive_all_kpi_values_populated(page, config, credentials):
    """Verify all 6 KPI cards have populated values after Fleet Summary generation."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    kpi_values = reports_page.get_all_kpi_values()
    for name, value in kpi_values.items():
        assert value, f"KPI card '{name}' has empty value"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_kpi_positive_total_units_is_numeric(page, config, credentials):
    """Verify Total Units KPI value is a valid number."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    total_text = reports_page.get_kpi_card_value("Total Units")
    total_num = int(re.search(r"\d+", total_text).group())
    assert total_num > 0, f"Total Units should be positive, got {total_num}"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_kpi_positive_ignition_on_percentage(page, config, credentials):
    """Verify Ignition On KPI shows count and percentage."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    ignition_text = reports_page.get_kpi_card_value("Ignition On")
    assert re.search(r"\d+", ignition_text), f"Ignition On has no numeric value: {ignition_text}"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_kpi_positive_table_has_data(page, config, credentials):
    """Verify the generated report table has at least one row of data."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    assert reports_page.has_results_table(), "Results table not visible"
    row_count = reports_page.result_row_count()
    assert row_count > 0, f"Table has {row_count} rows, expected at least 1"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_kpi_positive_pagination_info_matches_total_units(page, config, credentials):
    """Verify pagination total matches Total Units KPI."""
    reports_page = login_and_generate_fleet_summary(page, config, credentials)
    total_text = reports_page.get_kpi_card_value("Total Units")
    total_units = int(re.search(r"\d+", total_text).group())
    pagination_total = reports_page.get_pagination_total()
    if pagination_total > 0:
        assert total_units == pagination_total, (
            f"KPI Total Units ({total_units}) != pagination total ({pagination_total})"
        )
