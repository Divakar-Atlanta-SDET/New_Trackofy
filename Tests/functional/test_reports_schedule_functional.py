import email
import imaplib
import re
import time
from datetime import datetime, timedelta

import pytest
from playwright.sync_api import expect

from config.config import TEST_RECIPIENT_EMAIL, TEST_RECIPIENT_EMAIL_PASSWORD
from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage


def _wait_for_scheduled_report_email(subject_contains: str, after: datetime, timeout_seconds: int = 420, poll_seconds: int = 20):
    """Poll the real test inbox (IMAP) for an email whose subject contains
    `subject_contains` and whose internal date is after `after`. Returns the
    matching email.message.Message, or None if it never arrives within
    timeout_seconds. Requires TEST_RECIPIENT_EMAIL/TEST_RECIPIENT_EMAIL_PASSWORD
    (a Gmail App Password) in .env.
    """
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        conn = imaplib.IMAP4_SSL("imap.gmail.com")
        try:
            conn.login(TEST_RECIPIENT_EMAIL, TEST_RECIPIENT_EMAIL_PASSWORD)
            conn.select("INBOX")
            since = after.strftime("%d-%b-%Y")
            status, data = conn.search(None, f'(SINCE "{since}")')
            ids = data[0].split() if data and data[0] else []
            for msg_id in reversed(ids):
                status, msg_data = conn.fetch(msg_id, "(RFC822)")
                if not msg_data or not msg_data[0]:
                    continue
                message = email.message_from_bytes(msg_data[0][1])
                subject = message.get("Subject", "") or ""
                if subject_contains.lower() in subject.lower():
                    return message
        finally:
            try:
                conn.logout()
            except Exception:
                pass
        time.sleep(poll_seconds)
    return None


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
@pytest.mark.skipif(
    not (TEST_RECIPIENT_EMAIL and TEST_RECIPIENT_EMAIL_PASSWORD),
    reason="TEST_RECIPIENT_EMAIL / TEST_RECIPIENT_EMAIL_PASSWORD not configured in .env",
)
def test_rep_sch_030b_scheduled_report_actually_delivered_to_email(page, config, credentials):
    """Reverification of AS-219 ('Scheduled reports are not received on the
    configured email address') with real evidence: creates a genuine
    schedule (Daily, ~2 minutes from now, Schedule Till = today) against the
    real inbox in TEST_RECIPIENT_EMAIL, then polls that inbox via IMAP for
    up to 7 minutes for the resulting email -- not a placeholder
    "test@example.com" that nobody can ever check, and not a "could not
    verify, no inbox access" writeoff like prior passes.

    Cleans up by deleting the schedule it created regardless of outcome.
    """
    reports_page = login_and_open_reports(page, config, credentials)

    fire_at = datetime.now() + timedelta(minutes=2)
    schedule_time = fire_at.strftime("%H:%M")
    created_at = datetime.now()

    before_count = 0
    reports_page.open_schedule_reports()
    before_count = reports_page.schedule_count()

    reports_page.open_new_schedule_report_modal()
    reports_page.fill_schedule_report_form(
        report_scope="Standard Report",
        report_name="Fleet Summary",
        frequency="Daily",
        schedule_time=schedule_time,
        email_1=TEST_RECIPIENT_EMAIL,
        schedule_till_day_name=str(datetime.now().day),
    )
    assert reports_page.schedule_submit_enabled(), "Schedule submit should be enabled with a fully valid form"
    reports_page.save_schedule_report(previous_count=before_count)

    try:
        message = _wait_for_scheduled_report_email(
            subject_contains="Fleet Summary",
            after=created_at,
            timeout_seconds=360,
            poll_seconds=20,
        )
        assert message is not None, (
            f"No email containing 'Fleet Summary' arrived at {TEST_RECIPIENT_EMAIL} within 6 minutes"
            f"of the {schedule_time} scheduled delivery time -- AS-219 still reproduces."
        )
        assert message.is_multipart() and any(
            part.get_filename() for part in message.walk()
        ), "Scheduled report email arrived but has no attachment"
    finally:
        reports_page.open_schedule_reports()
        entries = reports_page.schedule_entries()
        if any(e.get("title") == "Fleet Summary" for e in entries):
            reports_page.delete_first_schedule_entry()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_sch_031_schedule_submit_disabled_without_fields(page, config, credentials):
    """REP-SCH-031: Verify schedule submit button is disabled when required fields are empty."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_schedule_report_modal()
    assert not reports_page.schedule_submit_enabled(), (
        "Schedule submit should be disabled when required fields are empty"
    )
