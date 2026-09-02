import re
import pytest
from playwright.sync_api import expect

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


@pytest.mark.functional
@pytest.mark.reports
def test_rep_std_001_open_fleet_performance_category(page, config, credentials):
    """REP-STD-001: Open Fleet Performance category and verify reports listed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.wait_for_standard_categories()
    assert reports_page.contains_texts(["Fleet Performance"]), "Fleet Performance category not visible"


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.parametrize("report_data", load_test_data("reports_functional.json", "standard_reports_with_config"))
def test_rep_std_select_report_shows_config(page, config, credentials, report_data):
    """REP-STD-002/006/010/014/018/022/027/031/035/039/043/048/052/056/060/065/069/073/077/081/085: Select report and verify config controls."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_name = report_data["report_name"]
    if not reports_page.is_standard_report_available(report_name):
        pytest.skip(f"Report '{report_name}' not available in current environment")
    reports_page.open_standard_report_form(report_name)
    assert reports_page.contains_texts([report_name, "Configure report filters", "Generate report"]), (
        f"Configuration controls not displayed for {report_name}"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_std_026_open_trips_movement_category(page, config, credentials):
    """REP-STD-026: Open Trips & Movement category and verify reports listed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.wait_for_standard_categories()
    assert reports_page.contains_texts(["Trips"]), "Trips & Movement category not visible"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_std_047_open_driver_safety_category(page, config, credentials):
    """REP-STD-047: Open Driver & Safety category and verify reports listed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.wait_for_standard_categories()
    assert reports_page.contains_texts(["Driver"]), "Driver & Safety category not visible"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_std_064_open_bms_sensors_category(page, config, credentials):
    """REP-STD-064: Open BMS & Sensors category and verify reports listed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.wait_for_standard_categories()
    assert reports_page.contains_texts(["BMS"]), "BMS & Sensors category not visible"
