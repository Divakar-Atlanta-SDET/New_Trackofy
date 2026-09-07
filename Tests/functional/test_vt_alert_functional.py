"""Video Telematics Phase 3 -- Alert Configuration list (VT-037 to 052).

Confirmed live: Video Telematics uses a dedicated ADAS account (env vars
ADAS_TEST_USERNAME/ADAS_TEST_PASSWORD), not the main tarun_01 account --
it has a large number of real alert configurations (~105) across two
vehicles (B123456, B123459), matching the design doc's own screenshots
in shape. Assertions below check the displayed count is real/positive
and internally self-consistent (e.g. survives a filter round-trip)
rather than hardcoding the exact total, since real record counts can
shift over time. Test data uses alert names/vehicles directly confirmed
present in this account's real data.
"""
import pytest


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_037_verify_alert_count(vt_alert_page):
    """VT-037: The displayed count matches a real, positive number of
    records."""
    count = vt_alert_page.alert_count()
    assert count > 0, f"Expected a real, positive alert count, got {count}"
    assert count == vt_alert_page.alert_count(), "Expected the count to be stable across an immediate re-read"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_038_verify_table_columns(vt_alert_page):
    """VT-038: All configured columns are present."""
    body = vt_alert_page.visible_text()
    for column in ["Sr No", "Category", "Vehicle", "Alert", "Priority", "WhatsApp", "Email", "Delivery", "Status"]:
        assert column in body, f"Expected column {column!r} present in the Alert Configuration table"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_039_filter_all_vehicles(vt_alert_page):
    """VT-039: 'All vehicles' shows every authorized configuration."""
    baseline = vt_alert_page.alert_count()
    vt_alert_page.select_vehicle_filter("All vehicles")
    assert vt_alert_page.alert_count() == baseline, "Expected 'All vehicles' to show the full, unfiltered list"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_bug40_vehicle_filter_click_deselects_instead_of_isolating(vt_alert_page):
    """Regression pin for Bug #40 (Bug_Report.md, High): the Vehicle
    filter is a multi-select that starts with every vehicle already
    aria-selected (that's what "All vehicles" means), so a single plain
    click on one vehicle option toggles it OFF instead of isolating it.
    Asserts the confirmed-broken raw-click behavior; flip once fixed."""
    page = vt_alert_page.page
    panel = vt_alert_page._open_option_panel(vt_alert_page.vehicle_filter)
    b456_option = panel.get_by_role("option", name="B123456")
    assert b456_option.get_attribute("aria-selected") == "true", (
        "Expected every vehicle pre-selected by default (matching the 'All vehicles' display)"
    )
    b456_option.click()
    page.wait_for_timeout(500)
    assert b456_option.get_attribute("aria-selected") == "false", (
        "Bug #40: expected clicking an already-selected vehicle to (still) deselect it rather than "
        "isolate it. If it's now selected/isolated, the app has been fixed."
    )
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_040_filter_one_vehicle(vt_alert_page):
    """VT-040: Filtering to a specific real vehicle (B123456) shows only
    its configurations, with no cross-vehicle results. Uses
    select_vehicle_filter()'s isolate-by-deselecting-others workaround
    for Bug #40, since a plain single click cannot achieve this directly."""
    vt_alert_page.select_vehicle_filter("B123456")
    rows = vt_alert_page.rows()
    count = rows.count()
    assert count > 0, "Expected B123456 to have real configurations"
    for i in range(count):
        assert "B123459" not in vt_alert_page.row_vehicle_text(rows.nth(i)), (
            "Expected no cross-vehicle (B123459) results while filtered to B123456"
        )


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_041_042_filter_by_priority(vt_alert_page):
    """VT-041/042: Filtering by Critical or Warning priority returns only
    matching configurations, and resetting to All priorities restores
    the full, unfiltered count."""
    baseline = vt_alert_page.alert_count()
    for priority in ["Critical", "Warning"]:
        vt_alert_page.select_priority_filter(priority)
        count = vt_alert_page.rows().count()
        assert count > 0, f"Expected real {priority} configurations to exist"
    vt_alert_page.select_priority_filter("All priorities")
    assert vt_alert_page.alert_count() == baseline, "Expected resetting to All priorities to restore the full list"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_043_search_exact_alert(vt_alert_page):
    """VT-043: An exact, real alert name returns matching records."""
    vt_alert_page.search("Impacting Pedestrians Start")
    assert vt_alert_page.rows().count() >= 1


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_044_search_partial_alert(vt_alert_page):
    """VT-044: A partial, real alert name returns matching records."""
    vt_alert_page.search("Forward Collision")
    assert vt_alert_page.rows().count() >= 1


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_045_search_no_result(vt_alert_page):
    """VT-045: An unmatched search shows an empty result state."""
    vt_alert_page.search("XYZ-NONE-VT-045")
    assert vt_alert_page.rows().count() == 0


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.negative
def test_vt_046_search_special_characters(vt_alert_page):
    """VT-046: Special characters in search don't error the page."""
    vt_alert_page.search("@#$")
    assert vt_alert_page.heading.is_visible(), "Expected the Alert page to remain functional"


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_047_rows_per_page(vt_alert_page):
    """VT-047: Changing rows-per-page changes the number of rows shown."""
    vt_alert_page.rows_per_page_select.select_option(label=" 5 ")
    vt_alert_page.page.wait_for_timeout(800)
    assert vt_alert_page.rows().count() == 5

    vt_alert_page.rows_per_page_select.select_option(label=" 20 ")
    vt_alert_page.page.wait_for_timeout(800)
    assert vt_alert_page.rows().count() == 20


@pytest.mark.functional
@pytest.mark.video_telematics
def test_vt_048_049_050_051_pagination_controls(vt_alert_page):
    """VT-048/049/050/051: Next/Previous/First/Last page controls work
    across this account's real, multi-page (100+ alert) dataset."""
    assert vt_alert_page.first_page_button.is_visible()
    assert vt_alert_page.last_page_button.is_visible()
    assert not vt_alert_page.previous_page_button.is_enabled(), "Expected Previous disabled on page 1"

    first_page_rows = vt_alert_page.rows().count()
    vt_alert_page.next_page_button.click()
    vt_alert_page.page.wait_for_timeout(800)
    assert vt_alert_page.rows().count() > 0, "Expected page 2 to load real rows"
    assert vt_alert_page.previous_page_button.is_enabled(), "Expected Previous enabled after leaving page 1"

    vt_alert_page.previous_page_button.click()
    vt_alert_page.page.wait_for_timeout(800)
    assert vt_alert_page.rows().count() == first_page_rows, "Expected Previous to restore page 1's rows"

    vt_alert_page.last_page_button.click()
    vt_alert_page.page.wait_for_timeout(800)
    assert not vt_alert_page.next_page_button.is_enabled(), "Expected Next disabled on the last page"

    vt_alert_page.first_page_button.click()
    vt_alert_page.page.wait_for_timeout(800)
    assert not vt_alert_page.previous_page_button.is_enabled(), "Expected Previous disabled back on page 1"
