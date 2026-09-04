import pytest
from playwright.sync_api import expect
from Pages.alert_config_page import ALERT_SPECS

ALERT_TYPES_STANDARD = list(ALERT_SPECS.keys())


@pytest.mark.negative
@pytest.mark.parametrize("alert_type", ALERT_TYPES_STANDARD)
def test_reject_incomplete_alert_configuration(alert_page, alert_type):
    """SET-092/096/100/104/108/112/116/120/124/132: leaving mandatory data
    blank (no vehicle selected) keeps the submit action disabled."""
    page = alert_page(alert_type)
    page.open_add_form()
    expect(page.submit_btn).to_be_disabled()
    page.close_dialog()


@pytest.mark.negative
def test_poi_alert_create_rejected_server_side(alert_page):
    """SET-124 (and standing in for SET-123's "create valid" case): a fully
    filled-out POI Alert form is broken, not just flaky -- the Angular form
    reports valid (ng-valid throughout, submit enabled) after selecting a
    unit, a POI, and a notification channel, but the server rejects the
    request with "Missing required fields" and the dialog stays open. See
    Bug_Report.md #10. This documents the real (broken) behavior rather than
    asserting a successful creation the UI cannot currently perform.
    """
    page = alert_page("POI Alert")
    page.open_add_form()
    page.select_vehicles(1)
    page.set_extra_combos()
    page.set_notify()
    expect(page.submit_btn).to_be_enabled()
    page.submit_btn.click()
    page.page.wait_for_timeout(1500)
    expect(page.dialog).to_be_visible()
    expect(page.page.locator("app-toast")).to_contain_text("Missing required fields")
    page.close_dialog()


@pytest.mark.negative
@pytest.mark.parametrize("alert_type", ["BMS Alert", "Vehicle Odometer Alert"])
def test_alert_created_but_not_listed(alert_page, alert_type):
    """SET-119/131 (standing in for the "create valid" case): creating a
    BMS/Vehicle Odometer Alert configuration succeeds -- a success toast
    appears and the dialog closes -- but the list still reads empty
    afterward, even after a full page reload. See Bug_Report.md #11. This
    documents the real (broken) behavior rather than asserting the record
    becomes visible, which the UI cannot currently show.
    """
    page = alert_page(alert_type)
    page.open_add_form()
    page.select_vehicles(1)
    page.set_time_range()
    page.set_extra_combos()
    page.fill_numeric_fields()
    page.set_notify()
    expect(page.submit_btn).to_be_enabled()
    page.submit_btn.click()
    expect(page.dialog).to_have_count(0, timeout=5000)
    page.page.wait_for_timeout(1000)
    toast_text = page.page.locator("app-toast").inner_text()
    assert "success" in toast_text.lower() or "saved" in toast_text.lower(), (
        f"expected a success toast confirming creation, got: {toast_text!r}"
    )

    page.page.reload()
    page.wait_for_loading_to_finish()
    page.page.wait_for_timeout(1500)
    expect(page.table).to_be_visible()
    assert page.empty_state_visible(), "expected the (buggy) empty list state to persist after creation"
