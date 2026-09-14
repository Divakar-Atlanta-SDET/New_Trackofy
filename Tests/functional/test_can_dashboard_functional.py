import pytest


@pytest.mark.functional
@pytest.mark.can
def test_can_dash_func_001_online_plus_offline_equals_total_assets(can_dashboard_page):
    values = can_dashboard_page.all_kpi_values()
    total = int(float(values["Total Assets"]))
    online = int(float(values["Online / Reporting"]))
    offline = int(float(values["Offline / Stale"]))
    assert online + offline == total, (
        f"Online ({online}) + Offline ({offline}) != Total Assets ({total})"
    )


@pytest.mark.functional
@pytest.mark.can
def test_can_dash_func_002_total_assets_matches_unit_list_and_live_map(can_dashboard_page):
    """Fixed 2026-09-14: dropped the Live Fleet Map unit-count comparison
    -- confirmed live the map widget is a visual-only canvas/tile map
    with no extractable text count anywhere near it; "directions_car"
    (which live_fleet_map_unit_count() searched for) is actually the
    separate "Total Assets" KPI card's own icon, not a map-specific
    counter. There is no real UI element this comparison could ever
    validate against. The Total-Assets-vs-Unit-List comparison below is
    unaffected and still real."""
    values = can_dashboard_page.all_kpi_values()
    total_assets = int(float(values["Total Assets"]))

    can_dashboard_page.open_units_from_dashboard()
    total_units = can_dashboard_page.pagination_total()
    assert total_units == total_assets, (
        f"Unit List total ({total_units}) disagrees with dashboard Total Assets ({total_assets})"
    )


@pytest.mark.functional
@pytest.mark.can
def test_can_dash_func_003_active_alerts_kpi_matches_alert_log_total(can_dashboard_page):
    values = can_dashboard_page.all_kpi_values()
    dashboard_active_alerts = int(float(values["Active Alerts"]))

    can_dashboard_page.open_view_all_alerts()
    from Pages.can_alerts_page import CanAlertsPage

    alerts_page = CanAlertsPage(can_dashboard_page.page)
    alert_log_total = alerts_page.total_alert_count()

    assert alert_log_total == dashboard_active_alerts, (
        f"Dashboard Active Alerts KPI ({dashboard_active_alerts}) disagrees with "
        f"Alert Log total ({alert_log_total})"
    )
