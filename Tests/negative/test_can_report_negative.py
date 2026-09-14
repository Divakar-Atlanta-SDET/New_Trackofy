import pytest


@pytest.mark.negative
@pytest.mark.can
def test_can_report_neg_001_generate_with_nothing_selected_does_not_crash(can_report_page):
    """Confirmed live: Generate Report stays enabled with no Protocol/
    Units selected (not disabled up front), and clicking it in that state
    generates an unfiltered/default-scope report rather than erroring --
    real server-error detection is handled by the can_authenticated_page
    fixture's global 5xx tracking (conftest.py), so this just confirms
    the UI settles into a real result state rather than hanging."""
    can_report_page.safe_click(can_report_page.generate_button)
    result = can_report_page.result_table.or_(can_report_page.no_data_text)
    result.first.wait_for(state="visible", timeout=30000)
    assert can_report_page.has_results_table() or can_report_page.has_no_data_message(), (
        "Generate Report with nothing selected did not settle into a table or no-data state"
    )


@pytest.mark.negative
@pytest.mark.can
def test_can_report_neg_002_units_has_no_options_until_protocol_selected(can_report_page):
    """Confirmed live: Units/Devices stays enabled without a Protocol
    selected (not disabled) -- but should offer no real units to pick
    before a Protocol is chosen."""
    can_report_page.open_units_dropdown()
    # Scoped to the just-opened overlay panel -- a page-wide
    # get_by_role("option") also matches the unrelated, always-present
    # Language selector's options (confirmed live).
    panel = can_report_page.page.locator(".cdk-overlay-pane").last
    options = panel.get_by_role("option")
    real_options = [
        options.nth(i).inner_text().strip()
        for i in range(options.count())
        if options.nth(i).inner_text().strip() and not options.nth(i).inner_text().strip().startswith("Select")
    ]
    can_report_page.page.keyboard.press("Escape")
    assert not real_options, (
        f"Units/Devices offered selectable options before any Protocol was chosen: {real_options}"
    )
