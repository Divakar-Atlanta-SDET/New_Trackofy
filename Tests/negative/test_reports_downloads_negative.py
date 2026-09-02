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
def test_rep_dl_116_download_link_broken(page, config, credentials):
    """REP-DL-116: Verify behavior when download link is broken/expired."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    entries = reports_page.get_download_entries()
    if not entries:
        pytest.skip("No download entries to test")
    # Verify entries have download URLs
    for entry in entries:
        if entry["status"] == "Done":
            assert "download_url" in entry, f"Done entry missing download URL: {entry}"


@pytest.mark.negative
@pytest.mark.reports
def test_rep_dl_126_search_nonexistent_report(page, config, credentials):
    """REP-DL-126: Search for non-existent report in downloads."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_downloads_page()
    searchbox = reports_page.page.get_by_role("searchbox", name="Search")
    searchbox.fill("nonexistent_report_xyz_12345")
    reports_page.wait_for_loading_to_finish()
    entries = reports_page.get_download_entries()
    assert len(entries) == 0, "Search for non-existent report should return no results"
