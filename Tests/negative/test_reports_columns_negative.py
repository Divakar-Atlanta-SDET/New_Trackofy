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
@pytest.mark.allow_server_error
def test_rep_col_020_column_configuration_api_resilience(page, config, credentials):
    """REP-COL-020: When the column configuration API fails, an appropriate error
    is shown and the app does not silently generate a report with an incorrect
    (e.g. empty or default-only) column configuration."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_category_for("Fleet Summary")
    page.route("**/api/v2/table_columns", lambda route: route.fulfill(status=500, body="{}"))
    reports_page._standard_report_button("Fleet Summary").click()
    page.wait_for_timeout(3000)
    page.unroute("**/api/v2/table_columns")

    form_opened = page.get_by_text("Configure report filters", exact=False).count() > 0
    checkbox_count = page.get_by_role("checkbox").count()
    has_error_state = reports_page.contains_any_text(["error", "failed", "try again", "unable to load", "No Data"])
    # The form must not silently open with a fully-populated column list as if
    # nothing failed -- either it doesn't open cleanly, or it shows no columns /
    # a visible error instead of proceeding as normal.
    assert (not form_opened) or checkbox_count == 0 or has_error_state, (
        f"Column configuration API failed but the form opened normally with {checkbox_count} "
        "column checkboxes and no visible error -- looks like a silently-defaulted config"
    )
