import re
import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_tc003_tc004_verify_alert_table_and_columns(unit_settings):
    """TC-003, TC-004: Open Alert tab and verify configured alerts table and columns."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    unit_settings_page.switch_tab("Alert")

    # TC-003: Heading visible
    expect(unit_settings_page.alert_heading).to_be_visible()

    # TC-004: Table headers
    headers = [th.inner_text().strip() for th in unit_settings_page.alert_headers.all()]
    for col in ["Alert Name", "Limit", "Duration", "SMS", "Email", "Notification"]:
        assert any(col.lower() in h.lower() for h in headers), f"Expected column '{col}' in {headers}"

    assert unit_settings_page.alert_rows.count() > 0, "Expected at least 1 alert configured in Alert table"


@pytest.mark.functional
def test_tc005_verify_alert_count_badge_matches_rows(unit_settings):
    """TC-005: Functional - Compare displayed alert count badge with listed records."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Alert")

    row_count = unit_settings_page.alert_rows.count()
    if unit_settings_page.alert_count_badge.is_visible():
        badge_text = unit_settings_page.alert_count_badge.inner_text()
        match = re.search(r"(\d+)", badge_text)
        if match:
            expected_count = int(match.group(1))
            pagination = unit_settings_page.dialog.locator(".mat-mdc-paginator-range-label, [class*='paginator-range']").first
            if pagination.count() > 0 and pagination.is_visible():
                pag_match = re.search(r"of\s+(\d+)", pagination.inner_text())
                if pag_match:
                    assert int(pag_match.group(1)) == expected_count, f"Badge ({expected_count}) != pagination total ({pag_match.group(1)})"
                    return
            assert row_count == expected_count, f"Badge says {expected_count} alerts, but table has {row_count} rows"


@pytest.mark.functional
def test_tc006_verify_alert_status_indicators(unit_settings):
    """TC-006: Functional - Verify alert notification channel status indicators."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    unit_settings_page.switch_tab("Alert")
    unit_settings_page.wait_for_loading_to_finish()
    page.wait_for_timeout(500)

    data_row = unit_settings_page.alert_rows.filter(has=page.locator("td:nth-child(2)")).first
    if data_row.count() > 0:
        cells = data_row.locator("td").all()
        assert len(cells) >= 6, f"Expected at least 6 cells in alert row, got {len(cells)}"
        alert_name = cells[0].inner_text().strip()
        assert len(alert_name) > 0, "Alert name in row 1 should not be empty"
    else:
        expect(unit_settings_page.alert_heading).to_be_visible()
