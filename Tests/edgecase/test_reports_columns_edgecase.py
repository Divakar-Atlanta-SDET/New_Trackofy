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


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_col_009_deselect_all_optional_columns(page, config, credentials):
    """REP-COL-009: Edge Case - Deselect all optional columns and generate report."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.uncheck_all_optional_columns()
    reports_page.click_fetch()
    reports_page.wait_for_table()

    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "info"), (
        f"Report should handle deselecting all optional columns, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_col_015_rapid_column_toggling(page, config, credentials):
    """REP-COL-015: Edge Case - Rapidly select and deselect columns."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    for _ in range(3):
        reports_page.toggle_report_column("Distance", check=False)
        reports_page.toggle_report_column("Distance", check=True)
    assert reports_page.is_column_checkbox_checked("Distance"), "Distance should be checked after final toggle"
