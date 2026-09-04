import pytest
from playwright.sync_api import expect


def _attempt_save_and_confirm_rejected(route_page):
    """Save Route is always enabled (confirmed live -- this form validates
    on submit attempt, not via a disabled button); clicking it with
    incomplete data must not navigate away or show a success toast."""
    route_page.save_btn.click()
    route_page.page.wait_for_timeout(1500)
    assert route_page.is_on_path("/settings/route/create-route"), (
        "expected to stay on the create-route page after an incomplete submit"
    )
    toast = route_page.page.locator("app-toast")
    if toast.count() > 0 and toast.is_visible():
        assert "success" not in toast.inner_text().lower()


@pytest.mark.negative
def test_set_157_route_name_not_actually_enforced(route_page):
    """SET-157: route name is documented as mandatory, but saving without
    one is NOT rejected -- confirmed live it silently defaults to "My
    Route" and the save succeeds. See Bug_Report.md #13. This documents the
    real (broken) behavior rather than asserting a rejection the app
    doesn't perform.
    """
    route_page.open_create_route()
    route_page.pick_location(route_page.origin_input, "Noida")
    route_page.pick_location(route_page.destination_input, "Delhi")
    route_page.page.wait_for_timeout(500)
    route_page.save_btn.click()
    route_page.expect_path("/home")
    route_page.page.goto("/settings/route")
    route_page.expect_path("/settings/route")
    route_page.wait_for_loading_to_finish()
    route_page.page.wait_for_timeout(1000)

    row = route_page.row_containing("My Route")
    expect(row.first).to_be_visible(timeout=10000)
    del_btn = row.first.locator("td").nth(9).locator("button")
    del_btn.click()
    route_page.wait_for_visible(route_page.confirm_delete_btn)
    route_page.page.wait_for_timeout(400)
    route_page.confirm_delete_btn.click()
    route_page.wait_for_dialog_closed()


@pytest.mark.negative
def test_set_158_start_location_mandatory(route_page):
    """SET-158: attempting to save without a start location is rejected."""
    route_page.open_create_route()
    route_page.name_input.fill("NoOriginRoute")
    route_page.pick_location(route_page.destination_input, "Delhi")
    route_page.page.wait_for_timeout(500)
    _attempt_save_and_confirm_rejected(route_page)
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_159_destination_mandatory(route_page):
    """SET-159: attempting to save without a destination is rejected."""
    route_page.open_create_route()
    route_page.name_input.fill("NoDestRoute")
    route_page.pick_location(route_page.origin_input, "Noida")
    route_page.page.wait_for_timeout(500)
    _attempt_save_and_confirm_rejected(route_page)
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_168_custom_route_requires_drawn_path(route_page):
    """SET-168: on the Custom Route tab, source/destination are read-only
    fields only populated by drawing on the map (confirmed live: real
    input HTML carries readonly + placeholder "Draw the route to select
    source") -- a name alone, with no manually drawn path, is not enough
    for a successful save."""
    route_page.open_create_route()
    route_page.open_custom_route_tab()
    expect(route_page.custom_source_input).to_have_attribute("readonly", "true")
    expect(route_page.custom_destination_input).to_have_attribute("readonly", "true")
    route_page.name_input.fill("CustomRouteNoPathTest")
    route_page.page.wait_for_timeout(500)
    route_page.save_btn.click()
    route_page.page.wait_for_timeout(1500)
    assert route_page.is_on_path("/settings/route/create-route"), (
        "expected to stay on the create-route page without a drawn path"
    )
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_171_cancel_route_deletion(route_page):
    """SET-171: cancelling a delete confirmation leaves the route intact."""
    row = route_page.table.locator("tbody tr").first
    expect(row).to_be_visible()
    route_name = row.locator("td").nth(1).inner_text().strip()

    route_page.delete_button(route_name).click()
    route_page.wait_for_visible(route_page.cancel_delete_btn)
    route_page.page.wait_for_timeout(400)
    route_page.cancel_delete_btn.click()
    route_page.wait_for_dialog_closed()
    expect(route_page.row_containing(route_name)).to_be_visible()
