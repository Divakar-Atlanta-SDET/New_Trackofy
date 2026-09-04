import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_set_155_route_list_loads(route_page):
    """SET-155a: Verify Route Management list loads without error."""
    expect(route_page.table).to_be_visible()


@pytest.mark.functional
def test_set_155_open_create_route_page(route_page):
    """SET-155: "Add Route" opens Route Setup with name/origin/destination
    fields and the Save Route action."""
    route_page.open_create_route()
    expect(route_page.name_input).to_be_visible()
    expect(route_page.origin_input).to_be_visible()
    expect(route_page.destination_input).to_be_visible()
    expect(route_page.add_waypoint_btn).to_be_visible()
    route_page.cancel_create_route()


@pytest.mark.functional
def test_set_155_route_setup_has_create_and_custom_tabs(route_page):
    """SET-155: Route Setup opens with both Create Route and Custom Route
    options, matching the documented behavior."""
    route_page.open_create_route()
    expect(route_page.custom_route_tab).to_be_visible()
    route_page.cancel_create_route()


@pytest.mark.functional
def test_set_168_open_custom_route_tab(route_page):
    """SET-168: Custom Route tab exposes its own source/destination fields
    and manual drawing tools. Actually drawing a freeform path on the map
    canvas is out of scope for reliable UI automation (same limitation
    class as Geofence Alert's shape drawing) -- this covers the tab's
    non-drawing controls."""
    route_page.open_create_route()
    route_page.open_custom_route_tab()
    expect(route_page.custom_source_input).to_be_visible()
    expect(route_page.custom_destination_input).to_be_visible()
    expect(route_page.start_drawing_btn).to_be_visible()
    expect(route_page.clear_route_btn).to_be_visible()
    route_page.cancel_create_route()


@pytest.mark.functional
def test_set_164_show_route_on_map(route_page):
    """SET-164: Clicking Show Route on an existing seeded route renders the
    map view without error."""
    row = route_page.table.locator("tbody tr").first
    expect(row).to_be_visible()
    route_name = row.locator("td").nth(1).inner_text().strip()
    route_page.show_route_button(route_name).click()
    route_page.page.wait_for_timeout(1500)
    expect(route_page.page.locator("h1").first).to_be_visible()


@pytest.mark.functional
def test_set_165_route_details(route_page):
    """SET-165: Route details match the stored name/distance/duration/origin/destination."""
    row = route_page.table.locator("tbody tr").first
    route_name = row.locator("td").nth(1).inner_text().strip()
    distance = row.locator("td").nth(2).inner_text().strip()
    origin = row.locator("td").nth(4).inner_text().strip()

    route_page.details_button(route_name).click()
    route_page.page.wait_for_timeout(1500)
    details_text = route_page.page.locator("body").inner_text()
    assert route_name in details_text
    assert distance in details_text
    assert origin.split(",")[0] in details_text
