import pytest

from Pages.reports_page import ReportsPage
from data.reports import CUSTOM_REPORT_FIELDS, SCHEDULE_REPORT_FIELDS
from Tests.functional._network_assertions import assert_successful_backend_fetches


@pytest.mark.functional
@pytest.mark.reports
def test_custom_reports_catalog_and_new_report_wizard(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    network_monitor.clear()
    network_monitor.start()
    reports_page.open_custom_reports()
    network_monitor.stop()
    assert all(reports_page.report_tabs_state().values())
    assert reports_page.custom_catalog_visible() is True
    assert_successful_backend_fetches(network_monitor, context="Custom reports catalog")

    reports_page.open_new_custom_report_modal()
    assert reports_page.contains_texts(CUSTOM_REPORT_FIELDS)
    reports_page.close_dialog()
    assert reports_page.custom_catalog_visible() is True


@pytest.mark.functional
@pytest.mark.reports
def test_schedule_reports_catalog_and_new_schedule_wizard(authenticated_page, network_monitor):
    reports_page = ReportsPage(authenticated_page)
    network_monitor.clear()
    network_monitor.start()
    reports_page.open_schedule_reports()
    network_monitor.stop()
    assert all(reports_page.report_tabs_state().values())
    assert reports_page.schedule_catalog_visible() is True
    assert_successful_backend_fetches(network_monitor, context="Schedule reports catalog")

    reports_page.open_new_schedule_report_modal()
    assert reports_page.contains_texts(SCHEDULE_REPORT_FIELDS)
    reports_page.close_dialog()
    assert reports_page.schedule_catalog_visible() is True
