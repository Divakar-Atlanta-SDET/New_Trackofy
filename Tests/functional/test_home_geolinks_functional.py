import pytest


@pytest.mark.functional
@pytest.mark.home
def test_home_0233_geolinks_panel_opens(home_page):
    """HOME-0233: The GeoLinks panel opens from the toolbar and shows the
    account's current list (or an empty state)."""
    home_page.open_geolinks()
    assert home_page.geolinks_dialog().is_visible(), "GeoLinks panel did not open"
    assert home_page.geolinks_count() >= 0, "GeoLinks count did not parse as a number"


@pytest.mark.functional
@pytest.mark.home
def test_home_0234_create_form_shows_all_sections(home_page):
    """HOME-0234: The Create GeoLink form shows all 3 configuration
    sections: General, Schedule (with the 'Max 48 hrs' rule) and Access."""
    home_page.open_geolinks()
    home_page.click_create_geolink()
    dialog_text = home_page.geolinks_dialog().inner_text()
    for expected in [
        "General", "Share name", "Select Vehicles",
        "Schedule", "Max 48 hrs", "Start date", "Start time", "Expiry days", "Expiry hours",
        "Access", "Map only", "Map and details",
    ]:
        assert expected in dialog_text, f"Expected '{expected}' in Create GeoLink form: {dialog_text!r}"
    home_page.cancel_geolink_form()


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0235_0236_create_requires_share_name_and_vehicle(home_page):
    """HOME-0235/0236: Create is blocked until both a share name and at
    least one vehicle are selected."""
    home_page.open_geolinks()
    home_page.click_create_geolink()
    assert not home_page.geolink_create_button_enabled(), "Create should be disabled on an empty form"

    home_page.fill_geolink_share_name("validation-probe")
    assert not home_page.geolink_create_button_enabled(), (
        "Create should still be disabled with a share name but no vehicle selected"
    )

    vehicle_id = home_page.visible_vehicle_ids(max_count=1)[0]
    home_page.select_geolink_vehicle(vehicle_id)
    home_page.page.wait_for_timeout(500)
    assert home_page.geolink_create_button_enabled(), (
        "Create should become enabled once both a share name and a vehicle are set"
    )
    home_page.cancel_geolink_form()


@pytest.mark.functional
@pytest.mark.home
def test_home_0237_0245_0270_create_list_and_delete_geolink(home_page):
    """HOME-0237 (create), 0245 (appears in list), 0270 (delete) --
    full create-then-delete round trip using this suite's established
    diff-based CRUD pattern (create, assert, delete, assert restored).
    """
    home_page.open_geolinks()
    before_count = home_page.geolinks_count()
    title = "pytest-home-geolink-crud"

    try:
        home_page.click_create_geolink()
        home_page.fill_geolink_share_name(title)
        vehicle_id = home_page.visible_vehicle_ids(max_count=1)[0]
        home_page.select_geolink_vehicle(vehicle_id)
        home_page.select_geolink_access("Map only")
        home_page.submit_geolink_form()
        home_page.page.wait_for_timeout(1000)

        share_url = home_page.get_geolink_share_url()
        assert share_url, "Expected a public share URL to be shown after creating the GeoLink"
        home_page.cancel_geolink_share_panel()

        row = home_page.geolink_row(title)
        assert row.count() > 0, f"Created GeoLink '{title}' does not appear in the list"
        assert "Active" in row.first.inner_text(), f"Newly created GeoLink should show as Active: {row.first.inner_text()!r}"
        assert home_page.geolinks_count() == before_count + 1, (
            f"Expected GeoLinks count to rise by 1 (was {before_count}), got {home_page.geolinks_count()}"
        )
    finally:
        if home_page.geolink_row(title).count() > 0:
            home_page.delete_geolink(title)

    assert home_page.geolink_row(title).count() == 0, f"GeoLink '{title}' should be removed after delete"
    assert home_page.geolinks_count() == before_count, (
        f"Expected GeoLinks count restored to {before_count} after delete, got {home_page.geolinks_count()}"
    )


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0260_map_only_geolink_does_not_expose_vehicle_details(home_page, browser, config):
    """Regression pin for Bug #23 (Bug_Report.md, Home Module): a GeoLink
    created with 'Map only' access (labeled "Vehicle location without
    details") should not expose the vehicle's identifying registration
    string to an anonymous visitor of the public share URL -- but confirmed
    live that it currently does. This asserts the confirmed-broken behavior;
    it should start failing (and be flipped to assert the identifier is
    NOT present) once the app is fixed.

    Uses a genuinely fresh, unauthenticated browser context (no storage
    state / cookies from this test's own login) to visit the real public
    URL, matching how an actual recipient would open the link.
    """
    home_page.open_geolinks()
    title = "pytest-home-geolink-security"
    vehicle_id = home_page.visible_vehicle_ids(max_count=1)[0]

    try:
        home_page.click_create_geolink()
        home_page.fill_geolink_share_name(title)
        home_page.select_geolink_vehicle(vehicle_id)
        home_page.select_geolink_access("Map only")
        home_page.submit_geolink_form()
        home_page.page.wait_for_timeout(1000)
        share_url = home_page.get_geolink_share_url()
        assert share_url, "Expected a public share URL after creating the GeoLink"
        home_page.cancel_geolink_share_panel()

        anon_context = browser.new_context(base_url=config["base_url"])
        anon_page = anon_context.new_page()
        try:
            anon_page.goto(share_url)
            anon_page.wait_for_timeout(2000)
            # The public page shows a "Verifying geolink..." loading state
            # before vehicle data is ready -- wait it out rather than
            # reading the page mid-load.
            for _ in range(10):
                if "Verifying geolink" not in anon_page.locator("body").inner_text():
                    break
                anon_page.wait_for_timeout(1000)
            anon_body = anon_page.locator("body").inner_text()
            assert vehicle_id in anon_body, (
                "Bug #23: a 'Map only' GeoLink should currently (still) expose the vehicle "
                f"identifier '{vehicle_id}' to an anonymous visitor -- it was NOT found on the "
                "public page. If this is no longer present, the bug is fixed and this test "
                "should be flipped to assert the identifier is absent instead."
            )
        finally:
            anon_context.close()
    finally:
        # The GeoLinks panel is very likely still open from the steps
        # above (cancel_geolink_share_panel() returns to the list view
        # within the same panel, it doesn't close it) -- only (re)open it
        # if it isn't already visible.
        if not home_page.geolinks_dialog().is_visible():
            home_page.open_geolinks()
        if home_page.geolink_row(title).count() > 0:
            home_page.delete_geolink(title)
