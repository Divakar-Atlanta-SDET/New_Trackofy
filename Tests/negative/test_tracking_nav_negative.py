import pytest
from playwright.sync_api import expect


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_trk_nav_009_initial_tracking_load_failure(authenticated_page):
    """TRK-NAV-009: Negative - Intercept initial tracking config API failure; no false tracking state."""
    from Pages.tracking_page import TrackingPage

    page = authenticated_page
    page.route("**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    tracking_page = TrackingPage(page)
    tracking_page.page.goto("/tracking")
    page.wait_for_timeout(2500)
    # The page must not silently claim a working tracking state after every API call fails.
    assert not tracking_page.start_tracking_btn.is_enabled() or tracking_page.contains_any_text(
        ["error", "failed", "unable", "something went wrong", "retry"]
    )
