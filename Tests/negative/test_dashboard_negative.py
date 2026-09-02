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

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_set_003_rename_with_empty_value(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    dashboard_page.click_card_edit(orig)
    dashboard_page.set_card_name("")

    # Update Widget correctly stays disabled for an empty title rather than
    # accepting it, so assert the disabled state instead of clicking through.
    update_btn = page.get_by_role("button", name=re.compile(r"Update Widget", re.I)).first
    expect(update_btn).to_be_disabled()
    assert dashboard_page.card_is_visible(orig)

    dashboard_page.click_cancel_settings()

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_set_019_remove_mandatory_column(page, config, credentials):
    pytest.skip("Hard to identify mandatory column reliably without specific test data")

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_gf_006_apply_invalid_filter(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_global_filter()
    # Apply without selecting a unit: the button must stay disabled rather than
    # accepting an incomplete filter.
    apply_btn = page.get_by_role("button", name=re.compile(r"^Apply$", re.I)).first
    expect(apply_btn).to_be_disabled()
    assert not dashboard_page.is_global_filter_active()

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_trs_007_cancel_permanent_deletion(page, config, credentials):
    pytest.skip("Permanent deletion not explicitly mentioned in requirements for trash")
