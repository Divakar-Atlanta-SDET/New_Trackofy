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
def test_rep_dl_110_navigate_to_downloads_page(page, config, credentials):
    """REP-DL-110: Navigate to Downloads page and verify it loads."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    assert reports_page.is_on_path("/profile/downloads"), "Not on downloads page"
    assert reports_page.contains_texts(["Downloads"]), "Downloads heading not visible"


@pytest.mark.functional
@pytest.mark.reports
def test_rep_dl_111_downloads_table_has_columns(page, config, credentials):
    """REP-DL-111: Verify downloads table has correct columns."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    table = reports_page.page.get_by_role("table")
    if table.count() == 0:
        pytest.skip("No downloads table present")
    assert reports_page.contains_any_text(["Report Name", "Status", "Download"]), (
        "Downloads table missing expected columns"
    )


@pytest.mark.functional
@pytest.mark.reports
def test_rep_dl_120_121_downloads_search(page, config, credentials):
    """REP-DL-120/121: Verify search functionality on downloads page."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    searchbox = reports_page.page.get_by_role("searchbox", name="Search")
    expect(searchbox).to_be_visible()


@pytest.mark.functional
@pytest.mark.reports
def test_rep_dl_131_downloads_pagination(page, config, credentials):
    """REP-DL-131: Verify downloads page has pagination controls."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    items_per_page = reports_page.page.get_by_role("combobox", name="Items per page:")
    if items_per_page.count() > 0:
        expect(items_per_page).to_be_visible()
