import time

import pytest

from Pages.login_page import LoginPage
from components.toast_notifcations import ToastNotifications


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_150_151_152_submit_creates_user_appears_once_and_count_increments(administrator_page):
    """ADM-150/151/152: Submitting a complete valid configuration creates
    the user, it appears exactly once in User Management after a reload,
    and the total user count increases by exactly one."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        before_count = int(admin.user_count_text() or "0")
        admin.create_user(username, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)

        after_count = int(admin.user_count_text() or "0")
        assert after_count == before_count + 1, (
            f"Expected user count to increase by exactly 1 -- expected {before_count + 1}, got {after_count}"
        )

        admin.search(username)
        assert admin.matching_record_count() == 1, (
            f"Expected the new user to appear exactly once, got {admin.matching_record_count()}"
        )
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_153_login_with_new_credentials_succeeds(administrator_page, browser, config):
    """ADM-153: A freshly created sub-user can log in with the credentials
    just configured, using a genuinely fresh, unauthenticated browser
    context (not the admin's own session)."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        sub_context = browser.new_context(base_url=config["base_url"])
        sub_page = sub_context.new_page()
        try:
            login_page = LoginPage(sub_page, config)
            toast = ToastNotifications(sub_page)
            login_page.open()
            login_page.login(username, password)
            sub_page.wait_for_timeout(2000)
            assert "/home" in sub_page.url, (
                f"Expected the new sub-user to reach /home after login, got {sub_page.url}"
            )
        finally:
            sub_context.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_154_wrong_password_fails(administrator_page, browser, config):
    """ADM-154: Attempting to log in as the new sub-user with the wrong
    password fails -- stays off /home."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        sub_context = browser.new_context(base_url=config["base_url"])
        sub_page = sub_context.new_page()
        try:
            login_page = LoginPage(sub_page, config)
            login_page.open()
            login_page.login(username, "WrongPassword999@")
            sub_page.wait_for_timeout(2000)
            assert "/home" not in sub_page.url, (
                f"Expected login with wrong password to fail (stay off /home), got {sub_page.url}"
            )
        finally:
            sub_context.close()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_157_create_api_failure_does_not_falsely_report_success(administrator_page):
    """ADM-157: If the create-user API call fails, the app should show an
    error and must not falsely report the user as created. Simulated via
    page.route aborting the save_subuser call at the Step 1->2 transition
    (confirmed live this is where the real create API call fires)."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        before_count = int(admin.user_count_text() or "0")
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")

        admin.page.route("**/save_subuser*", lambda route: route.abort())
        admin.wizard_dialog().get_by_role("button", name="Next Step").click()
        admin.page.wait_for_timeout(2500)
        admin.page.unroute("**/save_subuser*")

        dialog_text = admin.wizard_dialog().inner_text() if admin.wizard_dialog().count() > 0 else ""
        still_on_step1 = "STEP 1" in dialog_text and "Menu access" not in dialog_text.split("Progress")[0]
        error_shown = bool(admin.wizard_error_toast_text())
        assert error_shown or still_on_step1, (
            "Expected either a visible error or the wizard staying on Step 1 after a simulated API failure, "
            f"got dialog_text={dialog_text!r}"
        )

        admin.page.keyboard.press("Escape")
        admin.page.wait_for_timeout(500)
        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        after_count = int(admin.user_count_text() or "0")
        assert after_count == before_count, (
            f"A failed create API call must not leave a real user behind -- expected count to stay "
            f"{before_count}, got {after_count}"
        )
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_158_network_interruption_during_submit_fails_safely(administrator_page):
    """ADM-158: A network interruption during the create API call (Step
    1->2 save_subuser) must fail safely, not show a misleading success."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        before_count = int(admin.user_count_text() or "0")
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")

        admin.page.route("**/save_subuser*", lambda route: route.abort("connectionreset"))
        admin.wizard_dialog().get_by_role("button", name="Next Step").click()
        admin.page.wait_for_timeout(2500)
        admin.page.unroute("**/save_subuser*")

        admin.page.keyboard.press("Escape")
        admin.page.wait_for_timeout(500)
        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        after_count = int(admin.user_count_text() or "0")
        assert after_count == before_count, (
            f"A network interruption during create must not leave a real user behind -- expected count "
            f"to stay {before_count}, got {after_count}"
        )
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.skip(
    reason="ADM-155 (configured values match submission via Edit) is blocked by Bug #28 "
    "(Bug_Report.md, Administrator Module, CRITICAL): the Edit dialog currently opens a "
    "different, unrelated user's data regardless of which row is clicked, so it cannot be "
    "used to verify a specific user's own submitted configuration. Un-skip once Bug #28 is fixed."
)
@pytest.mark.functional
@pytest.mark.admin
def test_adm_155_configured_values_match_submission():
    pass


@pytest.mark.skip(
    reason="ADM-159 (session expiry during submit) has no reliable simulation path in this "
    "suite -- session/token expiry isn't a request-level condition page.route can abort or "
    "delay the way ADM-157/158 do, and there's no exposed way to force server-side session "
    "invalidation mid-request. Honest skip rather than a flaky/meaningless approximation, "
    "matching the REP-COM-021 precedent (Reports module)."
)
@pytest.mark.functional
@pytest.mark.admin
def test_adm_159_session_expiry_during_submit():
    pass


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_28_edit_opens_wrong_users_data(administrator_page):
    """Regression pin for Bug #28 (Bug_Report.md, Administrator Module,
    CRITICAL): clicking "Edit" on a specific, verified user row opens the
    "Edit Units" dialog for a completely different, unrelated user instead
    of the one clicked. This asserts the confirmed-broken behavior; it
    should start failing -- and be flipped to assert the dialog matches the
    clicked user -- once the app is fixed.
    """
    admin = administrator_page
    username = _unique_username("pytesteditbug")
    try:
        admin.create_user(username, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
        admin.page.wait_for_timeout(1500)

        admin.search(username)
        assert admin.matching_record_count() == 1, "Expected search to isolate exactly the new user"
        assert admin.row_username(admin.user_rows().first) == username

        admin.edit_button(username).click()
        admin.page.wait_for_timeout(1500)
        dialog_text = admin.edit_units_dialog().inner_text()
        assert username not in dialog_text, (
            f"Bug #28: Edit should currently (still) open the WRONG user's data (not '{username}'). "
            f"If this now shows the correct username, the app has been fixed and this test should be "
            f"flipped to assert the dialog matches the clicked user. Got: {dialog_text!r}"
        )
        admin.close_edit_units_dialog()
    finally:
        _delete_if_exists(admin, username)
