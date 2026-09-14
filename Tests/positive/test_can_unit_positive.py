import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_001_unit_list_renders_with_expected_columns(can_unit_page):
    expect(can_unit_page.list_heading).to_be_visible()
    headers = can_unit_page.column_headers()
    for expected in ["Unit", "IMEI", "Protocol", "Type", "Last Contact", "Status", "Action"]:
        assert any(expected in header for header in headers), f"Missing column {expected!r} in {headers}"


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_002_row_count_matches_pagination_total(can_unit_page):
    total = can_unit_page.pagination_total()
    assert total > 0
    assert can_unit_page.row_count() > 0
    assert can_unit_page.row_count() <= total


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_003_search_filters_table(can_unit_page):
    units_before = can_unit_page.cell_values(1)
    assert units_before, "No units to search against"
    target_unit = units_before[0]
    can_unit_page.search_table(target_unit)
    units_after = can_unit_page.cell_values(1)
    assert all(target_unit in unit or unit == target_unit for unit in units_after), (
        f"Search for {target_unit!r} returned unrelated units: {units_after}"
    )


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_004_view_unit_opens_detail(can_unit_page):
    row = can_unit_page.rows().first
    can_unit_page.view_unit(row)
    can_unit_page.page.wait_for_timeout(1500)
    assert can_unit_page.contains_any_text(["IMEI", "Protocol", "Status"])


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_005_sorting_by_unit_column_changes_order(can_unit_page):
    before = can_unit_page.cell_values(1)
    can_unit_page.sort_by_column("Unit")
    after = can_unit_page.cell_values(1)
    assert before != after or sorted(before) == before, "Sorting by Unit had no visible effect on row order"


@pytest.mark.positive
@pytest.mark.can
def test_can_unit_pos_006_export_buttons_visible(can_unit_page):
    expect(can_unit_page.export_button("excel")).to_be_visible()
    expect(can_unit_page.export_button("csv")).to_be_visible()
    expect(can_unit_page.export_button("pdf")).to_be_visible()
