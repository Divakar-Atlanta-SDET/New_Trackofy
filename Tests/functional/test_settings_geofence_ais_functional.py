import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_set_126_geofence_list_loads(geofence_alert_page):
    """SET-126: Verify Geofence Alert list loads without error."""
    expect(geofence_alert_page.table).to_be_visible()


@pytest.mark.functional
def test_set_126b_open_create_geofence_page(geofence_alert_page):
    """SET-126: "Add Geofence" opens the dedicated create-geofence page with
    its name field and drawing tools -- drawing an actual shape on the map
    is out of scope for reliable UI automation (same limitation class as
    Tracking's GPS/map tests)."""
    geofence_alert_page.open_create_page()
    expect(geofence_alert_page.name_input).to_be_visible()
    expect(geofence_alert_page.create_btn).to_be_disabled()
    geofence_alert_page.close_create_page()


@pytest.mark.functional
def test_set_134_ais_alert_list_loads(ais_alert_page):
    """SET-134: Verify AIS Alert's per-vehicle list loads without error."""
    expect(ais_alert_page.table).to_be_visible()


@pytest.mark.functional
def test_set_134b_open_ais_edit_dialog(ais_alert_page):
    """SET-134: Opening a vehicle's row shows its AIS sub-alert toggle grid."""
    ais_alert_page.open_edit_for_row(0)
    expect(ais_alert_page.toggles().first).to_be_visible()
    expect(ais_alert_page.update_btn).to_be_disabled()
    ais_alert_page.close_dialog()
