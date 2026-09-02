import re
import pytest
from playwright.sync_api import expect


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_tc008_alert_api_failure(unit_settings):
    """TC-008: Negative - Intercept alert API request failure and check error handling."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.page.route(
        "**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error")
    )
    unit_settings_page.switch_tab("Alert")
    unit_settings_page.page.wait_for_timeout(1500)
    # The tab must not silently show stale/false alert data as current.
    assert not unit_settings_page.alert_rows.first.is_visible() or unit_settings_page.contains_any_text(
        ["error", "failed", "unable", "something went wrong"]
    )


@pytest.mark.negative
@pytest.mark.allow_server_error
def test_tc016_handle_settings_api_failure(unit_settings):
    """TC-016: Negative - Intercept the General tab's settings update API request failure."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    original_value = unit_settings_page.speed_limit_spin.input_value()

    unit_settings_page.page.route(
        "**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error")
    )
    unit_settings_page.speed_limit_spin.fill("55")
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
    unit_settings_page.page.wait_for_timeout(1500)

    unit_settings_page.page.unroute("**/api/**")
    unit_settings_page.page.reload()
    unit_page.wait_for_unit_page_ready()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    unit_settings_page.switch_tab("General")
    assert unit_settings_page.speed_limit_spin.input_value() == original_value, (
        "A failed update must not falsely persist the new value"
    )


@pytest.mark.negative
def test_tc028_verify_failed_update_notification(unit_settings):
    """TC-028: Negative - Trigger a validation failure (invalid Speed Limit) and assert no false success."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.fill("-10")
    unit_settings_page.speed_limit_spin.press("Tab")
    unit_settings_page.page.wait_for_timeout(500)
    assert not unit_settings_page.update_btn.is_enabled() or unit_settings_page.has_validation_error(), (
        "Invalid input must block Update or show a validation error, not silently succeed"
    )


@pytest.mark.negative
def test_tc029_expired_session_during_update(unit_settings):
    """TC-029: Negative - Update API returns 401 (expired session); client redirects to login.

    ponytail: this app's auth token lives in localStorage but the running SPA
    keeps using it from memory -- clearing localStorage without a reload does
    NOT reproduce an expired session (the update still silently succeeds), so
    the realistic way to simulate expiry is a real 401 from the API itself.
    """
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    unit_settings_page.switch_tab("General")
    page.route(
        "**/api/unit_general/update",
        lambda route: route.fulfill(status=401, body='{"message":"Unauthorized"}'),
    )
    unit_settings_page.speed_limit_spin.fill("55")
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
    page.wait_for_timeout(2500)
    assert re.search(r"login|signin|sign-in", page.url, re.I) or page.get_by_placeholder(
        "Enter username or email"
    ).is_visible(), "Session expiry during update should redirect to login, not silently continue"


@pytest.mark.negative
def test_tc070_attempt_invalid_icon_selection(unit_settings):
    """TC-070: Negative - Attempt to submit the Icon form with no icon selected; Update stays blocked."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_src = unit_settings_page.current_icon_img.get_attribute("src")
    expect(unit_settings_page.icon_update_btn).to_be_disabled()

    unit_settings_page.close_modal()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.current_icon_img).to_have_attribute("src", original_src)
