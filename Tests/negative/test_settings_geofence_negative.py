import pytest
from playwright.sync_api import expect


@pytest.mark.negative
def test_set_128_geofence_name_alone_insufficient(geofence_alert_page):
    """SET-128: A geofence name alone (no drawn shape) is not enough to
    enable Create Geofence -- a shape must also be drawn on the map."""
    geofence_alert_page.open_create_page()
    geofence_alert_page.name_input.fill("AutoGeofenceTest")
    geofence_alert_page.page.wait_for_timeout(500)
    expect(geofence_alert_page.create_btn).to_be_disabled()
    geofence_alert_page.close_create_page()
