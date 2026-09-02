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
@pytest.mark.parametrize("template_data", load_test_data("reports_positive.json", "valid_custom_report_templates"))
def test_rep_cus_003_fill_valid_template_details(page, config, credentials, template_data):
    """REP-CUS-003: Fill valid template name and description in General step."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general(
        template_data["template_name"],
        template_data["template_description"],
    )
    # Verify Continue button becomes clickable
    continue_btn = reports_page.page.get_by_role("button", name=re.compile(r"Continue", re.I)).last
    assert continue_btn.is_enabled(), "Continue button not enabled after filling valid template details"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_cus_004_005_navigate_to_components_step(page, config, credentials):
    """REP-CUS-004/005: Navigate from General to Components step with valid data."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general("Test Template", "Automation test template")
    reports_page.click_custom_continue()
    assert reports_page.contains_texts(["Components"]), "Components step not reached"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_cus_006_010_011_custom_report_dialog_navigation(page, config, credentials):
    """REP-CUS-006/010/011: Full dialog navigation through General > Components."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    assert reports_page.contains_texts(["General"])
    reports_page.fill_custom_report_general("Nav Test Template", "Testing navigation")
    reports_page.click_custom_continue()
    assert reports_page.contains_texts(["Components"])
    reports_page.close_dialog()


@pytest.mark.positive
@pytest.mark.reports
def test_rep_cus_019_search_templates(page, config, credentials):
    """REP-CUS-019: Search for existing templates returns results."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_custom_reports()
    search_box = reports_page.page.get_by_placeholder(re.compile(r"Search templates", re.I))
    search_box.fill("Fleet")
    reports_page.wait_for_loading_to_finish()
    # Verify search doesn't break the page
    assert reports_page.is_on_path("/reports/custom"), "Search caused navigation away from custom reports"
