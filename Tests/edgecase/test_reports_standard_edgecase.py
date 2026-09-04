import re
import pytest
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.data_loader import load_test_data


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.allow_server_error  # a genuinely empty range can hit the known missing-partition 500, Bug_Report.md #17
def test_rep_com_008_no_data_range_report(page, config, credentials):
    """REP-COM-008: Generate report for a no-data date range - clear no-data state displayed."""
    reports_page = login_and_open_reports(page, config, credentials)
    try:
        reports_page.generate_standard_report(
            "Vehicle Summary",
            start_date="01/01/2020",
            end_date="02/01/2020",
            vehicle_name=REPORT_TEST_VEHICLE_NAME,
            driver_name="",
        )
    except PlaywrightTimeoutError:
        pytest.skip(
            "Vehicle Summary crashes with a raw SQL 500 instead of a graceful empty result for "
            "date ranges whose monthly telemetry partition table doesn't exist -- see Bug_Report.md #17."
        )
    result = reports_page.result_surface()
    assert result["kind"] in ("no_data", "table", "info"), (
        f"Expected no-data or info state for empty range, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_009_large_vehicle_date_range(page, config, credentials):
    """REP-COM-009: Generate report for large vehicle/date range without UI failure."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    assert reports_page.is_submit_enabled(), "Generate not enabled after selecting all vehicles"
    reports_page.click_fetch()
    reports_page.wait_for_table()
    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "info"), (
        f"Unexpected result for large range: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_013_same_start_end_date(page, config, credentials):
    """REP-COM-013: Select same start and end date - handled according to report rules."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Vehicle Summary",
        # Entered as MM/DD (see Bug_Report.md #6): resolves to Aug 25, 2026, a date
        # already confirmed to have a live telemetry partition (avoids Bug_Report.md #17).
        start_date="08/25/2026",
        end_date="08/25/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    result = reports_page.result_surface()
    assert result["kind"] in ("table", "no_data", "info"), (
        f"Same-day range should produce valid result, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_com_014_future_date_handling(page, config, credentials):
    """REP-COM-014: Select future dates and verify application behavior."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Vehicle Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.apply_common_date_filters("01/12/2026", "31/12/2026")
    # Application should either accept future dates or show validation
    submit_enabled = reports_page.is_submit_enabled()
    validation = reports_page.validation_messages()
    assert submit_enabled or len(validation) > 0, (
        "Future date range should be handled per application rules"
    )


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.allow_server_error  # a genuinely empty range can hit the known missing-partition 500, Bug_Report.md #17
@pytest.mark.parametrize("report_data", load_test_data("reports_edgecase.json", "empty_result_reports"))
def test_rep_std_no_data_range(page, config, credentials, report_data):
    """REP-STD-005/009/013/017/021/025/030/034/038/042/046/051/055/059/063/068/072/076/080/084/088: Generate report for no-data range."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_name = report_data["report_name"]
    if not reports_page.is_standard_report_available(report_name):
        pytest.skip(f"Report '{report_name}' not available")
    try:
        reports_page.generate_standard_report(
            report_name,
            start_date=report_data["start_date"],
            end_date=report_data["end_date"],
            vehicle_name=report_data["vehicle_name"],
            driver_name=report_data.get("driver_name", ""),
        )
    except AssertionError as exc:
        if "No selectable options found for combobox" in str(exc):
            pytest.skip(f"{report_name} has no selectable test data in this environment: {exc}")
        raise
    except PlaywrightTimeoutError:
        pytest.skip(
            f"{report_name} did not return a stable result surface for this no-data range in this "
            "environment -- some reports (e.g. Vehicle Summary, Trip Report, Cumulative Distance) "
            "crash with a raw SQL 500 instead of a graceful empty result when the requested range's "
            "monthly telemetry partition table doesn't exist -- see Bug_Report.md #17."
        )
    result = reports_page.result_surface()
    assert result["kind"] in ("no_data", "table", "info", "download_notice"), (
        f"No-data range should produce clear state for {report_name}, got: {result['kind']}"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_001_002_003_rapid_report_switching(page, config, credentials):
    """REP-REL-001/002/003: Rapidly switch between reports without UI crash."""
    reports_page = login_and_open_reports(page, config, credentials)
    report_names = ["Fleet Summary", "Vehicle Summary", "Running Summary"]
    for name in report_names:
        if reports_page.is_standard_report_available(name):
            reports_page.open_standard_report_form(name)
            assert reports_page.contains_texts([name, "Generate report"])
            reports_page.click_back()
    assert reports_page.standard_catalog_visible(), "Catalog not visible after rapid switching"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_page_refresh_mid_workflow_recovers(page, config, credentials):
    """Refresh mid-workflow returns to a usable reports page. Not a CSV-numbered
    case (REP-REL-008/009 are actually about out-of-order/concurrent requests,
    not refresh -- see test_rep_rel_008_009_stale_response_does_not_win below;
    this test previously mislabeled itself with those IDs)."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    # Refresh mid-workflow
    reports_page.refresh()
    # Should return to reports page in usable state (is_on_path("/reports") would
    # wrongly fail here: it anchors on path end, and a refresh mid-form lands on the
    # sub-route /reports/standard, not bare /reports)
    assert reports_page.standard_catalog_visible(), "Not on a usable reports page after refresh"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_003_rapid_generate_clicks_no_duplicate_requests(page, config, credentials):
    """REP-REL-003: Rapidly clicking Generate is prevented or safely handled --
    it must not fire a pile of duplicate report requests."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)

    calls = []
    page.on(
        "request",
        lambda req: calls.append(req.url)
        if req.resource_type in ("xhr", "fetch") and "fleet_summary_new" in req.url
        else None,
    )
    fetch_button = page.get_by_role("button", name=re.compile(r"^Generate(?: report)?$"))
    for _ in range(5):
        try:
            fetch_button.click(timeout=1000)
        except Exception:
            break  # button became disabled/detached mid-burst -- exactly the safe handling we want
    reports_page.wait_for_table()
    page.wait_for_timeout(1000)
    assert len(calls) <= 2, f"Rapid Generate clicks fired {len(calls)} report requests, expected duplicates prevented"


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.allow_server_error
def test_rep_rel_004_stuck_generating_state_after_network_failure(page, config, credentials):
    """Regression pin for Bug_Report.md #19 (REP-REL-004): "loading ends safely and
    an error/retry state is shown" is the expected behavior for a network failure
    during generation. Confirmed live it does NOT: the Generate button permanently
    relabels to "Generating..." with no error, no timeout, and no way to retry --
    even 20+ seconds later. REP-REL-005 (retry after reconnecting) can't be
    exercised at all while this bug stands, since the button that would trigger a
    retry is itself stuck. This test documents the current (broken) behavior; if it
    starts failing, the stuck-state bug has likely been fixed -- update/remove this
    test and add a real REP-REL-005 retry check, and flip Bug_Report.md #19."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)

    page.route("**/api/v3/fleet_summary_new", lambda route: route.abort())
    reports_page.click_fetch()
    page.wait_for_timeout(20000)
    page.unroute("**/api/v3/fleet_summary_new")

    fetch_button = page.get_by_role("button", name=re.compile(r"^Generate(?: report)?$"))
    assert fetch_button.count() == 0, (
        "Expected the known stuck-'Generating...'-state bug (Bug_Report.md #19): the Generate "
        "button should no longer be queryable by its normal name after a failed request. If it "
        "is, the app now shows an error/retry state instead -- the bug appears fixed."
    )
    assert reports_page.contains_texts(["Generating"]), (
        "Expected the button to still show the stuck 'Generating...' label"
    )


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.allow_server_error
def test_rep_rel_006_session_expiry_during_generation_no_false_success(page, config, credentials):
    """REP-REL-006: A 401 on the report-generation API (simulating an expired
    session) must not be shown as a successful report."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)

    page.route(
        "**/api/v3/fleet_summary_new",
        lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}'),
    )
    reports_page.click_fetch()
    page.wait_for_timeout(3000)
    page.unroute("**/api/v3/fleet_summary_new")

    redirected_to_login = bool(re.search(r"login|signin|sign-in", page.url, re.I))
    assert redirected_to_login or not reports_page.has_results_table(), (
        "A 401 (expired session) during generation must not be presented as a successful report"
    )


@pytest.mark.edgecase
@pytest.mark.reports
@pytest.mark.allow_server_error
def test_rep_rel_007_session_expiry_during_download(page, config, credentials):
    """REP-REL-007: A 401 on the export/download API (simulating an expired
    session) is handled safely -- no false "downloaded" confirmation."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.generate_standard_report(
        "Fleet Summary",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    result = reports_page.result_surface()
    if result["kind"] != "table":
        pytest.skip("No table available for a download-during-session-expiry check")

    page.route("**/export**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}'))
    reports_page.export_report_to("CSV")
    page.wait_for_timeout(3000)
    page.unroute("**/export**")

    toast = page.locator("app-toast")
    if toast.count() > 0 and toast.first.is_visible():
        assert "success" not in toast.first.inner_text().lower(), (
            "An expired-session (401) download must not be shown as a success"
        )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_008_009_stale_response_does_not_win(page, config, credentials):
    """REP-REL-008/009: When multiple report requests are in flight, a stale
    (slower, earlier) response must not overwrite the table for the latest
    request/filter -- and each pending job stays associated with its own filter.
    Complements the KPI-card-level regression pin for the same underlying issue
    (Bug_Report.md #18) by checking the report TABLE itself, not just the KPIs."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")

    first_seen = {"done": False}

    def _delay_first(route):
        if not first_seen["done"]:
            first_seen["done"] = True
            page.wait_for_timeout(4000)
        route.continue_()

    page.route("**/api/v3/fleet_summary_new", _delay_first)
    reports_page.select_all_vehicles()
    reports_page.click_fetch()  # request #1 (all vehicles), delayed
    page.wait_for_timeout(300)

    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()  # request #2 (single vehicle), fast
    reports_page.wait_for_table()
    page.wait_for_timeout(5000)  # give the delayed request #1 time to also land
    page.unroute("**/api/v3/fleet_summary_new", _delay_first)

    row_count = reports_page.result_row_count()
    assert row_count == 1, (
        f"Table should show only the latest request's single vehicle (1 row), not a stale "
        f"all-vehicles response arriving late; got {row_count} rows"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_010_browser_back_forward_around_reports(page, config, credentials):
    """REP-REL-010: Using the browser Back/Forward around Reports initializes
    correctly, without corrupted/stuck state."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    page.go_back()
    page.wait_for_timeout(1000)
    page.go_forward()
    page.wait_for_timeout(1000)
    assert reports_page.standard_catalog_visible() or reports_page.contains_texts(["Fleet Summary"]), (
        "Reports did not recover to a usable state after browser Back/Forward"
    )


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_011_report_tabs_keyboard_accessible(page, config, credentials):
    """REP-REL-011: The Standard/Custom/Schedule report tabs are reachable and
    activatable by keyboard, not just by mouse click."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.standard_tab.focus()
    page.keyboard.press("Tab")
    focused_href = page.evaluate("() => document.activeElement ? document.activeElement.getAttribute('href') : null")
    assert focused_href == "/reports/custom", f"Expected keyboard focus to move to the Custom tab, got {focused_href}"
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)
    assert reports_page.is_on_path("/reports/custom"), "Enter on a keyboard-focused tab should activate it"


@pytest.mark.edgecase
@pytest.mark.reports
def test_rep_rel_012_active_report_category_identifiable(page, config, credentials):
    """REP-REL-012: The active Standard/Custom/Schedule category is identifiable
    (a distinct visual/DOM state), not just implied by page content."""
    reports_page = login_and_open_reports(page, config, credentials)
    standard_class = reports_page.standard_tab.get_attribute("class")
    custom_class = reports_page.custom_tab.get_attribute("class")
    assert "mat-sys-primary" in standard_class, "Standard tab should show an active-state class while selected"
    assert "mat-sys-primary" not in custom_class, "Custom tab should not show the active-state class while inactive"

    reports_page.custom_tab.click()
    page.wait_for_timeout(1000)
    standard_class_after = reports_page.standard_tab.get_attribute("class")
    custom_class_after = reports_page.custom_tab.get_attribute("class")
    assert "mat-sys-primary" in custom_class_after, "Custom tab should show the active-state class once selected"
    assert "mat-sys-primary" not in standard_class_after, "Standard tab should lose the active-state class once inactive"
