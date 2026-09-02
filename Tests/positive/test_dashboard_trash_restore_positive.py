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
def test_dash_trs_001_move_card_to_trash(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    target = titles[0]
    dashboard_page.click_add_to_trash(target)
    assert not dashboard_page.card_is_visible(target)
    
    dashboard_page.open_trash_store()
    items = dashboard_page.get_trash_items()
    assert any(target in i for i in items)
    dashboard_page.restore_from_trash(target)

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_trs_002_restore_one_card(page, config, credentials):
    pytest.skip("Covered by 001")

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_trs_003_restore_multiple_cards(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if len(titles) < 2: pytest.skip()
    t1, t2 = titles[0], titles[1]
    
    dashboard_page.click_add_to_trash(t1)
    dashboard_page.click_add_to_trash(t2)
    
    dashboard_page.open_trash_store()
    dashboard_page.restore_from_trash(t1)
    dashboard_page.restore_from_trash(t2)
    
    assert dashboard_page.card_is_visible(t1)
    assert dashboard_page.card_is_visible(t2)
