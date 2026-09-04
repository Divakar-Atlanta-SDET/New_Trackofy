import pytest


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0311_xss_payload_in_search_is_not_executed(home_page):
    """HOME-0311 (data quality/security): An XSS payload typed into the
    Fleet search box is neither executed nor breaks the page -- it's just
    treated as a (non-matching) search string."""
    home_page.open_fleet_tab()
    payload = "<script>window.__xss_fired=true</script>"
    home_page.search(payload)
    home_page.page.wait_for_timeout(1000)
    fired = home_page.page.evaluate("() => window.__xss_fired === true")
    assert not fired, "XSS payload in the search box should not execute as script"
    assert home_page.fleet_result_count() == 0, "Nonsense/payload search text should just show 0 results"
    home_page.clear_search()


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0312_xss_payload_in_geolink_name_is_escaped(home_page):
    """HOME-0312 (data quality/security): An XSS payload used as a GeoLink
    share name is not executed and is rendered as literal escaped text in
    the list, not live markup."""
    home_page.open_geolinks()
    payload = "<img src=x onerror=window.__xss_fired=true>"

    try:
        home_page.click_create_geolink()
        home_page.fill_geolink_share_name(payload)
        vehicle_id = home_page.visible_vehicle_ids(max_count=1)[0]
        home_page.select_geolink_vehicle(vehicle_id)
        home_page.select_geolink_access("Map only")
        home_page.submit_geolink_form()
        home_page.page.wait_for_timeout(1000)
        home_page.cancel_geolink_share_panel()
        home_page.page.wait_for_timeout(1000)

        fired = home_page.page.evaluate("() => window.__xss_fired === true")
        assert not fired, "XSS payload in the GeoLink share name should not execute as script"
        assert payload in home_page.geolinks_dialog().inner_text(), (
            "The payload should appear as literal escaped text in the GeoLinks list"
        )
    finally:
        row = home_page.geolinks_dialog().locator("tr, [role='row']").filter(has_text="img")
        if row.count() > 0:
            row.first.locator("mat-icon", has_text="delete_outline").click()
            home_page.wait_for_loading_to_finish()
            confirm_dialog = home_page.page.locator(".cdk-overlay-container").last
            confirm_dialog.get_by_role("button", name="Delete", exact=True).click()
            home_page.wait_for_loading_to_finish()
