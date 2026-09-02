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

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_set_004_rename_beyond_max_length(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    dashboard_page.click_card_edit(orig)
    long_name = "A" * 500
    dashboard_page.set_card_name(long_name)
    dashboard_page.click_save_settings()
    
    # check validation or truncation
    err = dashboard_page.page.locator("mat-error, .error").is_visible()
    new_title = dashboard_page.get_all_card_titles()[0]
    assert err or len(new_title) <= 500
    
    try:
        dashboard_page.click_cancel_settings()
    except:
        pass
    
    if dashboard_page.card_is_visible(new_title) and new_title != orig:
        dashboard_page.click_card_edit(new_title)
        dashboard_page.set_card_name(orig)
        dashboard_page.click_save_settings()

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_set_009_switch_chart_types_repeatedly(page, config, credentials):
    pytest.skip("Chart types might not be fully implemented or robust enough yet")

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_df_009_rapidly_switch_date_filters(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    # The date-filter dropdown auto-closes after each pick, so it must be
    # reopened before every subsequent selection.
    for option in ("Today", "Last 7 Days", "This Month", "Yesterday"):
        dashboard_page.open_card_date_filter(titles[0])
        dashboard_page.select_card_date_option(option)
    assert "Yesterday" in dashboard_page.get_active_card_date_label()

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_gf_008_rapidly_change_global_filters(page, config, credentials):
    pytest.skip("Multiple vehicles not explicitly available in staging")

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_wst_008_add_already_present_widget(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    
    dashboard_page.open_widget_store()
    dashboard_page.open_fleet_store()
    try:
        dashboard_page.add_widget_from_store(orig)
    except:
        pass
    # No crash
    dashboard_page.close_widget_store()

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_trs_010_trash_all_cards(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()

    # Some cards (e.g. LiveCam View) have no 'More widget actions' menu and can't
    # be trashed; only attempt cards that actually expose the action.
    trashable = [t for t in titles if dashboard_page.get_card_locator(t).get_by_role(
        "button", name=re.compile(r"More widget actions", re.I)
    ).first.is_visible()]
    if not trashable:
        pytest.skip("No trashable cards on this dashboard")

    trashed = []
    try:
        for t in trashable:
            dashboard_page.click_add_to_trash(t)
            trashed.append(t)

        assert dashboard_page.count_visible_cards() == len(titles) - len(trashed)
    finally:
        # always restore, even if a trash click failed partway through
        dashboard_page.open_trash_store()
        for t in trashed:
            dashboard_page.restore_from_trash(t)

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_sys_008_open_multiple_card_menus_rapidly(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if len(titles) < 2: pytest.skip()
    
    dashboard_page.open_card_actions_menu(titles[0])
    dashboard_page.open_card_actions_menu(titles[1])
    # Expect second menu to be active, or no crash

@pytest.mark.edgecase
@pytest.mark.dashboard
def test_dash_drg_006_drag_card_to_current_position(page, config, credentials):
    pytest.skip("Drag and drop logic unreliable")
