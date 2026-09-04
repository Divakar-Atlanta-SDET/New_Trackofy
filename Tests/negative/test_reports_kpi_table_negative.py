import re
import pytest
from config.config import REPORT_TEST_VEHICLE_NAME

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.negative
@pytest.mark.reports
def test_rep_kpi_022_no_stale_values_after_report_switch(page, config, credentials):
    """REP-KPI-022: After changing filters (and passing through a report type that
    has no KPI cards at all, e.g. Work Hour), KPI cards reflect only the new
    report/filter -- not a stale value left over from an earlier generation."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()
    total_all = int(reports_page.get_kpi_card_value("Total Units"))
    assert total_all > 1, "Expected more than one unit with all vehicles selected"

    # Work Hour has no KPI cards at all (confirmed live) -- passing through it and
    # back should not leave Fleet Summary's cards showing the old aggregate value.
    reports_page.click_back()
    reports_page.generate_standard_report(
        "Work Hour",
        start_date="01/09/2026",
        end_date="01/09/2026",
        vehicle_name=REPORT_TEST_VEHICLE_NAME,
        driver_name="",
    )
    assert not reports_page.kpi_cards_visible(), "Work Hour should not show Fleet Summary's KPI cards"

    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()
    reports_page.wait_for_table()
    total_single = int(reports_page.get_kpi_card_value("Total Units"))
    assert total_single == 1, (
        f"Total Units should reflect the new single-vehicle filter (1), not a stale value ({total_single})"
    )


@pytest.mark.negative
@pytest.mark.reports
def test_rep_kpi_023_no_stale_kpi_from_earlier_request(page, config, credentials):
    """Regression pin for Bug_Report.md #18: REP-KPI-023 requires that a delayed
    response from an earlier request must NOT overwrite KPI values belonging to
    the latest report request. Confirmed live that it currently DOES: delaying the
    first (all-vehicles) fleet_summary_aggregate response past the second
    (single-vehicle, faster) request lets the stale first response overwrite the
    correct, current KPI values once it finally arrives. This test documents that
    confirmed (broken) behavior -- if it starts failing, the race has likely been
    fixed; update/remove this test and flip Bug_Report.md #18 accordingly."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")

    first_request_seen = {"done": False}

    def _delay_first_aggregate(route):
        if "fleet_summary_aggregate" in route.request.url and not first_request_seen["done"]:
            first_request_seen["done"] = True
            page.wait_for_timeout(4000)
        route.continue_()

    page.route("**/api/v3/fleet_summary_aggregate", _delay_first_aggregate)

    reports_page.select_all_vehicles()
    reports_page.click_fetch()  # request #1 (all vehicles) -- its aggregate response is delayed
    page.wait_for_timeout(300)  # let request #1 start before firing request #2

    reports_page.click_back()
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle(REPORT_TEST_VEHICLE_NAME)
    reports_page.click_fetch()  # request #2 (single vehicle) -- not delayed
    reports_page.wait_for_table()
    page.wait_for_timeout(5000)  # long enough for the delayed request #1 response to also land

    page.unroute("**/api/v3/fleet_summary_aggregate", _delay_first_aggregate)
    final_total = int(reports_page.get_kpi_card_value("Total Units"))
    assert final_total != 1, (
        "Expected the known stale-overwrite bug (Bug_Report.md #18): the delayed "
        "all-vehicles response should still clobber the correct single-vehicle value "
        "(1) once it arrives late, showing the larger fleet-wide count instead. "
        "Got 1 -- the race condition appears fixed; update/remove this test."
    )


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.allow_server_error
def test_rep_kpi_024_kpi_api_fails_table_still_usable(page, config, credentials):
    """REP-KPI-024: Report table loads but the KPI API fails -- app should show a
    clear KPI error/empty state, not misleading stale/zero values presented as real."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    page.route("**/api/v3/fleet_summary_aggregate", lambda route: route.fulfill(status=500, body="{}"))
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    reports_page.wait_for_table()
    page.unroute("**/api/v3/fleet_summary_aggregate")

    assert reports_page.has_results_table(), "Table should still load when only the KPI API fails"
    total_units = reports_page.get_kpi_card_value("Total Units")
    assert not (total_units.isdigit() and int(total_units) > 0), (
        f"KPI card should not show a misleading real-looking value ('{total_units}') when its API failed"
    )


@pytest.mark.negative
@pytest.mark.reports
@pytest.mark.allow_server_error
def test_rep_kpi_025_table_api_fails_kpi_not_presented_as_reconciled(page, config, credentials):
    """REP-KPI-025: KPI data loads but the report table API fails -- app must not
    present the page as a successfully reconciled KPI+table result."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    page.route("**/api/v3/fleet_summary_new", lambda route: route.fulfill(status=500, body="{}"))
    reports_page.select_all_vehicles()
    reports_page.click_fetch()
    page.wait_for_timeout(5000)
    page.unroute("**/api/v3/fleet_summary_new")

    assert not reports_page.has_results_table(), (
        "Table should not render successfully when its own API call failed"
    )
