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
def test_rep_sch_014_boundary_schedule_times(page, config, credentials, time_data):
    """REP-SCH-014: Schedule at boundary times (midnight, end of day)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    time_input = reports_page.page.get_by_role("combobox", name="Schedule Time")
    reports_page.wait_for_visible(time_input)
    time_input.fill(time_data["schedule_time"])
    # Should accept boundary times without error
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
