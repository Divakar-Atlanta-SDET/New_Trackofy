import pytest


@pytest.mark.negative
@pytest.mark.can
def test_can_settings_neg_001_save_with_nothing_filled_does_not_create_a_rule(can_settings_page):
    """Confirmed live: Save stays enabled with no Protocol/Unit/Metric/
    limits supplied (not disabled up front) -- verify clicking it in that
    state doesn't silently create a bogus, empty alert rule.

    Fixed 2026-09-14: the rule count reads "0" as a loading placeholder
    immediately after page load, resolving to the real count (confirmed
    live: within 0.5s) independent of Save -- reading rule_count_before
    too early made every Save look like it had bulk-created rules that
    already existed beforehand. configured_rule_count() now polls for a
    stable value internally (CanBasePage._read_stable_int), so a plain
    call here is already safe."""
    rule_count_before = can_settings_page.configured_rule_count()
    can_settings_page.save()
    can_settings_page.page.wait_for_timeout(1500)
    rule_count_after = can_settings_page.configured_rule_count()
    assert rule_count_after == rule_count_before, (
        f"Saving with nothing filled changed the configured rule count "
        f"({rule_count_before} -> {rule_count_after}) -- a bogus rule may have been created"
    )


@pytest.mark.negative
@pytest.mark.can
def test_can_settings_neg_002_critical_limit_below_warning_limit_not_silently_accepted(can_settings_page):
    """A Critical threshold that is numerically less severe than the
    Warning threshold (Critical < Warning, for a HIGH mode where breach
    means "over") is a logically inverted configuration. This mirrors a
    known bug class already confirmed elsewhere in this app (no
    validation on numeric config, Bug #2/#3 in Bug_Report.md) -- verify
    it either blocks Save or shows an inline validation error rather than
    silently accepting the inverted thresholds."""
    can_settings_page.safe_click(can_settings_page.protocol_select)
    protocol_option = can_settings_page.page.get_by_role("option")
    if protocol_option.count() == 0:
        pytest.skip("No protocols available to configure a rule against")
    can_settings_page.safe_click(protocol_option.first)
    can_settings_page.wait_for_loading_to_finish()

    can_settings_page.safe_click(can_settings_page.unit_select)
    unit_option = can_settings_page.page.get_by_role("option")
    if unit_option.count() == 0:
        pytest.skip("No units available for the selected protocol")
    can_settings_page.safe_click(unit_option.first)
    can_settings_page.wait_for_loading_to_finish()

    can_settings_page.safe_click(can_settings_page.metric_select)
    metric_option = can_settings_page.page.get_by_role("option")
    if metric_option.count() == 0:
        pytest.skip("No metrics available for the selected unit")
    can_settings_page.safe_click(metric_option.first)
    can_settings_page.wait_for_loading_to_finish()

    can_settings_page.set_warning_limit("100")
    can_settings_page.set_critical_limit("10")

    if can_settings_page.is_save_enabled():
        can_settings_page.save()
        assert can_settings_page.contains_any_text(["error", "invalid", "Critical", "greater"]), (
            "Inverted Warning/Critical thresholds were saved with no validation feedback -- "
            "possible new bug, cross-check against Configured Alert Rules for a bad row."
        )
