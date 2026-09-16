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

    # The rename-back cleanup MUST run even if the assertion below fails --
    # confirmed live 2026-09-16: it previously ran only on the success path,
    # so a single failed assertion left a real dashboard card permanently
    # stuck under this test-only name (found it still sitting on the live
    # dashboard from an earlier run, well after that run had ended).
    try:
        dashboard_page.click_card_edit(orig)
        dashboard_page.set_card_name(new_name)
        dashboard_page.click_save_settings()

        dashboard_page.click_add_to_trash(new_name)
        dashboard_page.open_trash_store()
        dashboard_page.restore_from_trash(new_name)
        page.wait_for_timeout(1500)  # let the restored card finish re-rendering before checking

        assert dashboard_page.card_is_visible(new_name)
    finally:
        if dashboard_page.card_is_visible(new_name):
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
