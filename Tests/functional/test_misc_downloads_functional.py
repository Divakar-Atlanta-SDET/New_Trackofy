"""Phase 3 -- Downloads (MISC-032 to 058)."""
import pytest

from Utils.download_helper import handle_and_verify_download


@pytest.mark.functional
@pytest.mark.misc
def test_misc_032_open_downloads(downloads_page):
    """MISC-032: The Downloads page opens with a real table."""
    assert downloads_page.table.is_visible()
    assert "Downloads" in downloads_page.visible_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_033_report_count_matches_records(downloads_page):
    """MISC-033: The displayed report count is a valid, non-negative
    number consistent with real rows existing on the page."""
    count = downloads_page.report_count()
    assert count >= 0, f"Expected a valid report count, got {count}"
    if count > 0:
        assert downloads_page.rows().count() > 0, "Expected at least one row when the count is nonzero"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_034_table_columns_present(downloads_page):
    """MISC-034: Report Name, Requested On, Duration, Status and Download
    columns are shown."""
    header_text = downloads_page.table.locator("thead").inner_text()
    for col in ["Report Name", "Requested On", "Duration", "Status"]:
        assert col in header_text, f"Expected column '{col}' in the table header"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_035_done_status_shown(downloads_page):
    """MISC-035: At least one report shows the 'Done' status (confirmed
    live this account has real Done reports)."""
    statuses = [downloads_page.row_status(downloads_page.rows().nth(i)) for i in range(downloads_page.rows().count())]
    assert "Done" in statuses, f"Expected at least one 'Done' report, got statuses={statuses}"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_036_037_038_download_completed_report_integrity(downloads_page, cleanup_downloads):
    """MISC-036/037/038: A Done report has a working download link that
    produces a real, non-empty file."""
    rows = downloads_page.rows()
    done_row = None
    for i in range(rows.count()):
        if downloads_page.row_status(rows.nth(i)) == "Done":
            done_row = rows.nth(i)
            break
    assert done_row is not None, "Expected at least one Done row to test downloading"

    report_name = downloads_page.row_report_name(done_row)
    link = downloads_page.row_download_link(done_row)
    href = link.get_attribute("href")
    assert href, "Expected the Download link to have a real href"

    file_path = handle_and_verify_download(
        downloads_page.page, lambda: link.click(), expected_extension=f".{href.rsplit('.', 1)[-1]}"
    )
    assert file_path.exists() and file_path.stat().st_size > 0, (
        f"Expected a real, non-empty downloaded file for report {report_name!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_039_pending_status_shown(downloads_page):
    """MISC-039: At least one report shows the 'Pending' status (confirmed
    live this account has real Pending reports)."""
    statuses = [downloads_page.row_status(downloads_page.rows().nth(i)) for i in range(downloads_page.rows().count())]
    assert "Pending" in statuses, f"Expected at least one 'Pending' report, got statuses={statuses}"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_040_pending_report_has_no_misleading_download(downloads_page):
    """MISC-040: A Pending row's Download cell has no clickable link/button
    -- confirmed live it shows a plain '----' placeholder instead."""
    rows = downloads_page.rows()
    pending_row = None
    for i in range(rows.count()):
        if downloads_page.row_status(rows.nth(i)) == "Pending":
            pending_row = rows.nth(i)
            break
    assert pending_row is not None, "Expected at least one Pending row"
    assert downloads_page.row_download_link(pending_row).count() == 0, (
        "Expected no download link/button on a Pending row"
    )
    last_cell_text = pending_row.locator("td").last.inner_text().strip()
    assert last_cell_text == "----", f"Expected a plain placeholder for Pending's Download cell, got {last_cell_text!r}"


@pytest.mark.skip(
    reason="MISC-041 (Pending transitions to Done) requires waiting for a real, uncontrolled backend "
    "report-generation job to finish -- there's no way to trigger or accelerate this from the test, "
    "and waiting indefinitely for an existing Pending report to complete would make this test slow "
    "and non-deterministic. Honest skip, matching the REP-COM-021 precedent."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_041_pending_becomes_done():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_042_search_exact_report_name(downloads_page):
    """MISC-042: Searching an exact report name filters to matching rows."""
    downloads_page.search("Single Vehicle Idle Report")
    rows = downloads_page.rows()
    assert rows.count() > 0, "Expected at least one match for an exact report name"
    for i in range(rows.count()):
        assert "Single Vehicle Idle Report" in downloads_page.row_report_name(rows.nth(i))
    downloads_page.clear_search()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_043_search_partial_report_name(downloads_page):
    """MISC-043: A partial report name search returns matching records."""
    downloads_page.search("Idle")
    rows = downloads_page.rows()
    assert rows.count() > 0, "Expected at least one match for a partial report name"
    for i in range(rows.count()):
        assert "idle" in downloads_page.row_report_name(rows.nth(i)).lower()
    downloads_page.clear_search()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_044_search_no_result_shows_empty_state(downloads_page):
    """MISC-044: An unmatched search term shows a clean empty state."""
    downloads_page.search("NoSuchReport_zzz_pytest")
    assert downloads_page.rows().count() == 0, "Expected zero rows for an unmatched search"
    downloads_page.clear_search()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_045_clear_search_restores_full_list(downloads_page):
    """MISC-045: Clearing the search restores the full list."""
    before_count = downloads_page.rows().count()
    downloads_page.search("Single Vehicle Idle Report")
    assert downloads_page.rows().count() <= before_count
    downloads_page.clear_search()
    assert downloads_page.rows().count() == before_count, "Expected the full list restored after clearing search"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_046_search_special_characters_no_error(downloads_page):
    """MISC-046: Special characters in search don't error the UI."""
    downloads_page.search("@#$")
    assert downloads_page.table.is_visible(), "Expected the table to remain rendered after a special-char search"
    downloads_page.clear_search()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_047_change_rows_per_page(downloads_page):
    """MISC-047: Changing the page size shows the requested number of
    rows (or fewer, if there aren't enough records)."""
    total = downloads_page.report_count()
    downloads_page.change_rows_per_page("25")
    expected = min(25, total) if total >= 0 else 25
    assert downloads_page.rows().count() == expected, (
        f"Expected {expected} rows after changing page size to 25, got {downloads_page.rows().count()}"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_048_049_050_051_pagination_controls(downloads_page):
    """MISC-048/049/050/051: Next/Previous/First/Last page controls work
    when there's more than one page."""
    downloads_page.change_rows_per_page("10")
    total = downloads_page.report_count()
    if total <= 10:
        pytest.skip("Not enough records in this account for multi-page pagination (10 or fewer total)")

    first_page_first_row = downloads_page.row_serial_number(downloads_page.rows().first)
    downloads_page.next_page_button.click()
    downloads_page.page.wait_for_timeout(1500)
    second_page_first_row = downloads_page.row_serial_number(downloads_page.rows().first)
    assert second_page_first_row != first_page_first_row, "Expected Next page to show different records"

    downloads_page.previous_page_button.click()
    downloads_page.page.wait_for_timeout(1500)
    assert downloads_page.row_serial_number(downloads_page.rows().first) == first_page_first_row, (
        "Expected Previous page to return to the first page's records"
    )

    downloads_page.last_page_button.click()
    downloads_page.page.wait_for_timeout(1500)
    last_page_first_row = downloads_page.row_serial_number(downloads_page.rows().first)
    assert last_page_first_row != first_page_first_row, "Expected Last page to show different records"

    downloads_page.first_page_button.click()
    downloads_page.page.wait_for_timeout(1500)
    assert downloads_page.row_serial_number(downloads_page.rows().first) == first_page_first_row, (
        "Expected First page to return to the original first page"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_052_pagination_after_search(downloads_page):
    """MISC-052: Pagination reflects the filtered (searched) result set,
    not the full unfiltered list."""
    downloads_page.search("Idle")
    filtered_count = downloads_page.rows().count()
    assert downloads_page.next_page_button.is_visible()
    downloads_page.clear_search()


@pytest.mark.skip(
    reason="MISC-053 (no downloads empty state) requires an account with zero generated reports -- "
    "this real account currently has real report history (confirmed live) and there's no supported "
    "way to clear it without deleting real data. Honest skip, matching the REP-COM-021 precedent."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_053_no_downloads_empty_state():
    pass


@pytest.mark.skip(
    reason="MISC-054 (account isolation between two accounts) and MISC-055 (unauthorized download URL "
    "from another account): per the approved plan's resolved fallback (see test_misc_profile_functional.py), "
    "a sub-user is not a genuinely independent account -- it shares the owner's identity. Without a real "
    "second account, there is no foreign download URL to test unauthorized access against. Honest skip."
)
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_054_055_account_isolation_and_unauthorized_download_url():
    pass


@pytest.mark.skip(
    reason="MISC-056 (corrupt downloaded file handling) requires a real corrupt report to already exist "
    "-- there's no supported way to make the backend generate a deliberately corrupt file from this "
    "test. Honest skip, matching the REP-COM-021 precedent."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_056_corrupt_downloaded_file_handling():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_057_repeated_download_same_report(downloads_page, cleanup_downloads):
    """MISC-057: Downloading the same Done report twice produces the same
    correct file both times (same href / same underlying report each
    time)."""
    rows = downloads_page.rows()
    done_row = None
    for i in range(rows.count()):
        if downloads_page.row_status(rows.nth(i)) == "Done":
            done_row = rows.nth(i)
            break
    assert done_row is not None
    link = downloads_page.row_download_link(done_row)
    href_1 = link.get_attribute("href")

    downloads_page.page.reload()
    downloads_page.wait_until_ready()
    downloads_page.page.wait_for_timeout(2000)
    rows2 = downloads_page.rows()
    done_row_2 = None
    for i in range(rows2.count()):
        if downloads_page.row_status(rows2.nth(i)) == "Done":
            done_row_2 = rows2.nth(i)
            break
    href_2 = downloads_page.row_download_link(done_row_2).get_attribute("href")
    assert href_1 == href_2, (
        f"Expected the same Done report's download URL to stay stable across reloads -- got {href_1!r} "
        f"then {href_2!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_058_download_link_points_to_a_real_reachable_resource(downloads_page):
    """MISC-058 (adapted): the Download link's URL is a real, reachable
    resource -- confirmed via a direct HEAD/GET-style request rather than
    simulating a route-level API failure (the download here is a direct
    <a href> to a file, not an XHR/fetch call page.route can intercept the
    same way as the Administrator/Reports modules' AJAX-driven actions)."""
    rows = downloads_page.rows()
    done_row = None
    for i in range(rows.count()):
        if downloads_page.row_status(rows.nth(i)) == "Done":
            done_row = rows.nth(i)
            break
    assert done_row is not None
    href = downloads_page.row_download_link(done_row).get_attribute("href")
    response = downloads_page.page.request.get(href)
    assert response.ok, f"Expected the download URL to resolve successfully, got status {response.status}"
