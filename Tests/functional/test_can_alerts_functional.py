import pytest


@pytest.mark.functional
@pytest.mark.can
def test_can_alerts_func_001_critical_filter_returns_only_critical_rows(can_alerts_page):
    can_alerts_page.filter_by_level("Critical")
    levels = can_alerts_page.level_values(max_rows=25)
    assert levels, "Critical filter returned no rows to check"
    assert all(level == "Critical" for level in levels), (
        f"Level=Critical filter leaked non-Critical rows: {levels}"
    )


@pytest.mark.functional
@pytest.mark.can
def test_can_alerts_func_002_warning_filter_returns_only_warning_rows(can_alerts_page):
    can_alerts_page.filter_by_level("Warning")
    levels = can_alerts_page.level_values(max_rows=25)
    assert levels, "Warning filter returned no rows to check"
    assert all(level == "Warning" for level in levels), (
        f"Level=Warning filter leaked non-Warning rows: {levels}"
    )


@pytest.mark.functional
@pytest.mark.can
def test_can_alerts_func_003_actual_vs_limit_consistent_with_level_for_sampled_rows(can_alerts_page):
    """Data-sense check: a Critical alert whose Actual value does not
    plausibly breach its own Limit (e.g. Actual == Limit or Actual well
    under Limit for a metric where breach means "over") is a signal the
    Level/Actual/Limit computation may be wrong. Recorded as an
    observation rather than a hard failure for the generic case, since
    the correct breach direction (over vs under limit) is metric-specific
    and not documented -- flags rows for manual/bug-report follow-up
    instead of asserting a business rule the test doesn't actually know.
    """
    unit_rows = can_alerts_page.rows()
    count = min(unit_rows.count(), 15)
    suspicious = []
    for i in range(count):
        cells = unit_rows.nth(i).locator("td")
        level = cells.nth(1).inner_text().strip()
        metric = cells.nth(5).inner_text().strip()
        actual = cells.nth(6).inner_text().strip()
        limit = cells.nth(7).inner_text().strip()
        if level == "Critical" and actual == limit:
            suspicious.append((metric, actual, limit))
    if suspicious:
        pytest.fail(
            "Critical alert rows with Actual == Limit (ambiguous/likely-wrong breach data): "
            f"{suspicious}"
        )
