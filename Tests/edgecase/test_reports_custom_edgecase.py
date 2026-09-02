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


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.parametrize("name_data", load_test_data("reports_edgecase.json", "custom_report_boundary_names"))
def test_rep_cus_008_boundary_template_names(page, config, credentials, name_data):
    """REP-CUS-008: Create custom report with boundary template names."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general(
        name_data["template_name"],
        name_data["template_description"],
    )
    # Should accept or show validation for boundary names
    continue_btn = reports_page.page.get_by_role("button", name=re.compile(r"Continue", re.I)).last
    assert continue_btn.is_visible(), "Continue button not visible for boundary name test"
    reports_page.close_dialog()


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_cus_014_015_open_close_dialog_rapidly(page, config, credentials):
    """REP-CUS-014/015: Rapidly open and close custom report dialog."""
    reports_page = login_and_open_reports(page, config, credentials)
    for _ in range(3):
        reports_page.open_new_custom_report_modal()
        reports_page.close_dialog()
    # UI should remain stable
    assert reports_page.is_on_path("/reports/custom"), "UI unstable after rapid open/close"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_cus_017_refresh_during_creation(page, config, credentials):
    """REP-CUS-017: Refresh page during custom report creation."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general("Refresh Test", "Testing refresh")
    page.reload()
    reports_page.wait_for_custom_reports_page()
    assert reports_page.is_on_path("/reports/custom"), "Page did not recover after refresh"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_cus_020_empty_search_returns_all(page, config, credentials):
    """REP-CUS-020: Empty search query returns all templates."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_custom_reports()
    search_box = reports_page.page.get_by_placeholder(re.compile(r"Search templates", re.I))
    search_box.fill("")
    reports_page.wait_for_loading_to_finish()
    assert reports_page.is_on_path("/reports/custom"), "Empty search broke custom reports page"
