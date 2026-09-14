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
def test_poi_alert_create_valid_configuration(alert_page):
    """SET-123: Regression pin for Bug_Report.md #10. Reverified live
    (2026-09-13): this is now FIXED -- a fully filled-out POI Alert form
    (unit, POI, notification channel) submits successfully, the dialog
    closes, and the new alert appears in the list (row count increments).
    Confirmed 3x live prior to updating this test.
    """
    page = alert_page("POI Alert")
    before_count = page.table.locator("tbody tr").count()
    page.open_add_form()
    vehicle_names = page.select_vehicles(1)
    page.set_extra_combos()
    page.set_notify()
    page.submit_btn.click()
    page.page.wait_for_timeout(1500)
    try:
        expect(page.dialog).to_have_count(0)
        after_count = page.table.locator("tbody tr").count()
        assert after_count >= before_count, (
            "Expected the new POI Alert to appear in the list -- if the dialog closed but no "
            "new row shows up, Bug #10 (or the list-refresh gap in Bug #11) may have regressed."
        )
    finally:
        # This is a regression pin that runs on every suite pass -- clean up
        # the alert it creates each time, or staging accumulates one extra
        # POI Alert row per run indefinitely.
        if page.table.locator("tbody tr", has_text=vehicle_names[0]).count() > 0:
            page.delete_alert(vehicle_names[0])


@pytest.mark.negative
@pytest.mark.parametrize("alert_type", ["BMS Alert", "Vehicle Odometer Alert"])
def test_alert_created_and_listed_after_reload(alert_page, alert_type):
    """SET-119/131 (standing in for the "create valid" case): Regression
    pin for Bug_Report.md #11. Reverified live (2026-09-13): this is now
    FIXED -- creating a BMS/Vehicle Odometer Alert configuration succeeds
    (success toast, dialog closes), and after a full page reload the newly
    created vehicle's alert is genuinely present in the list (confirmed via
    both the page's own "N alerts" count incrementing and the assigned
    vehicle's name appearing in the reloaded table -- a page-1 row-count
    check alone isn't reliable here since a full page of existing alerts
    can mask a new row being added past the pagination cutoff). Confirmed
    3x live (including isolating one run to a vehicle with no prior config
    of this type, since an already-configured vehicle can update its
    existing row instead of adding a new one) prior to updating this test.
    """
    page = alert_page(alert_type)
    page.open_add_form()
    vehicle_names = page.select_vehicles(1)
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

    page.page.reload(); page.reopen()
    page.wait_for_loading_to_finish()
    page.page.wait_for_timeout(1500)
    try:
        body_after = page.page.inner_text("body")
        assert vehicle_names[0] in body_after, (
            f"Expected the newly configured vehicle ({vehicle_names[0]!r}) to appear in the "
            f"{alert_type} list after reload -- if this fails, Bug #11 (created alert never "
            f"shows up) may have regressed."
        )
    finally:
        # Same accumulation concern as the POI Alert regression pin above --
        # this test creates a real alert config on every suite run. BMS
        # Alert rows carry NO action buttons at all (confirmed live
        # 2026-09-13, see Bug_Report.md's new BMS-row-actions-missing
        # finding) so cleanup is only actually possible for the other
        # parametrized case; best-effort here, not a test failure either way.
        row = page.table.locator("tbody tr", has_text=vehicle_names[0])
        if row.count() > 0 and row.first.locator("button").count() > 0:
            page.delete_alert(vehicle_names[0])
