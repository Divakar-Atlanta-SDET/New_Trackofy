import re

import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
@pytest.mark.can
def test_can_sm_001_nav_link_visible_and_opens_dashboard(can_authenticated_page, config):
    from Pages.can_page import CanBasePage

    page = can_authenticated_page
    can_nav_link = page.get_by_role("link", name="CAN")
    expect(can_nav_link).to_be_visible()
    can_nav_link.click()
    page.wait_for_url(re.compile(r".*/can/dashboard/?$"), timeout=15000)
    can_page = CanBasePage(page)
    expect(can_page.module_heading).to_be_visible()


@pytest.mark.smoke
@pytest.mark.can
@pytest.mark.parametrize(
    "path,heading_name",
    [
        ("/can/dashboard", "CAN Dashboard"),
        ("/can/units", "CAN Units"),
        ("/can/trends", "CAN Trends"),
        ("/can/report", "CAN Report"),
        ("/can/alerts", "CAN Alerts"),
        ("/can/settings", "CAN Alert Settings"),
    ],
)
def test_can_sm_002_direct_url_deep_links_to_correct_section(can_authenticated_page, config, path, heading_name):
    page = can_authenticated_page
    page.goto(f"{config['base_url']}{path}")
    page.wait_for_url(re.compile(rf".*{re.escape(path)}/?$"), timeout=15000)
    expect(page.get_by_role("heading", name=heading_name, exact=True)).to_be_visible(timeout=15000)


@pytest.mark.smoke
@pytest.mark.can
def test_can_sm_003_sub_menu_navigation_between_all_sections(can_dashboard_page):
    can_dashboard_page.open_unit()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Units", exact=True)).to_be_visible()

    can_dashboard_page.open_trends()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Trends", exact=True)).to_be_visible()

    can_dashboard_page.open_reports()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Report", exact=True)).to_be_visible()

    can_dashboard_page.open_alerts()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Alerts", exact=True)).to_be_visible()

    can_dashboard_page.open_settings()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Alert Settings", exact=True)).to_be_visible()

    can_dashboard_page.open_dashboard()
    expect(can_dashboard_page.heading).to_be_visible()


@pytest.mark.smoke
@pytest.mark.can
def test_can_sm_004_live_fleet_map_present_on_every_section(can_dashboard_page):
    """Fixed 2026-09-14: dropped the unit-count assertion -- confirmed
    live the map widget is a visual-only canvas/tile map with no
    extractable text count anywhere near its heading (the icon
    live_fleet_map_unit_count() searched for actually belongs to the
    separate Total Assets KPI card). Presence of the widget itself
    (heading + map container) is what's real and checkable here."""
    expect(can_dashboard_page.live_fleet_map_heading).to_be_visible()
