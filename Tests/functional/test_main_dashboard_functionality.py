import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.main_dashboard_page import MainDashboardPage


def login_and_wait_for_home(login_page, page, config, credentials):
    """Helper to log in and wait for home page authentication redirect."""
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)


@pytest.mark.functional
def test_main_dashboard_loads_successfully_and_displays_kpis(page, config, credentials):
    """Verify that logging in and navigating to the Main Trackofy Dashboard loads summary KPI metrics."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Open login page and authenticate with test credentials.
    login_and_wait_for_home(login_page, page, config, credentials)

    # 2. Navigate to the Graphical Dashboard view.
    dashboard_page.open_graphical_dashboard()

    # 3. Assert URL path and heading visibility.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))
    expect(dashboard_page.dashboard_heading).to_be_visible()

    # 4. Verify the top KPI summary strip is rendered on screen.
    # Individual tiles (Running/Stopped/No Data/Expired/BMS Enabled/...) render
    # conditionally based on live fleet counts, so only Total Fleet -- which is
    # always present -- and the KPI Settings control are safe to assert on here.
    expect(dashboard_page.total_fleet_metric).to_be_visible()
    expect(page.get_by_role("button", name=re.compile(r"KPI Settings", re.I))).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_view_switcher_graphical_and_tabular(page, config, credentials):
    """Verify toggling between Graphical and Tabular view modes on the Main Dashboard."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in to Trackofy.
    login_and_wait_for_home(login_page, page, config, credentials)

    # 2. Open Graphical dashboard.
    dashboard_page.open_graphical_dashboard()
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))

    # 3. Switch to Tabular / Live view.
    dashboard_page.switch_to_tabular_view()
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/(tabular|live)/?$"))

    # 4. Switch back to Graphical view.
    dashboard_page.switch_to_graphical_view()
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))
    expect(dashboard_page.dashboard_heading).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_chart_and_table_column_data_sorting(page, config, credentials):
    """Verify sorting widget table/chart data in Ascending and Descending order by clicking column headers."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in to Trackofy.
    login_and_wait_for_home(login_page, page, config, credentials)

    # 2. Navigate to Graphical dashboard.
    dashboard_page.open_graphical_dashboard()

    # 3. Column-header sorting only works inside the "View details" modal
    # (real Angular Material mat-sort-header columns) -- confirmed live
    # 2026-09-11 that the small inline table shown directly on a dashboard
    # card does NOT support header-click sorting at all. An earlier version
    # of this test (and this session's first attempt at fixing it) targeted
    # that inline table unscoped and wrongly concluded sorting was broken;
    # see retest_bug_report.md, "NEW-3 retracted", for the full story.
    widget_title = "Vehicle in Transit"
    column_name = "Vehicle"
    if not dashboard_page.card_is_visible(widget_title):
        pytest.skip(f"'{widget_title}' card not present on this dashboard")

    dashboard_page.click_card_view_details(widget_title)

    # 4. Click target column header to toggle sorting (Ascending order).
    dashboard_page.click_column_header_to_sort(widget_title, column_name)
    asc_values = dashboard_page.get_widget_table_column_values(widget_title, column_name)

    # 5. Click target column header again to toggle sorting (Descending order).
    dashboard_page.click_column_header_to_sort(widget_title, column_name)
    desc_values = dashboard_page.get_widget_table_column_values(widget_title, column_name)

    # 6. Verify the actual displayed order is genuinely ascending, then
    # genuinely descending -- not just "no crash". Case-insensitive
    # comparison: confirmed live the app's own sort is case-insensitive
    # (e.g. descending puts 'ptc400-demo' between 'TS09PA6001-Telangana'
    # and 'MP0987' -- only consistent if 'p' sorts against 'T'/'M' with
    # case ignored, not plain ASCII where every lowercase letter outranks
    # every uppercase one).
    assert len(asc_values) >= 2, "Not enough rows to verify sort order"
    assert asc_values == sorted(asc_values, key=str.lower), (
        f"Expected ascending order after 1st header click, got {asc_values!r}"
    )
    assert desc_values == sorted(desc_values, key=str.lower, reverse=True), (
        f"Expected descending order after 2nd header click, got {desc_values!r}"
    )

    # 7. Verify the dialog itself is still intact after both sort clicks
    # (no crash/error state) -- dashboard_heading is deliberately not
    # checked here since the open dialog legitimately covers it.
    expect(page.get_by_role("heading", name=widget_title, exact=True)).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_refresh_control(page, config, credentials):
    """Verify that clicking the Refresh dashboard button updates dashboard data cleanly."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in to Trackofy.
    login_and_wait_for_home(login_page, page, config, credentials)

    # 2. Open Graphical dashboard.
    dashboard_page.open_graphical_dashboard()
    expect(dashboard_page.dashboard_heading).to_be_visible()

    # 3. Click Refresh dashboard button.
    dashboard_page.refresh_dashboard()

    # 4. Assert dashboard content remains loaded and visible.
    expect(dashboard_page.dashboard_heading).to_be_visible()
    expect(dashboard_page.total_fleet_metric).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_accessible_via_direct_url(page, config, credentials):
    """Regression test for retest_bug_report.md NEW-1 (2026-09-11): the
    Dashboard must be reachable by navigating straight to its URL, not only
    via an in-app nav-link click. Deliberately uses page.goto() directly
    (not dashboard_page.open_graphical_dashboard(), which works around this
    exact bug by clicking the nav link instead) -- this test exists
    specifically to catch a regression on direct URL access itself.

    Expected to FAIL until the underlying app bug is fixed: as of this
    writing, a direct goto("/dashboard/graphical") silently redirects to
    /home instead of loading the Dashboard.
    """
    login_page = LoginPage(page, config)

    # 1. Log in to Trackofy.
    login_and_wait_for_home(login_page, page, config, credentials)

    # 2. Navigate directly to the Dashboard URL -- not via the nav link.
    page.goto(f"{config['base_url']}/dashboard/graphical")
    page.wait_for_timeout(3000)

    # 3. The app should load the Dashboard, not silently redirect elsewhere.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))
    expect(MainDashboardPage(page).dashboard_heading).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_survives_page_refresh(page, config, credentials):
    """Regression test for retest_bug_report.md NEW-1 (2026-09-11): once on
    the Dashboard, a plain browser refresh must keep the user there, not
    silently bounce them back to /home.

    Expected to FAIL until the underlying app bug is fixed.
    """
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in and reach the Dashboard via the normal in-app nav link.
    login_and_wait_for_home(login_page, page, config, credentials)
    dashboard_page.open_graphical_dashboard()
    expect(dashboard_page.dashboard_heading).to_be_visible()

    # 2. Refresh the page in place.
    page.reload(wait_until="load")
    page.wait_for_timeout(3000)

    # 3. The app should still be showing the Dashboard, not /home.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))
    expect(dashboard_page.dashboard_heading).to_be_visible()
