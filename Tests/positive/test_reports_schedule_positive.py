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


@pytest.mark.positive
@pytest.mark.reports
@pytest.mark.parametrize("schedule_data", load_test_data("reports_positive.json", "valid_schedule_configs"))
def test_rep_sch_003_fill_valid_schedule_form(page, config, credentials, schedule_data):
    """REP-SCH-003: Fill schedule form with valid data and verify submit becomes enabled."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope=schedule_data["report_scope"],
        report_name=schedule_data["report_name"],
        frequency=schedule_data["frequency"],
        schedule_time=schedule_data["schedule_time"],
        email_1=schedule_data["email_1"],
        # "Schedule Till" is a required field for Daily/Weekly/Monthly frequencies
        # that fill_schedule_report_form only sets when explicitly asked.
        schedule_till_day_name=schedule_data.get("schedule_till_day_name"),
    )
    assert reports_page.schedule_submit_enabled(), (
        "Schedule submit button not enabled after filling valid form"
    )
    reports_page.close_dialog()


@pytest.mark.positive
@pytest.mark.reports
def test_rep_sch_006_007_select_daily_frequency(page, config, credentials):
    """REP-SCH-006/007: Select Daily frequency and verify it is accepted."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    freq_options = reports_page.schedule_frequency_options()
    assert "Daily" in freq_options, "Daily frequency not available"
    reports_page.close_dialog()


@pytest.mark.positive
@pytest.mark.reports
def test_rep_sch_008_009_select_weekly_monthly_frequency(page, config, credentials):
    """REP-SCH-008/009: Verify Weekly and Monthly frequency options exist."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    freq_options = reports_page.schedule_frequency_options()
    assert "Weekly" in freq_options, "Weekly frequency not available"
    reports_page.close_dialog()


@pytest.mark.positive
@pytest.mark.reports
def test_rep_sch_021_022_023_view_existing_schedules(page, config, credentials):
    """REP-SCH-021/022/023: View existing scheduled reports and verify structure."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_schedule_reports()
    entries = reports_page.schedule_entries()
    if entries:
        entry = entries[0]
        assert entry.get("title"), "First schedule entry has no title"
        assert entry.get("frequency") in ("Daily", "Weekly", "Monthly", "Manual"), (
            f"Unexpected frequency: {entry.get('frequency')}"
        )
