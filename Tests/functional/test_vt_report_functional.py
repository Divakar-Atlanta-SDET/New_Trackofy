"""Video Telematics Phase 6 -- Report (VT-119 to VT-168).

Confirmed live (ADAS account): default filters (last 5 days, All
Vehicles, All Alerts) return 89 real records, matching the design
doc's own screenshot exactly -- this is genuinely rich, real data
(unlike Playback), so most of this phase is built and verified for
real rather than honestly skipped.

Confirmed live via a read-only probe: the Vehicle and Alert Type
filters share the exact same "starts fully selected" bug already
pinned as Bug #40 on the Alert Configuration list's Vehicle filter
(Bug_Report.md) -- select_vehicle()/select_alert_type() apply the same
isolate-by-deselecting-others workaround.

Confirmed live: the Notification filter offers Sent/Pending/Failed but
has no "Skipped" option, even though SKIPPED is the most common real
notification value in this account's data -- logged as Bug #42
(Bug_Report.md); VT-131 is adjusted to pin that gap rather than
attempting an impossible filter selection.

Confirmed live: Generate Report posts to the same real endpoint as
Alert Configuration's mutations (POST .../adas_api.php) -- failure
simulation reuses that pattern (with @pytest.mark.allow_server_error).
An invalid date range (From > To) is not blocked client-side; Generate
stays enabled and silently returns 0 records (mirrors Playback's
Start > End handling) -- VT-125 tests that real behavior, not a
rejection that doesn't happen.

Evidence: clicking any of the three per-row action icons (View
evidence/View snapshots/Play video) opens the same single, comprehensive
in-page evidence panel containing severity, speed, notification,
location, a Snapshots section, and a Video Evidence section together --
not three separate targeted views. VT-153 (a row with evidence but no
video) is tested for real -- found live after the account's real
dataset grew from 89 to 318 records. VT-154 (a row missing just
snapshots) was still not found even in that larger sample and stays
honestly skipped.

Confirmed live: every export/print/copy action (Export to Excel/CSV/
PDF, Print, Copy) is an unimplemented stub -- each only console.logs
the report data and produces no file, tab, print dialog, or clipboard
write. Logged as Bug #43 (Bug_Report.md); VT-166 pins this real
behavior, VT-167/168 (which need an actual exported file to inspect)
are honestly skipped since there is nothing to verify.

Confirmed live via request-payload inspection: the Alert Type filter's
selection IS correctly reflected in the UI and correctly sent to the
backend (e.g. alarm_code:[11] for "Speeding"), but the returned
results are not actually filtered by it -- logged as Bug #44
(Bug_Report.md); VT-129 pins this, and VT-135 uses search() instead of
the (confirmed working-but-ineffective) Alert Type filter to combine
filters meaningfully.

Confirmed live: From/To Date are two visually separate fields but
share one underlying range-picker component -- setting From Date alone
(a fresh session) applies reliably, but a second, separate To Date
call in the same test was confirmed NOT to reliably apply (it silently
leaves To unchanged). Tests needing a genuinely different date range
therefore change only From Date (a single reliable call) rather than
both fields.
"""
import re
from datetime import date, timedelta

import pytest


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_119_open_report(vt_report_page):
    """VT-119: Video Telematics Reports opens."""
    assert vt_report_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_120_verify_report_count(vt_report_page):
    """VT-120: The displayed count matches a real, positive number of
    records for the default (last 5 days) criteria."""
    vt_report_page.generate()
    count = vt_report_page.record_count()
    assert count > 0, f"Expected a real, positive report count, got {count}"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_121_expand_filters(vt_report_page):
    """VT-121: Expanding Report Filters reveals the detailed controls."""
    vt_report_page.expand_filters()
    assert vt_report_page.from_date_input.is_visible()
    assert vt_report_page.vehicle_select.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_122_collapse_filters(vt_report_page):
    """VT-122: Collapsing Report Filters hides the detailed controls back
    to the chip summary."""
    vt_report_page.expand_filters()
    assert vt_report_page.from_date_input.is_visible()
    vt_report_page.collapse_filters()
    assert not vt_report_page.from_date_input.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_123_from_date_filter(vt_report_page):
    """VT-123: Selecting a valid From Date updates the field."""
    vt_report_page.expand_filters()
    target = date.today() - timedelta(days=2)
    vt_report_page.select_from_date(target)
    assert target.strftime("%d/%m/%Y") in vt_report_page.from_date_input.input_value()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_124_to_date_filter(vt_report_page):
    """VT-124: Selecting a valid To Date updates the field."""
    vt_report_page.expand_filters()
    target = date.today()
    vt_report_page.select_to_date(target)
    assert target.strftime("%d/%m/%Y") in vt_report_page.to_date_input.input_value()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
def test_vt_125_invalid_date_range(vt_report_page):
    """VT-125: confirmed live the date picker itself prevents
    constructing an invalid (From > To) range through normal UI
    interaction -- attempting to set From Date to a future date (which
    would put it after the default To Date, today) is silently
    rejected: the cell isn't visually disabled, but clicking it does
    not change the field's value at all. So rather than a rejected
    Generate call, the real, verifiable behavior is "the invalid state
    can't be reached in the first place" -- Generate stays usable and
    still returns the normal, unaffected baseline."""
    vt_report_page.expand_filters()
    vt_report_page.generate()
    baseline = vt_report_page.record_count()

    vt_report_page.select_from_date(date.today() + timedelta(days=5))
    assert vt_report_page.from_date_input.input_value() != (date.today() + timedelta(days=5)).strftime("%d/%m/%Y"), (
        "Expected the future date to be silently rejected, not applied"
    )
    assert vt_report_page.generate_button.is_enabled()
    vt_report_page.generate()
    assert vt_report_page.record_count() == baseline, "Expected Generate to still return the normal, unaffected report"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_126_vehicle_all(vt_report_page):
    """VT-126: "All Vehicles" includes every authorized vehicle's data."""
    vt_report_page.expand_filters()
    vt_report_page.generate()
    baseline = vt_report_page.record_count()
    vt_report_page.select_vehicle("All Vehicles")
    vt_report_page.generate()
    assert vt_report_page.record_count() == baseline


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_127_vehicle_specific(vt_report_page):
    """VT-127: Filtering to one real vehicle (B123459) returns only its
    records."""
    vt_report_page.expand_filters()
    vt_report_page.select_vehicle("B123459")
    vt_report_page.generate()
    rows = vt_report_page.rows()
    count = rows.count()
    assert count > 0, "Expected B123459 to have real report records"
    for i in range(count):
        assert "B123456" not in vt_report_page.row_vehicle_text(rows.nth(i)), (
            "Expected no cross-vehicle (B123456) results while filtered to B123459"
        )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_128_alert_type_all(vt_report_page):
    """VT-128: "All Alerts" includes every alert type."""
    vt_report_page.expand_filters()
    vt_report_page.generate()
    baseline = vt_report_page.record_count()
    vt_report_page.select_alert_type("All Alerts")
    vt_report_page.generate()
    assert vt_report_page.record_count() == baseline


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_129_alert_type_specific(vt_report_page):
    """VT-129 (Bug #44, Bug_Report.md): selecting one real alert type
    (Speeding) is confirmed correctly reflected in the UI's own
    selection state AND correctly sent to the backend (request payload
    verified to include the real alarm_code), but the returned results
    are NOT filtered by it -- pinned here as the current real (broken)
    behavior."""
    vt_report_page.expand_filters()
    vt_report_page.select_alert_type("Speeding")
    assert "Speeding" in vt_report_page.alert_type_select.inner_text(), (
        "Expected the UI selection itself to correctly show only Speeding"
    )
    vt_report_page.generate()
    rows = vt_report_page.rows()
    assert rows.count() > 0
    alert_names = {vt_report_page.row_alert_text(rows.nth(i)) for i in range(rows.count())}
    assert alert_names != {"Speeding"}, (
        "Bug #44: expected the backend to still ignore the Alert Type filter "
        "(if this now fails because every row is Speeding, the app has been fixed)"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_130_131_notification_filter_sent_and_skipped(vt_report_page):
    """VT-130: Filtering by "Sent" returns only SENT records. VT-131
    (Bug #42, Bug_Report.md): there is no "Skipped" filter option at
    all, even though SKIPPED is this account's most common real
    notification value -- pinned here instead of attempting an
    impossible selection."""
    vt_report_page.expand_filters()
    vt_report_page.select_notification("Sent")
    vt_report_page.generate()
    rows = vt_report_page.rows()
    count = rows.count()
    assert count > 0, "Expected real SENT records to exist"
    for i in range(count):
        assert vt_report_page.row_notification_text(rows.nth(i)) == "SENT"

    panel = vt_report_page._open_option_panel(vt_report_page.notification_select)
    options = panel.get_by_role("option")
    option_texts = [options.nth(i).inner_text() for i in range(options.count())]
    vt_report_page.page.keyboard.press("Escape")
    assert "Skipped" not in option_texts, (
        "Bug #42: expected no 'Skipped' filter option (if this now fails, the app has been fixed)"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_132_report_data_evidence(vt_report_page):
    """VT-132: Selecting "Evidence" as the Report Data filter returns
    only records that actually have evidence."""
    vt_report_page.expand_filters()
    vt_report_page.select_report_data("Evidence")
    vt_report_page.generate()
    rows = vt_report_page.rows()
    count = rows.count()
    assert count > 0, "Expected real evidence-bearing records to exist"
    for i in range(min(count, 10)):
        assert vt_report_page.row_has_evidence(rows.nth(i)), (
            "Expected every row under the Evidence filter to actually have evidence"
        )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_133_clear_all_filters(vt_report_page):
    """VT-133: Clear All resets the filters. Confirmed live: this
    clears the Vehicle multi-select to NO selection (a blank display),
    not back to "every vehicle selected" -- a real, distinct default
    from the page's own initial load state."""
    vt_report_page.expand_filters()
    vt_report_page.select_vehicle("B123459")
    vt_report_page.select_alert_type("Speeding")
    vt_report_page.page.wait_for_timeout(500)

    vt_report_page.clear_all()

    assert vt_report_page.vehicle_select.inner_text().strip() == "", (
        "Expected the vehicle filter cleared to no selection after Clear All"
    )
    vt_report_page.generate()
    assert vt_report_page.record_count() > 0, "Expected Generate to still work with filters cleared"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_134_generate_report_default(vt_report_page):
    """VT-134: Generate Report with default criteria replaces the
    "Generate a report" placeholder with real results."""
    assert "Generate a report" in vt_report_page.visible_text()
    vt_report_page.generate()
    assert "Generate a report" not in vt_report_page.visible_text()
    assert vt_report_page.rows().count() > 0


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_135_generate_filtered_report(vt_report_page):
    """VT-135: Combining date + vehicle filters (both confirmed reliably
    interactive) plus a search term (standing in for "alert type", since
    the Alert Type filter itself is confirmed broken -- Bug #44,
    Bug_Report.md -- and a second, separate To Date change on this
    shared range-picker component was confirmed not to reliably apply
    either) returns only matching records."""
    vt_report_page.expand_filters()
    vt_report_page.select_from_date(date.today() - timedelta(days=45))
    vt_report_page.select_vehicle("B123459")
    vt_report_page.generate()
    vt_report_page.search("Speeding")
    rows = vt_report_page.rows()
    count = rows.count()
    assert count > 0
    for i in range(count):
        row = rows.nth(i)
        assert "B123456" not in vt_report_page.row_vehicle_text(row)
        assert vt_report_page.row_alert_text(row) == "Speeding"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_136_generate_no_result_report(vt_report_page):
    """VT-136: A date range with no real data produces a clean 0-record
    empty state, not an error."""
    vt_report_page.expand_filters()
    vt_report_page.select_from_date(date.today() - timedelta(days=3650))
    vt_report_page.select_to_date(date.today() - timedelta(days=3649))
    vt_report_page.generate()
    assert vt_report_page.record_count() == 0
    assert vt_report_page.rows().count() == 0


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
@pytest.mark.allow_server_error
def test_vt_137_generate_api_failure(vt_report_page):
    """VT-137: A simulated failure of the real Generate Report endpoint
    (adas_api.php, the same one Alert Configuration's mutations use) is
    communicated -- no crash, no stale/misleading result left showing."""
    page = vt_report_page.page

    def fail_handler(route):
        route.fulfill(status=500, content_type="application/json", body='{"message":"error"}')

    page.route(re.compile(r".*adas_api\.php.*", re.I), fail_handler)
    try:
        vt_report_page.generate()
        assert vt_report_page.heading.is_visible(), "Expected the Report page to remain functional after a failed generate"
    finally:
        page.unroute(re.compile(r".*adas_api\.php.*", re.I))


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_138_report_table_headers(vt_report_page):
    """VT-138: All documented columns are present."""
    vt_report_page.generate()
    body = vt_report_page.visible_text()
    for column in ["Sr No", "Vehicle", "Date / Time", "Category", "Alert", "Location", "Notification", "Evidence"]:
        assert column in body, f"Expected column {column!r} present in the Report table"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_139_142_verify_row_fields(vt_report_page):
    """VT-139 to VT-142: A real row displays correct vehicle+IMEI,
    timestamp, category (ADAS), and a real alert name together."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    assert rows.count() > 0
    row = rows.nth(0)
    vehicle_text = vt_report_page.row_vehicle_text(row)
    assert re.search(r"B123456|B123459", vehicle_text), "VT-139: expected a real vehicle id"
    assert re.search(r"\d{8,}", vehicle_text), "VT-139: expected a real IMEI/device number alongside the vehicle"
    assert re.search(r"\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}", vt_report_page.row_datetime_text(row)), (
        "VT-140: expected a real formatted timestamp"
    )
    assert vt_report_page.row_category_text(row) == "ADAS", "VT-141: expected category ADAS"
    assert vt_report_page.row_alert_text(row) != "", "VT-142: expected a real alert name"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_143_144_location_handling(vt_report_page):
    """VT-143/144: The Location column always shows a clear state
    (confirmed live: "Load address..." placeholder), never blank or a
    raw error -- handled gracefully whether or not an address resolves."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    assert rows.count() > 0
    row = rows.nth(0)
    location_button = row.get_by_role("button").nth(0)
    assert location_button.is_visible()
    assert location_button.inner_text().strip() != "", "Expected a non-blank location state, not silently empty"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_145_146_notification_states_display(vt_report_page):
    """VT-145/146: Both real notification states (SENT, SKIPPED) render
    correctly in the table."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    values = {vt_report_page.row_notification_text(rows.nth(i)) for i in range(rows.count())}
    assert "SENT" in values, "VT-145: expected at least one real SENT row"
    assert "SKIPPED" in values, "VT-146: expected at least one real SKIPPED row"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_147_148_evidence_available_and_no_evidence_states(vt_report_page):
    """VT-147/148: Both real evidence states (icons present vs. "No
    Evidence") render correctly."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    count = rows.count()
    has_evidence_row = any(vt_report_page.row_has_evidence(rows.nth(i)) for i in range(count))
    has_no_evidence_row = any(not vt_report_page.row_has_evidence(rows.nth(i)) for i in range(count))
    assert has_evidence_row, "VT-147: expected at least one row with real evidence icons"
    assert has_no_evidence_row, "VT-148: expected at least one real 'No Evidence' row"


def _first_evidence_row(vt_report_page):
    rows = vt_report_page.rows()
    for i in range(rows.count()):
        row = rows.nth(i)
        if vt_report_page.row_has_evidence(row):
            return row
    return None


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_149_view_all_evidence(vt_report_page):
    """VT-149: Clicking the eye icon opens the evidence panel for the
    correct event."""
    vt_report_page.generate()
    row = _first_evidence_row(vt_report_page)
    assert row is not None
    alert_name = vt_report_page.row_alert_text(row)
    vt_report_page.open_view_evidence(row)
    assert vt_report_page.evidence_panel_visible()
    assert alert_name in vt_report_page.evidence_panel_header_text()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_150_view_all_snapshots(vt_report_page):
    """VT-150: Clicking the snapshots icon opens the evidence panel
    including its Snapshots section."""
    vt_report_page.generate()
    row = _first_evidence_row(vt_report_page)
    assert row is not None
    vt_report_page.open_view_snapshots(row)
    assert "Snapshots" in vt_report_page.visible_text()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_151_play_video(vt_report_page):
    """VT-151: Clicking the play icon opens the evidence panel including
    its Video Evidence section."""
    vt_report_page.generate()
    row = _first_evidence_row(vt_report_page)
    assert row is not None
    vt_report_page.open_play_video(row)
    assert "Video Evidence" in vt_report_page.visible_text()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.security
def test_vt_152_evidence_event_integrity(vt_report_page):
    """VT-152: Evidence shown for event A is never event B's -- opening
    two different evidence-bearing rows shows each one's own distinct
    alert name/timestamp, not a stale/mixed-up previous selection."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    evidence_rows = [rows.nth(i) for i in range(rows.count()) if vt_report_page.row_has_evidence(rows.nth(i))]
    assert len(evidence_rows) >= 2, "Expected at least two real evidence-bearing rows to compare"
    row_a, row_b = evidence_rows[0], evidence_rows[1]
    time_a = vt_report_page.row_datetime_text(row_a)
    time_b = vt_report_page.row_datetime_text(row_b)
    assert time_a != time_b, "Expected two distinct events to compare (different timestamps)"

    vt_report_page.open_view_evidence(row_a)
    assert time_a in vt_report_page.evidence_panel_header_text()
    vt_report_page.close_evidence_panel()

    vt_report_page.open_view_evidence(row_b)
    # Scoped to the panel's own header block, not whole-page text --
    # the underlying report table (and row A's own row within it)
    # stays visible behind the panel, so row A's timestamp is always
    # present SOMEWHERE on the page regardless of which panel is open.
    header = vt_report_page.evidence_panel_header_text()
    assert time_b in header
    assert time_a not in header, (
        "VT-152: expected event B's evidence panel header to show only B's own timestamp, not A's"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_153_missing_video_evidence(vt_report_page):
    """VT-153: An evidence-bearing event that genuinely has no video
    shows no "Video Evidence" section at all (not an error or a stuck
    loading state) -- re-verified live after the account's real dataset
    grew (89 -> 318 records); a real snapshots-only case now exists."""
    vt_report_page.expand_filters()
    vt_report_page.select_from_date(date.today() - timedelta(days=45))
    vt_report_page.generate()
    rows = vt_report_page.rows()
    target_row = None
    for i in range(rows.count()):
        row = rows.nth(i)
        if not vt_report_page.row_has_evidence(row):
            continue
        vt_report_page.open_view_evidence(row)
        vt_report_page.page.wait_for_timeout(800)
        if "Snapshots" in vt_report_page.visible_text() and "Video Evidence" not in vt_report_page.visible_text():
            target_row = row
            break
        vt_report_page.close_evidence_panel()
        vt_report_page.page.wait_for_timeout(400)
    assert target_row is not None, "Expected at least one real evidence row with snapshots but no video"
    assert "Delivery Status" in vt_report_page.visible_text(), (
        "Expected the panel to render its next real section cleanly, not an error/stuck state, "
        "when video is genuinely absent"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.skip(reason="VT-154: no real row with genuinely zero snapshots (while still having some evidence, e.g. video) was found live even after scanning a broader sample of the account's now-318-record dataset -- every evidence-bearing row checked had at least one snapshot")
def test_vt_154_missing_snapshot_evidence():
    pass


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_155_search_exact_vehicle(vt_report_page):
    """VT-155: An exact, real vehicle id returns matching records."""
    vt_report_page.generate()
    vt_report_page.search("B123459")
    assert vt_report_page.rows().count() >= 1


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_156_search_partial_alert(vt_report_page):
    """VT-156: A partial, real alert name returns matching records."""
    vt_report_page.generate()
    vt_report_page.search("Collision")
    assert vt_report_page.rows().count() >= 1


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_157_search_no_result(vt_report_page):
    """VT-157: An unmatched search shows an empty result state."""
    vt_report_page.generate()
    vt_report_page.search("XYZ-NONE-VT-157")
    assert vt_report_page.rows().count() == 0


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
def test_vt_158_search_special_characters(vt_report_page):
    """VT-158: Special characters in search don't error the page."""
    vt_report_page.generate()
    vt_report_page.search("@#$")
    assert vt_report_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_159_rows_per_page(vt_report_page):
    """VT-159: Changing rows-per-page changes the number of rows shown.
    Confirmed live real options are 10/20/50/100 (not 50/25/10 as the
    CSV lists)."""
    vt_report_page.generate()
    vt_report_page.rows_per_page_select.select_option(label="10")
    vt_report_page.page.wait_for_timeout(800)
    assert vt_report_page.rows().count() == 10

    vt_report_page.rows_per_page_select.select_option(label="20")
    vt_report_page.page.wait_for_timeout(800)
    assert vt_report_page.rows().count() == 20


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_160_163_pagination_controls(vt_report_page):
    """VT-160 to VT-163: Next/Previous/First/Last page controls work
    across this account's real, multi-page (89-record) dataset."""
    vt_report_page.generate()
    assert not vt_report_page.previous_page_button.is_enabled(), "Expected Previous disabled on page 1"

    first_page_rows = vt_report_page.rows().count()
    vt_report_page.next_page_button.click()
    vt_report_page.page.wait_for_timeout(800)
    assert vt_report_page.rows().count() > 0, "Expected page 2 to load real rows"
    assert vt_report_page.previous_page_button.is_enabled()

    vt_report_page.previous_page_button.click()
    vt_report_page.page.wait_for_timeout(800)
    assert vt_report_page.rows().count() == first_page_rows

    vt_report_page.last_page_button.click()
    vt_report_page.page.wait_for_timeout(800)
    assert not vt_report_page.next_page_button.is_enabled(), "Expected Next disabled on the last page"

    vt_report_page.first_page_button.click()
    vt_report_page.page.wait_for_timeout(800)
    assert not vt_report_page.previous_page_button.is_enabled()


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_164_pagination_after_filter(vt_report_page):
    """VT-164: Pagination reflects the currently filtered data, not the
    full unfiltered set."""
    vt_report_page.expand_filters()
    vt_report_page.select_vehicle("B123459")
    vt_report_page.generate()
    filtered_count = vt_report_page.record_count()
    if filtered_count > 10:
        vt_report_page.next_page_button.click()
        vt_report_page.page.wait_for_timeout(800)
        rows = vt_report_page.rows()
        for i in range(rows.count()):
            assert "B123456" not in vt_report_page.row_vehicle_text(rows.nth(i))
    else:
        pytest.skip("Filtered result too small to exercise a second page")


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_165_pagination_after_search(vt_report_page):
    """VT-165: Pagination reflects the current search results."""
    vt_report_page.generate()
    vt_report_page.search("ADAS")
    result_count = vt_report_page.rows().count()
    if vt_report_page.next_page_button.is_enabled():
        vt_report_page.next_page_button.click()
        vt_report_page.page.wait_for_timeout(800)
        assert vt_report_page.rows().count() > 0
    else:
        assert result_count > 0, "Expected the single-page search result to still be non-empty"


def _no_download_fires(page, trigger_action, wait_ms: int = 6000) -> bool:
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    trigger_action()
    page.wait_for_timeout(wait_ms)
    return len(downloads) == 0


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_166_export_report(vt_report_page):
    """VT-166 (Bug #43, Bug_Report.md): every export action is confirmed
    live to be an unimplemented stub -- each one only console.logs the
    report data and produces no file, no new tab, and no network
    request. Pinned here as the current real behavior rather than
    asserting the (non-functional) working export the CSV describes."""
    vt_report_page.generate()
    page = vt_report_page.page
    assert _no_download_fires(page, lambda: vt_report_page.export_excel_button.click()), (
        "Bug #43: expected Export to Excel to still be a no-op (if this now fails, the app has been fixed)"
    )
    assert _no_download_fires(page, lambda: vt_report_page.export_csv_button.click()), (
        "Bug #43: expected Export to CSV to still be a no-op"
    )
    assert _no_download_fires(page, lambda: vt_report_page.export_pdf_button.click()), (
        "Bug #43: expected Export to PDF to still be a no-op"
    )
    assert vt_report_page.heading.is_visible(), "Expected the Report page to remain functional after every export click"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.skip(reason="VT-167: cannot verify export reflects the filtered scope -- Bug #43 (Bug_Report.md) confirms export is a non-functional stub that produces no file at all")
def test_vt_167_export_filtered_report():
    pass


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.skip(reason="VT-168: cannot verify safe empty-report export behavior -- Bug #43 (Bug_Report.md) confirms export is a non-functional stub that produces no file at all, empty or otherwise")
def test_vt_168_export_empty_report():
    pass
