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
def test_dash_set_001_open_card_settings(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    expect(page.get_by_role("button", name=re.compile(r"Update Widget", re.I)).first).to_be_visible()
    expect(page.get_by_role("button", name=re.compile(r"^Cancel$", re.I)).first).to_be_visible()

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_set_022_save_settings_persist_after_refresh(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    try:
        dashboard_page.click_card_edit(orig)
        dashboard_page.set_card_name("TestPersist")
        dashboard_page.click_save_settings()
        page.reload()
        dashboard_page.wait_for_dashboard_ready()
        assert dashboard_page.card_is_visible("TestPersist")
    finally:
        if dashboard_page.card_is_visible("TestPersist"):
            dashboard_page.click_card_edit("TestPersist")
            dashboard_page.set_card_name(orig)
            dashboard_page.click_save_settings()

@pytest.mark.functional
@pytest.mark.dashboard
def test_dash_set_023_cancel_discards_changes(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    dashboard_page.click_card_edit(orig)
    dashboard_page.set_card_name("RandomNameDiscard")
    dashboard_page.click_cancel_settings()
    assert dashboard_page.card_is_visible(orig)
    assert not dashboard_page.card_is_visible("RandomNameDiscard")
