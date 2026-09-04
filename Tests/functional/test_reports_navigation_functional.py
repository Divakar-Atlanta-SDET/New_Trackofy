import re
import pytest
from playwright.sync_api import expect
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.data_loader import load_test_data


def login_and_open_reports(page, config, credentials):
    """Helper to log in and open /reports/standard."""
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_001_open_reports_module(page, config, credentials):
    """REP-COM-001: Open Reports module - page loads with Standard, Custom and Schedule categories."""
    reports_page = login_and_open_reports(page, config, credentials)
    tabs = reports_page.report_tabs_state()
    assert tabs["Standard"], "Standard tab not visible"
    assert tabs["Custom"], "Custom tab not visible"
    assert tabs["Schedule"], "Schedule tab not visible"


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.parametrize("tab_data", load_test_data("reports_functional.json", "report_tabs"))
def test_rep_com_002_switch_between_tabs(page, config, credentials, tab_data):
    """REP-COM-002: Switch between Standard, Custom and Schedule tabs without stale
    content -- checks both the route and that the tab's own content actually
    rendered (folded in from the retired test_reports_tab_navigation.py, which
    only ever checked this same thing with no unique data/setup of its own)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_reports_tab(tab_data["tab_name"])
    assert reports_page.is_on_path(tab_data["expected_path"]), (
        f"Expected path {tab_data['expected_path']} but on {reports_page.current_path()}"
    )
    catalog_visible = {
        "Standard": reports_page.standard_catalog_visible,
        "Custom": reports_page.custom_catalog_visible,
        "Schedule": reports_page.schedule_catalog_visible,
    }[tab_data["tab_name"]]()
    assert catalog_visible, f"{tab_data['tab_name']} tab's catalog content did not render"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_003_open_standard_reports(page, config, credentials):
    """REP-COM-003: Open Standard reports - all four categories and reports are displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    assert reports_page.standard_catalog_visible(), "Standard catalog not visible"
    reports_page.wait_for_standard_categories()
    assert reports_page.contains_any_text(["Fleet Performance", "Trips & Movement", "Driver & Safety", "BMS & Sensors"])


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_004_open_report_type_selector(page, config, credentials):
    """REP-COM-004: Open report type selector - available reports are displayed and selectable."""
    reports_page = login_and_open_reports(page, config, credentials)
    catalog_names = reports_page.standard_catalog_names()
    assert len(catalog_names) > 0, "No standard reports found in catalog"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_005_select_standard_report(page, config, credentials):
    """REP-COM-005: Select a standard report - configuration controls are displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    assert reports_page.contains_texts(["Fleet Summary", "Configure report filters", "Generate report"])


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_010_reset_filters(page, config, credentials):
    """REP-COM-010: Modify filters and reset - all resettable filters return to defaults."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    assert reports_page.is_submit_enabled(), "Generate button should be enabled after selecting vehicle"
    reports_page.reset_form()
    assert not reports_page.is_submit_enabled(), "Generate button should be disabled after reset"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_015_open_vehicle_selector(page, config, credentials):
    """REP-COM-015: Open vehicle selector - available vehicles are displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    vehicle_options = reports_page._option_names_for_combobox("Select Vehicles")
    assert len(vehicle_options) > 0, "No vehicles displayed in vehicle selector"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_com_018_export_options_visible(page, config, credentials):
    """REP-COM-018: Open export options for generated report - supported formats displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    visible_exports = reports_page.export_buttons_visible()
    assert len(visible_exports) > 0, "No export buttons visible on generated report"
