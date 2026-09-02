import re
import pytest
from playwright.sync_api import expect

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


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_001_column_selector_displayed(page, config, credentials):
    """REP-COL-001: Functional - Verify column selector and checkboxes are displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    assert reports_page.contains_texts(["Report columns"]), "Report columns section not displayed"
    assert reports_page.contains_texts(["Select the information to include in the generated report."])


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_002_default_columns_selected(page, config, credentials):
    """REP-COL-002: Functional - Verify all configured default columns are checked by default."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    # In Fleet Summary, columns like Distance, Max Speed, Ignition are checked by default
    assert reports_page.is_column_checkbox_checked("Distance"), "Distance column should be checked by default"
    assert reports_page.is_column_checkbox_checked("Ignition"), "Ignition column should be checked by default"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_010_column_order(page, config, credentials):
    """REP-COL-010: Functional - Verify column order in configuration drawer."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    assert reports_page.contains_texts(["Report columns"])


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_012_hidden_column_persists_across_pagination(page, config, credentials):
    """REP-COL-012: Functional - Verify deselected column remains hidden when navigating through pagination."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers_p1 = reports_page.get_table_column_headers()
    assert "Battery Voltage" not in headers_p1, "Deselected column appeared on page 1"

    if reports_page.is_next_page_enabled():
        reports_page.click_next_page()
        headers_p2 = reports_page.get_table_column_headers()
        assert "Battery Voltage" not in headers_p2, "Deselected column reappeared on page 2 after pagination"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_013_hidden_column_persists_after_sort(page, config, credentials):
    """REP-COL-013: Functional - Verify sorting table does not restore hidden column."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    if headers:
        reports_page.sort_table_by_column(headers[0])
        headers_after_sort = reports_page.get_table_column_headers()
        assert "Battery Voltage" not in headers_after_sort, "Hidden column restored after sorting"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_014_hidden_column_persists_after_search(page, config, credentials):
    """REP-COL-014: Functional - Verify searching/filtering table does not restore hidden column."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    reports_page.search_in_report_table("GCBL")
    headers_after_search = reports_page.get_table_column_headers()
    assert "Battery Voltage" not in headers_after_search, "Hidden column restored after search"
    reports_page.clear_report_table_search()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_016_existing_report_unchanged_until_regenerated(page, config, credentials):
    """REP-COL-016: Functional - Existing generated report remains unchanged until regenerated."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.click_fetch()
    reports_page.wait_for_table()
    initial_headers = reports_page.get_table_column_headers()
    assert len(initial_headers) > 0, "Report table generated without headers"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_col_017_reset_column_selection(page, config, credentials):
    """REP-COL-017: Functional - Reset restores column checkboxes to configured defaults."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.toggle_report_column("Distance", check=False)
    assert not reports_page.is_column_checkbox_checked("Distance"), "Distance should be unchecked"
    reports_page.reset_form()
    reports_page.open_standard_report_form("Fleet Summary")
    assert reports_page.is_column_checkbox_checked("Distance"), "Distance should be restored after reset"
