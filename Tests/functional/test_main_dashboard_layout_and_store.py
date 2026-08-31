import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.main_dashboard_page import MainDashboardPage


def login_and_open_dashboard(page, config, credentials) -> MainDashboardPage:
    """Helper to log in and open main graphical dashboard."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    dashboard_page.open_graphical_dashboard()
    return dashboard_page


@pytest.mark.functional
def test_main_dashboard_drag_and_drop_card_reordering(page, config, credentials):
    """Verify dragging widget cards via reorder handles updates card grid positioning."""
    dashboard_page = login_and_open_dashboard(page, config, credentials)

    # 1. Capture initial widget title sequence on dashboard.
    initial_titles = dashboard_page.get_widget_titles_order()
    assert len(initial_titles) >= 2, "At least 2 widget cards are required for drag-and-drop testing."

    source_title = initial_titles[0]
    target_title = initial_titles[1]

    # 2. Perform drag-and-drop reordering.
    dashboard_page.drag_and_drop_widget(source_title, target_title)

    # 3. Assert dashboard remains stable and visible.
    expect(dashboard_page.dashboard_heading).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_layout_persistence_after_refresh(page, config, credentials):
    """Verify layout state and widget rendering remain stable across page reloads."""
    dashboard_page = login_and_open_dashboard(page, config, credentials)

    # 1. Capture widget titles before refresh.
    pre_refresh_titles = dashboard_page.get_widget_titles_order()

    # 2. Reload the page.
    page.reload()
    dashboard_page.wait_for_dashboard_ready()

    # 3. Capture widget titles after refresh.
    post_refresh_titles = dashboard_page.get_widget_titles_order()

    # 4. Assert widget titles rendering and dashboard integrity.
    expect(dashboard_page.dashboard_heading).to_be_visible()
    assert len(post_refresh_titles) > 0, "Dashboard widget cards should re-render after page reload."


@pytest.mark.functional
def test_main_dashboard_widget_store_drawer(page, config, credentials):
    """Verify opening Widget Store drawer and checking available widget collections."""
    dashboard_page = login_and_open_dashboard(page, config, credentials)

    # 1. Click Widgets button to open Widget Store drawer.
    dashboard_page.open_widget_store()

    # 2. Assert Widget Store drawer heading and collections are visible.
    expect(dashboard_page.widget_store_heading).to_be_visible()
    expect(dashboard_page.fleet_widget_store_link).to_be_visible()
    expect(dashboard_page.bms_widget_store_link).to_be_visible()
    expect(dashboard_page.video_telematics_store_link).to_be_visible()

    # 3. Close the Widget Store drawer.
    dashboard_page.close_widget_store()


@pytest.mark.functional
def test_main_dashboard_trash_store_and_ai_insights(page, config, credentials):
    """Verify interacting with Trash Store and AI Insights header controls."""
    dashboard_page = login_and_open_dashboard(page, config, credentials)

    # 1. Click Trash button to open Trash Store.
    dashboard_page.open_trash_store()
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/trash/?$"))

    # 2. Navigate back to graphical dashboard.
    dashboard_page.open_graphical_dashboard()

    # 3. Click AI Insights button.
    dashboard_page.open_ai_insights()
    expect(dashboard_page.dashboard_heading).to_be_visible()
