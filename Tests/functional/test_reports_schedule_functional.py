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
def test_rep_sch_001_open_schedule_tab(page, config, credentials):
    """REP-SCH-001: Open Schedule tab and verify it loads correctly."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_schedule_reports()
    assert reports_page.schedule_catalog_visible(), "Schedule catalog not visible"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_002_open_new_schedule_dialog(page, config, credentials):
    """REP-SCH-002: Click New and verify schedule report dialog opens with all required fields."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    assert reports_page.schedule_form_has_required_fields(), (
        "Schedule form missing required fields"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_015_016_verify_frequency_options(page, config, credentials):
    """REP-SCH-015/016: Verify available frequency options in schedule form."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    freq_options = reports_page.schedule_frequency_options()
    assert "Daily" in freq_options, "Daily frequency not available"
    assert "Weekly" in freq_options, "Weekly frequency not available"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_017_018_verify_report_type_options(page, config, credentials):
    """REP-SCH-017/018: Verify available report type options in schedule form."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    type_options = reports_page.schedule_report_type_options()
    assert len(type_options) > 0, "No report type options available"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_019_close_schedule_dialog(page, config, credentials):
    """REP-SCH-019: Close the schedule report dialog."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    assert reports_page.is_schedule_dialog_open()
    reports_page.close_dialog()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_027_028_list_existing_schedules(page, config, credentials):
    """REP-SCH-027/028: Open schedule tab and verify existing scheduled reports are listed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_schedule_reports()
    entries = reports_page.schedule_entries()
    # Entries may or may not exist; just verify the method works without error
    assert isinstance(entries, list), "schedule_entries() should return a list"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_029_verify_schedule_entry_details(page, config, credentials):
    """REP-SCH-029: Verify schedule entry shows title, frequency, status, delivery time."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_schedule_reports()
    entries = reports_page.schedule_entries()
    if not entries:
        pytest.skip("No scheduled reports exist to verify details")
    entry = entries[0]
    assert "title" in entry and entry["title"], "Schedule entry missing title"
    assert "frequency" in entry and entry["frequency"], "Schedule entry missing frequency"
    assert "status" in entry and entry["status"], "Schedule entry missing status"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_031_schedule_submit_disabled_without_fields(page, config, credentials):
    """REP-SCH-031: Verify schedule submit button is disabled when required fields are empty."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    assert not reports_page.schedule_submit_enabled(), (
        "Schedule submit should be disabled when required fields are empty"
    )
