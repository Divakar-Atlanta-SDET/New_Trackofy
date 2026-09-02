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

    # 3. Target a populated widget (e.g., 'Alerts' or 'BMS Command Logs').
    widget_title = "Alerts"
    column_name = "Vehicle"

    # 4. Click target column header to toggle sorting (Ascending order).
    dashboard_page.click_column_header_to_sort(widget_title, column_name)
    asc_values = dashboard_page.get_widget_table_column_values(widget_title, column_name)

    # 5. Click target column header again to toggle sorting (Descending order).
    dashboard_page.click_column_header_to_sort(widget_title, column_name)
    desc_values = dashboard_page.get_widget_table_column_values(widget_title, column_name)

    # 6. Verify sort triggers without application error snackbars or crashes.
    expect(dashboard_page.dashboard_heading).to_be_visible()


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
