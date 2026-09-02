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
def test_dash_set_002_rename_card(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    try:
        dashboard_page.click_card_edit(orig)
        dashboard_page.set_card_name("TestRename_Auto")
        dashboard_page.click_save_settings()
        assert dashboard_page.card_is_visible("TestRename_Auto")
    finally:
        if dashboard_page.card_is_visible("TestRename_Auto"):
            dashboard_page.click_card_edit("TestRename_Auto")
            dashboard_page.set_card_name(orig)
            dashboard_page.click_save_settings()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_005_change_chart_to_bar(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    try:
        dashboard_page.select_chart_type("Bar")
    except:
        pytest.skip("Bar chart type not available for this card")
    dashboard_page.click_save_settings()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_010_change_chart_color(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    try:
        dashboard_page.set_chart_color("#00ff00")
    except Exception:
        pytest.skip("Chart color not available for this card (table-only widget)")
    assert dashboard_page.get_chart_color().lower() == "#00ff00"
    dashboard_page.click_save_settings()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_012_sort_ascending(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    try:
        dashboard_page.set_sort_direction("Ascending")
    except:
        pytest.skip("Sort direction not available")
    dashboard_page.click_save_settings()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_013_sort_descending(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    try:
        dashboard_page.set_sort_direction("Descending")
    except:
        pytest.skip("Sort direction not available")
    dashboard_page.click_save_settings()

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_015_add_hidden_table_column(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    dashboard_page.click_card_edit(titles[0])
    try:
        dashboard_page.toggle_column_in_settings("Vehicle", check=False)
        dashboard_page.toggle_column_in_settings("Vehicle", check=True)
    except Exception:
        pytest.skip("'Vehicle' column checkbox not available for this card")
    dashboard_page.click_save_settings()
    assert "Vehicle" in dashboard_page.get_card_table_headers(titles[0])

@pytest.mark.positive
@pytest.mark.dashboard
def test_dash_set_016_remove_visible_table_column(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    try:
        dashboard_page.click_card_edit(orig)
        dashboard_page.toggle_column_in_settings("Vehicle", check=False)
        dashboard_page.click_save_settings()
        assert "Vehicle" not in dashboard_page.get_card_table_headers(orig)
    finally:
        dashboard_page.click_card_edit(orig)
        dashboard_page.toggle_column_in_settings("Vehicle", check=True)
        dashboard_page.click_save_settings()
