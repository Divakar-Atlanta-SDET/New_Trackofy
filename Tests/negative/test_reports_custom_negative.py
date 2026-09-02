import re
import pytest

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


@pytest.mark.negative
@pytest.mark.reports
def test_rep_cus_009_continue_without_required_fields(page, config, credentials):
    """REP-CUS-009: Attempt to Continue without filling required fields."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    # Leave name and description empty, try to continue
    continue_btn = reports_page.page.get_by_role("button", name=re.compile(r"Continue", re.I)).last
    # Button should be disabled or clicking should show validation
    if continue_btn.is_enabled():
        continue_btn.click()
        reports_page.wait_for_loading_to_finish()
        validation = reports_page.validation_messages()
        assert len(validation) > 0, "Expected validation errors for empty template fields"
    else:
        assert not continue_btn.is_enabled(), "Continue should be disabled without required fields"


@pytest.mark.negative
@pytest.mark.reports
def test_rep_cus_016_empty_template_name(page, config, credentials):
    """REP-CUS-016: Create custom report with empty template name."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_new_custom_report_modal()
    reports_page.fill_custom_report_general("", "Some description")
    continue_btn = reports_page.page.get_by_role("button", name=re.compile(r"Continue", re.I)).last
    # Should either be disabled or show validation
    if continue_btn.is_enabled():
        continue_btn.click()
        reports_page.wait_for_loading_to_finish()
        validation = reports_page.validation_messages()
        assert len(validation) > 0, "Expected validation for empty template name"
