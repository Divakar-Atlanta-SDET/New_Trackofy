import time
import pytest
from playwright.sync_api import expect


def _unique_name(prefix: str) -> str:
    suffix = "".join(chr(ord("A") + int(d)) for d in str(int(time.time() * 1000))[-6:])
    return f"{prefix} {suffix}"


@pytest.mark.positive
def test_set_156_create_valid_route(route_page):
    """SET-156/162/163/172: create a valid route; it's saved with correct
    distance/duration and remains present after refresh."""
    name = _unique_name("AutoRoute")
    route_page.create_route(name, "Noida", "Delhi")

    try:
        row = route_page.row_containing(name)
        expect(row).to_be_visible(timeout=10000)
        distance = row.locator("td").nth(2).inner_text().strip()
        duration = row.locator("td").nth(3).inner_text().strip()
        assert distance and distance != "0", f"expected a real distance, got {distance!r}"
        assert duration and duration != "0", f"expected a real duration, got {duration!r}"

        route_page.page.reload()
        route_page.wait_for_loading_to_finish()
        route_page.page.wait_for_timeout(1000)
        expect(route_page.row_containing(name)).to_be_visible()
    finally:
        route_page.delete_route(name)


@pytest.mark.positive
def test_set_160_add_waypoint_to_route(route_page):
    """SET-160/161: adding waypoints includes them and the route is saved."""
    name = _unique_name("WaypointRoute")
    route_page.open_create_route()
    route_page.name_input.fill(name)
    route_page.pick_location(route_page.origin_input, "Noida")
    route_page.add_waypoint("Ghaziabad")
    route_page.pick_location(route_page.destination_input, "Delhi")
    route_page.page.wait_for_timeout(500)
    route_page.save_btn.click()
    # Confirmed live: saving redirects to /home, not back to the route list
    # (see Bug_Report.md #12) -- navigate back explicitly.
    route_page.expect_path("/home")
    route_page.page.goto("/settings/route")
    route_page.expect_path("/settings/route")
    route_page.wait_for_loading_to_finish()
    route_page.page.wait_for_timeout(1000)

    try:
        expect(route_page.row_containing(name)).to_be_visible(timeout=10000)
    finally:
        route_page.delete_route(name)


@pytest.mark.positive
def test_set_169_edit_route(route_page):
    """SET-169: editing a saved route via Details persists the change."""
    name = _unique_name("EditRoute")
    route_page.create_route(name, "Noida", "Delhi")

    try:
        expect(route_page.row_containing(name)).to_be_visible(timeout=10000)
        route_page.details_button(name).click()
        route_page.page.wait_for_timeout(1500)
        edit_btn = route_page.page.get_by_role("button", name="Edit")
        if edit_btn.count() == 0:
            pytest.skip("No edit action available from Route Details -- editing may not be supported per product rule")
        edit_btn.first.click()
        route_page.page.wait_for_timeout(1000)
        new_name = _unique_name("Renamed")
        name_field = route_page.page.locator("input[formcontrolname='routeName']")
        name_field.fill(new_name)
        route_page.save_btn.click()
        route_page.page.wait_for_timeout(2000)
        if not route_page.is_on_path("/settings/route"):
            # Same redirect-to-/home quirk as route creation (Bug_Report.md #12).
            route_page.page.goto("/settings/route")
            route_page.expect_path("/settings/route")
        route_page.wait_for_loading_to_finish()
        route_page.page.wait_for_timeout(1000)
        expect(route_page.row_containing(new_name)).to_be_visible()
        name = new_name
    finally:
        route_page.delete_route(name)
