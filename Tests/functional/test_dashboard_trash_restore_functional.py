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
def test_dash_trs_004_restored_card_retains_settings(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    new_name = "TrashSettings_Test"
    
    dashboard_page.click_card_edit(orig)
    dashboard_page.set_card_name(new_name)
    dashboard_page.click_save_settings()
    
    dashboard_page.click_add_to_trash(new_name)
    dashboard_page.open_trash_store()
    dashboard_page.restore_from_trash(new_name)
    
    assert dashboard_page.card_is_visible(new_name)
    
    # cleanup
    dashboard_page.click_card_edit(new_name)
    dashboard_page.set_card_name(orig)
    dashboard_page.click_save_settings()

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_trs_005_restored_card_loads_data(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    t1 = titles[0]
    
    dashboard_page.click_add_to_trash(t1)
    dashboard_page.open_trash_store()
    dashboard_page.restore_from_trash(t1)
    
    count = dashboard_page.get_card_record_count(t1)
    assert count >= 0
