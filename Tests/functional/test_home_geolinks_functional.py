import pytest
from uuid import uuid4


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
    title = f"pytest-home-geolink-{uuid4().hex[:8]}"

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
def test_home_0261_map_only_geolink_does_not_expose_vehicle_details(home_page, browser, config):
    """HOME-0261: a Map-only link must not expose restricted identifying
    details to an anonymous visitor. Regression for Bug #23."""
    home_page.open_geolinks()
    title = f"pytest-home-security-{uuid4().hex[:8]}"
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
            assert "Verifying geolink" not in anon_body, "Public link never finished loading"
            if vehicle_id in anon_body:
                anon_page.screenshot(path="Tests/home_geolink_access_astra.png", full_page=True)
            assert vehicle_id not in anon_body, "Map-only GeoLink exposes a restricted vehicle identifier"
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


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("days,hours,valid", [(0,1,True),(1,0,True),(2,0,True),(2,1,False),(3,0,False),(-1,1,False),(0,-1,False)])
def test_home_0246_0251_geolink_expiry_boundaries(home_page, days, hours, valid):
    """Validate 1/24/48-hour and invalid expiry boundaries without creating a link."""
    vehicle = home_page.visible_vehicle_ids()[0]
    home_page.open_geolinks()
    home_page.click_create_geolink()
    try:
        home_page.fill_geolink_share_name("pytest-expiry-validation")
        home_page.select_geolink_vehicle(vehicle)
        home_page.fill_geolink_expiry(days, hours)
        home_page.page.keyboard.press("Tab")
        home_page.page.wait_for_timeout(300)
        assert home_page.geolink_expiry_is_valid() == valid, f"Unexpected validity for {days} days + {hours} hours"
    finally:
        home_page.cancel_geolink_form()
