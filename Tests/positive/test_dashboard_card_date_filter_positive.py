import re
import pytest
from playwright.sync_api import expect
from Pages.login_page import LoginPage
from Pages.main_dashboard_page import MainDashboardPage

def login_and_open_dashboard(page, config, credentials):
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    dashboard_page.open_graphical_dashboard()
    return dashboard_page

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_df_001_select_today(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.open_card_date_filter(titles[0])
    dashboard_page.select_card_date_option("Today")
    assert "Today" in dashboard_page.get_active_card_date_label()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_df_002_select_yesterday(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.open_card_date_filter(titles[0])
    dashboard_page.select_card_date_option("Yesterday")
    assert "Yesterday" in dashboard_page.get_active_card_date_label()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_df_003_select_last_7_days(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.open_card_date_filter(titles[0])
    dashboard_page.select_card_date_option("Last 7 Days")
    assert "7" in dashboard_page.get_active_card_date_label()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_df_004_select_this_month(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.open_card_date_filter(titles[0])
    dashboard_page.select_card_date_option("This Month")
    assert "Month" in dashboard_page.get_active_card_date_label()
