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


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_004_submit_without_filling_form(page, config, credentials):
    """REP-SCH-004: Attempt to submit schedule without filling required fields."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    assert not reports_page.schedule_submit_enabled(), (
        "Schedule submit should be disabled without required fields"
    )


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_005_submit_without_email(page, config, credentials):
    """REP-SCH-005: Fill form but leave email empty - submit should be disabled."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.select_all_schedule_vehicles()
    # Don't fill email
    assert not reports_page.schedule_submit_enabled(), (
        "Schedule submit should be disabled without email"
    )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.parametrize("config_data", load_test_data("reports_negative.json", "invalid_schedule_configs"))
def test_rep_sch_invalid_email_configs(page, config, credentials, config_data):
    """Email-address validation variants for the schedule form (empty/malformed
    email). Renamed from the old test_rep_sch_010_013_invalid_schedule_config,
    which claimed REP-SCH-010/011/012/013 (missing report, missing frequency,
    invalid/backwards custom range) but its backing data was 100% email
    scenarios -- none of those 4 IDs ever actually ran. Real REP-SCH-010/011/012/013
    tests are below."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope=config_data["report_scope"],
        report_name=config_data["report_name"],
        frequency=config_data["frequency"],
        schedule_time=config_data["schedule_time"],
        email_1=config_data["email_1"],
    )
    # With invalid email, submit should either be disabled or show validation
    if reports_page.schedule_submit_enabled():
        reports_page.schedule_action_button().click()
        reports_page.wait_for_loading_to_finish()
        page.wait_for_timeout(2000)
        validation = reports_page.validation_messages()
        # If dialog is still open, the submission was rejected
        assert reports_page.is_schedule_dialog_open() or len(validation) > 0, (
            f"Invalid schedule config accepted: {config_data['description']}"
        )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_010_save_without_report_selected(page, config, credentials):
    """REP-SCH-010: Save without selecting a report -- schedule not saved,
    report validation is shown (Submit stays disabled)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.select_all_schedule_vehicles()
    reports_page._open_combobox_options("Select Report Type")
    reports_page._select_option("Standard Report")
    # Deliberately skip selecting a specific report.
    assert not reports_page.schedule_submit_enabled(), (
        "Submit should be disabled without a specific report selected"
    )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_011_save_without_frequency(page, config, credentials):
    """REP-SCH-011: Save without selecting frequency -- schedule not saved,
    frequency validation is shown (Submit stays disabled)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.select_all_schedule_vehicles()
    reports_page._open_combobox_options("Select Report Type")
    reports_page._select_option("Standard Report")
    reports_page._open_combobox_options("Select Standard Report")
    reports_page._select_option("Fleet Summary")
    # Deliberately skip selecting a frequency.
    assert not reports_page.schedule_submit_enabled(), (
        "Submit should be disabled without a frequency selected"
    )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_012_013_invalid_custom_date_range(page, config, credentials):
    """REP-SCH-012/013: A Custom-frequency schedule with start date after end
    date is rejected or shows validation."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope="Standard Report",
        report_name="Fleet Summary",
        frequency="Custom",
        schedule_time="08:00",
        email_1="test@example.com",
        from_date="10/09/2026",
        to_date="01/09/2026",
    )
    submit_enabled = reports_page.schedule_submit_enabled()
    validation = reports_page.validation_messages()
    assert not submit_enabled or len(validation) > 0, (
        "Custom schedule with start date after end date should be rejected or show validation"
    )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_020_invalid_email_format(page, config, credentials):
    """REP-SCH-020: Enter invalid email format in schedule form."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    email_input = reports_page.page.get_by_role("textbox", name="Email 1")
    email_input.fill("not-an-email")
    email_input.evaluate(
        "(el) => { el.dispatchEvent(new Event('blur', { bubbles: true })); }"
    )
    reports_page.wait_for_loading_to_finish()
    validation = reports_page.validation_messages()
    is_submit_disabled = not reports_page.schedule_submit_enabled()
    assert len(validation) > 0 or is_submit_disabled, (
        "Invalid email should show validation or prevent submission"
    )
    reports_page.close_dialog()


@pytest.mark.negative
@pytest.mark.reports
def test_rep_sch_024_missing_report_type(page, config, credentials):
    """REP-SCH-024: Attempt schedule with vehicles but no report type selected."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    reports_page.select_all_schedule_vehicles()
    # Don't select report type
    assert not reports_page.schedule_submit_enabled(), (
        "Submit should be disabled without report type"
    )
    reports_page.close_dialog()
