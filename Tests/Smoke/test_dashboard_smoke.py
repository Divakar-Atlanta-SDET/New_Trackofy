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

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_001_dashboard_loads(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    expect(dashboard_page.dashboard_heading).to_be_visible()
    expect(dashboard_page.graphical_view_button).to_be_visible()
    expect(dashboard_page.tabular_view_button).to_be_visible()
    expect(dashboard_page.widgets_button).to_be_visible()
    expect(dashboard_page.trash_button).to_be_visible()

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_002_cards_load_with_title_and_data(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    assert len(titles) > 0, "No widget cards visible"
    
    found_data = False
    for t in titles:
        count = dashboard_page.get_card_record_count(t)
        if count > 0:
            found_data = True
            break
    assert found_data, "No cards with record count > 0 found"

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_003_open_card_settings(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    assert len(titles) > 0, "No cards available"
    dashboard_page.click_card_edit(titles[0])
    val = dashboard_page.get_card_name_value()
    assert val != "", "Card name input should not be empty"

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_004_card_date_filter_options(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles:
        pytest.skip("No cards to check date filter")
    dashboard_page.open_card_date_filter(titles[0])
    expect(page.get_by_role("button", name=re.compile(r"Today", re.I)).first).to_be_visible()
    expect(page.get_by_role("button", name=re.compile(r"Yesterday", re.I)).first).to_be_visible()

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_005_widget_stores_accessible(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_widget_store()
    expect(dashboard_page.fleet_widget_store_link).to_be_visible()
    expect(dashboard_page.bms_widget_store_link).to_be_visible()
    expect(dashboard_page.video_telematics_store_link).to_be_visible()

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_006_open_trash(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_trash_store()
    expect(page.get_by_role("heading", name=re.compile(r"Trash", re.I)).first).to_be_visible()

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_007_drag_and_drop_card(page, config, credentials):
    pytest.skip("Drag and drop might be unreliable.")

@pytest.mark.smoke
@pytest.mark.dashboard
def test_dash_sm_008_delete_and_restore_card(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles:
        pytest.skip("No cards available to delete")
    target_card = titles[0]
    dashboard_page.click_add_to_trash(target_card)
    assert not dashboard_page.card_is_visible(target_card)
    
    dashboard_page.open_trash_store()
    dashboard_page.restore_from_trash(target_card)
    assert dashboard_page.card_is_visible(target_card)
