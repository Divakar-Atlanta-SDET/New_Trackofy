import pytest
from playwright.sync_api import expect


def _confirm_save_disabled(route_page):
    """Reverified live (2026-09-13): this form now validates via a disabled
    Save Route button, not submit-then-reject -- confirmed for missing
    name, missing origin, and missing destination alike. Superseded
    the older submit-and-check-for-rejection assumption, which is stale."""
    expect(route_page.save_btn).to_be_disabled()


@pytest.mark.negative
def test_set_157_route_name_not_actually_enforced(route_page):
    """SET-157: Regression pin for Bug_Report.md #13. Reverified live
    (2026-09-13): this is now FIXED -- Save Route stays disabled when the
    route name is blank (previously it silently saved with a defaulted
    "My Route" name). Confirmed 3x live prior to updating this test.
    """
    route_page.open_create_route()
    route_page.pick_location(route_page.origin_input, "Noida")
    route_page.pick_location(route_page.destination_input, "Delhi")
    route_page.page.wait_for_timeout(500)
    _confirm_save_disabled(route_page)
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_158_start_location_mandatory(route_page):
    """SET-158: attempting to save without a start location is rejected."""
    route_page.open_create_route()
    route_page.name_input.fill("NoOriginRoute")
    route_page.pick_location(route_page.destination_input, "Delhi")
    route_page.page.wait_for_timeout(500)
    _confirm_save_disabled(route_page)
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_159_destination_mandatory(route_page):
    """SET-159: attempting to save without a destination is rejected."""
    route_page.open_create_route()
    route_page.name_input.fill("NoDestRoute")
    route_page.pick_location(route_page.origin_input, "Noida")
    route_page.page.wait_for_timeout(500)
    _confirm_save_disabled(route_page)
    route_page.cancel_create_route()


@pytest.mark.negative
def test_set_168_custom_route_requires_drawn_path(route_page):
    """SET-168: on the Custom Route tab, source/destination are read-only
    fields only populated by drawing on the map (confirmed live: real
    input HTML carries readonly + placeholder "Draw the route to select
    source") -- a name alone, with no manually drawn path, is not enough
    for a successful save.

    Reverified live (2026-09-13): unlike the main Create Route tab, this
    tab's own Save Route button (form="customRouteForm") is NOT disabled
    client-side when source/destination are empty -- it validates via a
    submit-then-reject toast ("name, source, and destination are required")
    instead. End result is correct (no route is created, confirmed 3x live:
    URL stays on create-route, no new row appears), just an inconsistent
    validation UX vs. the other tab's disabled-button pattern -- not a
    functional bug, so this asserts the rejection instead of a disabled
    button."""
    route_page.open_create_route()
    route_page.open_custom_route_tab()
    expect(route_page.custom_source_input).to_have_attribute("readonly", "true")
    expect(route_page.custom_destination_input).to_have_attribute("readonly", "true")
    route_page.name_input.fill("CustomRouteNoPathTest")
    route_page.page.wait_for_timeout(500)
    expect(route_page.save_btn).to_be_enabled()
    route_page.save_btn.click()
    route_page.page.wait_for_timeout(1500)
    toast_text = route_page.page.locator("app-toast").inner_text()
    assert "required" in toast_text.lower(), (
        f"expected a rejection toast for the missing source/destination, got: {toast_text!r}"
    )
    assert route_page.is_on_path("/settings/route/create-route"), (
        "expected the rejected submit to leave the user on the create-route form, not navigate away"
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
