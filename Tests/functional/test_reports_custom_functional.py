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
def test_rep_cus_001_open_custom_reports_tab(page, config, credentials):
    """REP-CUS-001: Open Custom reports tab and verify it loads correctly."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_custom_reports()
    assert reports_page.custom_catalog_visible() or reports_page.contains_texts(["New"]), (
        "Custom reports tab did not load"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_cus_002_open_new_custom_report_modal(page, config, credentials):
    """REP-CUS-002: Click New button and verify custom report creation dialog opens."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    assert reports_page.contains_texts(["Create Custom Report"]), (
        "Custom report creation dialog not displayed"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_cus_007_custom_report_dialog_has_steps(page, config, credentials):
    """REP-CUS-007: Verify custom report dialog has General, Components, Settings steps."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    assert reports_page.custom_dialog_has_steps(), (
        "Custom report dialog missing General/Components/Settings steps"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_cus_012_close_custom_report_dialog(page, config, credentials):
    """REP-CUS-012: Close the custom report dialog and verify it closes properly."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    assert reports_page.contains_texts(["Create Custom Report"])
    reports_page.close_dialog()
    assert not reports_page.contains_texts(["Create Custom Report"]), (
        "Custom report dialog did not close"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_cus_013_navigate_between_steps(page, config, credentials):
    """REP-CUS-013: Navigate between General and Components steps."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general("Test Template", "Test description")
    reports_page.click_custom_continue()
    assert reports_page.contains_texts(["Components"]), "Did not navigate to Components step"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_cus_018_search_custom_templates(page, config, credentials):
    """REP-CUS-018: Search for templates in custom reports."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_custom_reports()
    search_box = reports_page.page.get_by_placeholder(re.compile(r"Search templates", re.I))
    expect(search_box).to_be_visible()
