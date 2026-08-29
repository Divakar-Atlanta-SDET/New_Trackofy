import pytest

from Pages.reports_page import ReportsPage


@pytest.mark.functional
@pytest.mark.reports
def test_reports_tabs_switch_between_standard_custom_and_schedule_views(authenticated_page):
    reports_page = ReportsPage(authenticated_page)

    reports_page.open_standard_reports()
    tabs_state = reports_page.report_tabs_state()
    assert all(tabs_state.values()), f"Expected all report tabs to be visible, got: {tabs_state}"
    assert reports_page.standard_catalog_visible() is True, "Expected Standard reports catalog to be visible"

    reports_page.open_reports_tab("Custom")
    assert reports_page.custom_catalog_visible() is True, "Expected Custom reports catalog to be visible"

    reports_page.open_reports_tab("Schedule")
    assert reports_page.schedule_catalog_visible() is True, "Expected Schedule reports list or empty state to be visible"

    reports_page.open_reports_tab("Standard")
    assert reports_page.standard_catalog_visible() is True, "Expected Standard reports catalog to be visible after returning from Schedule"
