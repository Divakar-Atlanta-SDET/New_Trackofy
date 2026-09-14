import pytest

from Pages.reports_page import ReportsPage
from data.reports import STANDARD_REPORTS, STANDARD_REPORT_NAMES


@pytest.mark.functional
@pytest.mark.reports
def test_standard_reports_catalog_and_search(authenticated_page):
    reports_page = ReportsPage(authenticated_page)
    reports_page.open_standard_reports()
    actual_report_names = set(reports_page.standard_catalog_names())
    expected_report_names = set(STANDARD_REPORT_NAMES)
    assert actual_report_names == expected_report_names, (
        f"Expected standard catalog reports to match configured contracts. "
        f"Missing: {sorted(expected_report_names - actual_report_names)}; "
        f"Unexpected: {sorted(actual_report_names - expected_report_names)}"
    )
    assert reports_page.standard_catalog_visible() is True, "Expected Standard reports catalog to be visible"

    # Regression pin for NEW-4 (retest_bug_report.md). Confirmed live 3x
    # (2026-09-12): typing ANY query into the catalog search box -- even an
    # exact, currently-visible report name like "Distance Chart", or just
    # "Distance" -- empties the entire catalog. Zero results, and no "no
    # reports found" message either, even though the report genuinely exists
    # and is visible the moment the search box is cleared again.
    reports_page.report_search_box.fill("Distance Chart")
    assert reports_page.report_search_value() == "Distance Chart"
    assert not reports_page.contains_texts(["Distance Chart"]), (
        "Expected the known NEW-4 search bug (catalog empties on any query) -- "
        "if 'Distance Chart' is still shown, NEW-4 may be fixed."
    )


@pytest.mark.functional
@pytest.mark.reports
@pytest.mark.parametrize("report", STANDARD_REPORTS, ids=[report["name"] for report in STANDARD_REPORTS])
def test_each_standard_report_opens_expected_filter_form(authenticated_page, report):
    reports_page = ReportsPage(authenticated_page)
    reports_page.open_standard_reports()

    if not reports_page.is_standard_report_available(report["name"]):
        pytest.skip(f"{report['name']} is visible in the catalog but disabled/unavailable in the current UI")

    reports_page.open_standard_report_form(report["name"])
    assert reports_page.standard_report_form_has_fields(report["name"], report["fields"]), (
        f"Expected {report['name']} form to contain configured fields: {report['fields']}"
    )
    reports_page.click_back()
    reports_page.wait_for_reports_page()
