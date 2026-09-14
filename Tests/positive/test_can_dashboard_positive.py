import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_001_kpi_cards_render_with_numeric_values(can_dashboard_page):
    values = can_dashboard_page.all_kpi_values()
    for label, value in values.items():
        assert value != "", f"KPI card {label!r} has no numeric value"
        assert value.replace(".", "", 1).isdigit(), f"KPI card {label!r} value {value!r} is not numeric"


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_002_charts_render(can_dashboard_page):
    expect(can_dashboard_page.protocol_chart_heading).to_be_visible()
    expect(can_dashboard_page.online_offline_chart_heading).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_003_recent_alerts_panel_and_view_all(can_dashboard_page):
    expect(can_dashboard_page.recent_alerts_heading).to_be_visible()
    can_dashboard_page.open_view_all_alerts()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Alerts", exact=True)).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_004_open_units_link_navigates_to_unit_list(can_dashboard_page):
    can_dashboard_page.open_units_from_dashboard()
    expect(can_dashboard_page.page.get_by_role("heading", name="CAN Units", exact=True)).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_005_can_unit_table_renders(can_dashboard_page):
    expect(can_dashboard_page.can_unit_table_heading).to_be_visible()
    assert can_dashboard_page.unit_table_row_count() > 0


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_006_ai_summary_panel_opens(can_dashboard_page):
    can_dashboard_page.open_ai_summary()
    panel = can_dashboard_page.ai_summary_panel()
    expect(panel).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_dash_pos_007_refresh_reloads_without_full_page_navigation(can_dashboard_page, network_monitor):
    network_monitor.start()
    url_before = can_dashboard_page.page.url
    can_dashboard_page.click_refresh()
    can_dashboard_page.page.wait_for_timeout(1500)
    assert can_dashboard_page.page.url == url_before
    network_monitor.stop()
