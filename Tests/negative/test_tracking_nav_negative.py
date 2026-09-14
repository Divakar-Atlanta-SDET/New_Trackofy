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
    # A raw page.goto("/tracking") does not work on this app (NEW-1, see
    # retest_bug_report.md) -- use the nav-link-based open_tracking_page()
    # instead; the API-failure route above still applies to whatever calls
    # the resulting page makes, regardless of how navigation happened.
    tracking_page.open_tracking_page()
    page.wait_for_timeout(2500)
    # The page must not silently claim a working tracking state after every API call fails.
    assert not tracking_page.start_tracking_btn.is_enabled() or tracking_page.contains_any_text(
        ["error", "failed", "unable", "something went wrong", "retry"]
    )
