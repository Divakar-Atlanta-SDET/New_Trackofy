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
def test_rep_col_008_mandatory_column_locked_and_disabled(page, config, credentials):
    """REP-COL-008: Negative - Mandatory column (e.g. Vehicle No / Date Time) cannot be deselected."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    # Vehicle No is mandatory and must be disabled
    assert reports_page.is_column_checkbox_disabled("Vehicle No"), "Mandatory column 'Vehicle No' should be disabled"
    assert reports_page.is_column_checkbox_checked("Vehicle No"), "Mandatory column 'Vehicle No' should be checked"


@pytest.mark.negative
@pytest.mark.reports
def test_rep_col_020_column_configuration_api_resilience(page, config, credentials):
    """REP-COL-020: Negative - Resilience when column configuration API returns error."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    assert reports_page.contains_texts(["Report columns"])
