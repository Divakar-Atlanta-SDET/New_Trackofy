import random
from collections import Counter
from datetime import datetime, timedelta

import pytest

from Pages.reports_page import ReportsPage
from Tests.functional._network_assertions import assert_successful_backend_fetches


def _future_schedule_time(minutes_from_now: int) -> str:
    return (datetime.now() + timedelta(minutes=minutes_from_now)).strftime("%H:%M")


def _future_schedule_day(days_from_now: int) -> str:
    return str((datetime.now() + timedelta(days=days_from_now)).day)


def _entry_counter(entries: list[dict[str, str]]) -> Counter:
    return Counter(tuple(sorted(entry.items())) for entry in entries)


@pytest.mark.functional
@pytest.mark.reports
def test_schedule_report_create_and_delete_changes_schedule_state(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    create_time = _future_schedule_time(7)
    email = f"test.schedule.{int(datetime.now().timestamp())}@example.com"

    network_monitor.clear()
    network_monitor.start()
    reports_page.open_schedule_reports()
    network_monitor.stop()
    before_entries = reports_page.schedule_entries()
    before_count = len(before_entries)
    assert_successful_backend_fetches(network_monitor, context="Schedule reports list load")

    reports_page.open_new_schedule_report_modal()
    report_options = reports_page.available_schedule_report_names("Standard Report")
    assert report_options
    selected_report = random.choice(report_options)

    reports_page.fill_schedule_report_form(
        report_scope="Standard Report",
        report_name=selected_report,
        frequency="Daily",
        schedule_time=create_time,
        email_1=email,
        schedule_till_day_name=_future_schedule_day(1),
    )

    form_values = reports_page.schedule_form_values()
    assert reports_page.schedule_submit_enabled() is True
    assert form_values["vehicles"]
    assert form_values["report_scope"] == "Standard Report"
    assert form_values["standard_report"] == selected_report
    assert form_values["frequency"] == "Daily"
    assert form_values["schedule_time"] == create_time
    assert form_values["email_1"] == email

    network_monitor.clear()
    network_monitor.start()
    reports_page.save_schedule_report(previous_count=before_count)
    network_monitor.stop()
    assert_successful_backend_fetches(network_monitor, context="Schedule report create")
    reports_page.refresh_schedule_reports()

    after_create_entries = reports_page.schedule_entries()
    assert len(after_create_entries) == before_count + 1

    created_entries = _entry_counter(after_create_entries) - _entry_counter(before_entries)
    assert sum(created_entries.values()) == 1

    created_entry = dict(next(created_entries.elements()))
    assert created_entry["title"] == selected_report
    assert created_entry["frequency"] == "Daily"
    assert after_create_entries[0] == created_entry

    network_monitor.clear()
    network_monitor.start()
    reports_page.delete_first_schedule_entry(previous_count=len(after_create_entries))
    network_monitor.stop()
    assert_successful_backend_fetches(network_monitor, context="Schedule report delete")
    reports_page.refresh_schedule_reports()
    after_delete_entries = reports_page.schedule_entries()
    assert len(after_delete_entries) == before_count
    assert _entry_counter(after_delete_entries) == _entry_counter(before_entries)


@pytest.mark.functional
@pytest.mark.reports
def test_schedule_report_form_rejects_empty_submission(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)

    network_monitor.clear()
    network_monitor.start()
    reports_page.open_schedule_reports()
    network_monitor.stop()
    before_count = reports_page.schedule_count()
    assert_successful_backend_fetches(network_monitor, context="Schedule report empty-form baseline")

    reports_page.open_new_schedule_report_modal()
    assert reports_page.schedule_submit_enabled() is False
    reports_page.close_dialog()

    reports_page.open_schedule_reports()
    assert reports_page.schedule_count() == before_count
