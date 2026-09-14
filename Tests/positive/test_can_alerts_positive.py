import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_alerts_pos_001_alert_log_renders_with_expected_columns(can_alerts_page):
    expect(can_alerts_page.alert_log_heading).to_be_visible()
    headers = can_alerts_page.rows().first.locator("xpath=ancestor::table[1]").locator("thead th")
    header_texts = [headers.nth(i).inner_text().strip() for i in range(headers.count())]
    for expected in ["Level", "Unit", "Protocol", "Metric", "Actual", "Limit", "Message"]:
        assert any(expected in header for header in header_texts), f"Missing column {expected!r} in {header_texts}"


@pytest.mark.positive
@pytest.mark.can
def test_can_alerts_pos_002_total_alert_count_matches_pagination_total(can_alerts_page):
    total = can_alerts_page.total_alert_count()
    paginated_total = can_alerts_page.pagination_total()
    assert total > 0
    assert total == paginated_total, (
        f"Header alert count ({total}) disagrees with pagination total ({paginated_total})"
    )


@pytest.mark.positive
@pytest.mark.can
def test_can_alerts_pos_003_level_values_are_only_warning_or_critical(can_alerts_page):
    levels = can_alerts_page.level_values()
    assert levels, "No alert rows to check"
    assert all(level in ("Warning", "Critical") for level in levels), f"Unexpected level values: {levels}"


@pytest.mark.positive
@pytest.mark.can
def test_can_alerts_pos_004_export_and_pagination_controls_visible(can_alerts_page):
    expect(can_alerts_page.export_button("excel")).to_be_visible()
    expect(can_alerts_page.export_button("csv")).to_be_visible()
    expect(can_alerts_page.export_button("pdf")).to_be_visible()
    expect(can_alerts_page.rows_per_page_select()).to_be_visible()
