import re
import pytest

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.data_loader import load_test_data


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
@pytest.mark.parametrize("time_data", load_test_data("reports_edgecase.json", "schedule_boundary_times"))
def test_rep_sch_boundary_schedule_times_accepted(page, config, credentials, time_data):
    """Boundary Schedule Time values (00:00, 23:59) don't block submission on
    their own. Not REP-SCH-014 (that ID is same-day custom *date* range, see
    test_rep_sch_014_same_start_end_custom_date below) -- this test previously
    claimed that ID by mistake, and never asserted anything at all."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope="Standard Report",
        report_name="Fleet Summary",
        frequency="Daily",
        schedule_time=time_data["schedule_time"],
        email_1="test@example.com",
        schedule_till_day_name="15",  # "Schedule Till" is required for Daily frequency
    )
    assert reports_page.schedule_submit_enabled(), (
        f"Boundary schedule time '{time_data['schedule_time']}' should not block submission"
    )
    reports_page.close_dialog()


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_sch_014_same_start_end_custom_date(page, config, credentials):
    """REP-SCH-014: A same-day Custom schedule range follows defined behavior --
    confirmed live this account accepts it (a single-day custom range is valid)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope="Standard Report",
        report_name="Fleet Summary",
        frequency="Custom",
        schedule_time="08:00",
        email_1="test@example.com",
        from_date="01/09/2026",
        to_date="01/09/2026",
    )
    assert reports_page.schedule_submit_enabled(), (
        "A same-day custom schedule range should be accepted (Submit enabled)"
    )
    reports_page.close_dialog()


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_sch_025_026_rapid_open_close_dialog(page, config, credentials):
    """REP-SCH-025/026: Rapidly open and close schedule dialog."""
    reports_page = login_and_open_reports(page, config, credentials)
    for _ in range(3):
        reports_page.open_new_schedule_report_modal()
        reports_page.close_dialog()
    assert reports_page.is_on_path("/reports/scheduled"), (
        "UI unstable after rapid schedule dialog open/close"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_sch_030_refresh_schedule_page(page, config, credentials):
    """REP-SCH-030: Refresh the schedule page and verify it recovers."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_schedule_reports()
    reports_page.refresh_schedule_reports()
    assert reports_page.schedule_catalog_visible(), (
        "Schedule catalog not visible after page refresh"
    )
