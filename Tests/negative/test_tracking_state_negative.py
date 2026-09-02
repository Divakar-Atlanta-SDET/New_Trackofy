import re
import pytest
from playwright.sync_api import expect


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_trk_state_007_session_expiry_during_live_tracking(tracking):
    """TRK-STATE-007: Negative - API returns 401 (expired session) during Live Tracking; auth flow triggers.

    Ponytail lesson from the Unit module work: this app's auth token lives in
    localStorage and the running SPA keeps using it from memory, so clearing
    cookies does NOT reproduce an expired session -- a real 401 from the API
    is the only reliable way to simulate it.
    """
    page = tracking.page
    page.route("**/api/**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}'))
    page.route(
        "**/trackofy_api_new/**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}')
    )
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    tracking.start_tracking_btn.click()
    page.wait_for_timeout(3000)
    assert re.search(r"login|signin|sign-in", page.url, re.I) or page.get_by_placeholder(
        "Enter username or email"
    ).is_visible(), "A 401 during live tracking should trigger the auth flow, not continue silently"


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_trk_state_008_session_expiry_during_playback_load(tracking):
    """TRK-STATE-008: Negative - API returns 401 (expired session) while loading Playback."""
    page = tracking.page
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)

    page.route("**/api/**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}'))
    page.route(
        "**/trackofy_api_new/**", lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}')
    )
    if tracking.load_playback_btn.is_enabled():
        tracking.load_playback_btn.click()
    page.wait_for_timeout(3000)
    assert re.search(r"login|signin|sign-in", page.url, re.I) or page.get_by_placeholder(
        "Enter username or email"
    ).is_visible(), "A 401 during playback load should trigger the auth flow, not continue silently"
