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

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_wst_001_open_fleet_widget_store(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_widget_store()
    dashboard_page.open_fleet_store()
    names = dashboard_page.get_store_widget_names()
    assert len(names) > 0

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_wst_002_open_bms_widget_store(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_widget_store()
    dashboard_page.open_bms_store()
    # It might be empty, just ensure it doesn't crash
    dashboard_page.get_store_widget_names()

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_wst_003_open_video_telematics_store(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_widget_store()
    dashboard_page.open_video_telematics_store()
    dashboard_page.get_store_widget_names()

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_wst_011_close_store_without_adding(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_widget_store()
    dashboard_page.close_widget_store()
    assert not dashboard_page.widget_store_heading.is_visible()
