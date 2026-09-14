import pytest


@pytest.mark.edgecase
@pytest.mark.can
def test_can_alerts_edge_001_protocol_filter_with_no_matching_alerts_shows_empty_state(can_alerts_page):
    """Fixed 2026-09-14: this test had its own inline duplicate of the
    same broken get_by_role("option")/get_by_role("combobox") pattern
    already fixed elsewhere in the page object (see CanBasePage.
    custom_option()/combobox_by_visible_label()) -- routed through those
    instead of re-declaring raw locators here."""
    can_alerts_page.open_apply_filter()
    drawer = can_alerts_page.filter_drawer()
    can_alerts_page.safe_click(can_alerts_page.combobox_by_visible_label("Protocol", container=drawer))
    options = can_alerts_page.custom_option()
    if options.count() == 0:
        pytest.skip("No protocol options available to filter by")
    last_protocol = options.last.inner_text()
    can_alerts_page.safe_click(options.last)
    can_alerts_page.safe_click(can_alerts_page.apply_filter_submit_button(drawer))
    can_alerts_page.wait_for_loading_to_finish()

    if can_alerts_page.row_count() == 0:
        assert can_alerts_page.contains_any_text(["No data", "No results", "No records found"]), (
            f"Protocol filter ({last_protocol}) returned zero rows with no empty-state message"
        )


@pytest.mark.edgecase
@pytest.mark.can
def test_can_alerts_edge_002_reset_filters_restores_full_alert_count(can_alerts_page):
    total_before = can_alerts_page.total_alert_count()
    can_alerts_page.filter_by_level("Critical")
    filtered_total = can_alerts_page.pagination_total()
    assert filtered_total <= total_before

    can_alerts_page.open_apply_filter()
    can_alerts_page.reset_filters()
    can_alerts_page.wait_for_loading_to_finish()
    restored_total = can_alerts_page.pagination_total()
    assert restored_total == total_before, (
        f"Reset did not restore the full alert count: before={total_before}, after_reset={restored_total}"
    )


@pytest.mark.edgecase
@pytest.mark.can
def test_can_alerts_edge_003_last_page_pagination_reaches_final_rows(can_alerts_page):
    can_alerts_page.click_last_page()
    assert not can_alerts_page.page.get_by_role("button", name="Next page").is_enabled(), (
        "Next page is still enabled after navigating to the last page"
    )
