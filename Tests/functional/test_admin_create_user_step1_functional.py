import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    """Best-effort cleanup: Step 1 -> Next Step already persists the user
    server-side (Bug #25, Bug_Report.md), so any test that reaches that
    point leaves a real orphan account behind unless explicitly deleted."""
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(800)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_022_023_open_wizard_shows_four_step_progress(administrator_page):
    """ADM-022/023: Add User opens the 4-step Create User wizard with all
    step labels visible."""
    admin = administrator_page
    admin.open_add_user_wizard()
    dialog_text = admin.wizard_dialog().inner_text()
    for step in ["Personal info", "Menu access", "General permission", "Unit permission"]:
        assert step in dialog_text, f"Expected step label '{step}' in wizard: {dialog_text!r}"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_024_233_username_required_blocks_progression(administrator_page):
    """ADM-024/233: Leaving username blank (with other fields valid) blocks
    Next Step."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.password_input().fill("ValidPassword123@")
    admin.confirm_password_input().fill("ValidPassword123@")
    admin.select_arm_disarm("No")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert not next_btn.is_enabled(), "Next Step should be disabled with an empty username"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_025_valid_username_accepted(administrator_page):
    """ADM-025: A valid, unique username is accepted and lets the wizard
    proceed to Step 2."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        assert "STEP 2" in admin.wizard_dialog().inner_text() or "check" in admin.wizard_dialog().inner_text(), (
            "Expected the wizard to advance past Step 1 with a valid username"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_026_duplicate_username_rejected(administrator_page):
    """ADM-026: An existing username is rejected server-side (with a clear
    error) when Next Step is clicked, and the wizard stays on Step 1 --
    confirmed live this is enforced server-side, not blocked client-side
    (the button itself stays enabled for a duplicate value)."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.fill_step1("bruce", "ValidPassword123@", ["HP12G9691"], "No")
    admin.click_next_step()
    admin.page.wait_for_timeout(1000)
    toast = admin.wizard_error_toast_text()
    assert toast, "Expected an error toast when submitting a duplicate username"
    assert "STEP 1" in admin.wizard_dialog().inner_text() or "Personal info" in admin.wizard_dialog().inner_text(), (
        "Wizard should remain on Step 1 after a duplicate-username rejection"
    )
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
@pytest.mark.parametrize("common_word", ["test", "admin", "demo"])
def test_adm_bug32_common_username_falsely_rejected_as_duplicate(administrator_page, common_word):
    """Regression pin for Bug #32 (Bug_Report.md, Administrator Module):
    reported directly by the user -- common words like "test"/"admin"/
    "demo" are rejected with the same 'user_alread_exist' error as a real
    same-account duplicate, even though this account's only real user is
    "bruce" (confirmed live via a full list read). This indicates username
    uniqueness is checked globally across the platform, not scoped to this
    account, with a misleading error message. Asserts the confirmed-broken
    (misleading) behavior; it should start failing -- and be flipped --
    once the error message is fixed to clarify the check is global, or the
    check is scoped per-account."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.fill_step1(common_word, "ValidPassword123@", ["HP12G9691"], "No")
    admin.click_next_step()
    admin.page.wait_for_timeout(1000)
    toast = admin.wizard_error_toast_text()
    assert "user_alread_exist" in toast or "already exist" in toast.lower(), (
        f"Bug #32: '{common_word}' should currently (still) be falsely rejected as an 'already exists' "
        f"duplicate despite not existing in this account. If it's now accepted, or the error message "
        f"has been clarified, this test should be flipped/updated. Got toast: {toast!r}"
    )
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_bug33_no_password_visibility_toggle_in_wizard(administrator_page):
    """Regression pin for Bug #33 (Bug_Report.md, Administrator Module,
    Low priority): reported directly by the user -- the Password and
    Confirm Password fields on Step 1 have no show/hide (eye) toggle,
    unlike the User Management table's own "Show password" reveal button.
    Confirmed live: both fields stay plain type="password" inputs with no
    visibility-toggle button anywhere in their container. This asserts the
    confirmed-missing behavior; it should start failing -- and be flipped
    to assert a toggle IS present and works -- once the app adds one.
    """
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.password_input().fill("SomePassword123@")
    admin.confirm_password_input().fill("SomePassword123@")
    admin.page.wait_for_timeout(500)

    assert admin.password_input().get_attribute("type") == "password", (
        "Bug #33: the Password field should currently (still) have no way to reveal it (stays "
        "type='password' with no toggle button nearby). If a visibility toggle now exists and "
        "changes this to type='text' on click, this test should be flipped/updated."
    )
    assert admin.confirm_password_input().get_attribute("type") == "password"

    dialog = admin.wizard_dialog()
    visibility_buttons = dialog.locator("button[aria-label*='assword' i], button[aria-label*='visib' i]")
    assert visibility_buttons.count() == 0, (
        f"Bug #33: expected no password-visibility-toggle button in the wizard, found "
        f"{visibility_buttons.count()}. If this now finds one, the app has been fixed."
    )
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_030_password_required_blocks_progression(administrator_page):
    """ADM-030: Leaving password blank blocks Next Step."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(_unique_username("pytestqa"))
    admin.confirm_password_input().fill("")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert not next_btn.is_enabled(), "Next Step should be disabled with an empty password"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_031_confirm_password_required_blocks_progression(administrator_page):
    """ADM-031: Leaving confirm password blank (with a real password
    entered) blocks Next Step."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(_unique_username("pytestqa"))
    admin.password_input().fill("ValidPassword123@")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert not next_btn.is_enabled(), "Next Step should be disabled with an empty confirm-password"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_033_mismatched_password_blocks_progression(administrator_page):
    """ADM-033: A confirm-password value that doesn't match Password
    blocks Next Step.

    Confirmed live: no explicit "passwords don't match" text renders
    anywhere in the dialog (checked both immediately and after blurring
    the field) -- the app only communicates this by leaving Next Step
    disabled, contradicting the CSV's own expectation of a visible
    mismatch message. Asserting the confirmed actual behavior (silently
    disabled) rather than a message that doesn't exist.
    """
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(_unique_username("pytestqa"))
    admin.password_input().fill("Password123@")
    admin.confirm_password_input().fill("DifferentPassword456@")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert not next_btn.is_enabled(), "Next Step should be disabled when passwords don't match"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_032_034_matching_password_accepted_and_masked(administrator_page):
    """ADM-032/034: Matching password/confirm values are accepted, and
    both fields render as masked (type=password)."""
    admin = administrator_page
    admin.open_add_user_wizard()
    assert admin.password_input().get_attribute("type") == "password", "Password field should be masked"
    assert admin.confirm_password_input().get_attribute("type") == "password", (
        "Confirm password field should be masked"
    )
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(_unique_username("pytestqa"))
    admin.password_input().fill("ValidPassword123@")
    admin.confirm_password_input().fill("ValidPassword123@")
    admin.select_arm_disarm("No")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert next_btn.is_enabled(), "Next Step should be enabled with matching, policy-valid passwords"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_035_password_policy_requires_at_symbol(administrator_page):
    """ADM-035 (real policy discovered live): the password policy
    specifically requires the literal '@' character, not just any special
    character -- a password without '@' (e.g. with '!') is rejected even
    though it otherwise meets length/case/number rules."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(_unique_username("pytestqa"))
    admin.password_input().fill("ValidPassword123!")
    admin.confirm_password_input().fill("ValidPassword123!")
    admin.page.wait_for_timeout(500)
    next_btn = admin.wizard_dialog().get_by_role("button", name="Next Step")
    assert not next_btn.is_enabled(), (
        "Expected a password using '!' instead of '@' to be rejected by the real password policy"
    )
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_036_037_038_select_multiple_vehicles_and_remove_one(administrator_page):
    """ADM-036/037/038: One or more vehicles can be selected, and removing
    a selected vehicle (via toggling it again) works correctly."""
    admin = administrator_page
    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.select_vehicle("wailon_fuel")
    admin.close_vehicles_dropdown()
    admin.page.wait_for_timeout(500)
    text_with_both = admin.wizard_dialog().inner_text()
    assert "HP12G9691" in text_with_both and "wailon_fuel" in text_with_both, (
        f"Expected both selected vehicles to show: {text_with_both!r}"
    )

    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")  # toggle off
    admin.close_vehicles_dropdown()
    admin.page.wait_for_timeout(500)
    text_after_removal = admin.wizard_dialog().inner_text()
    assert "wailon_fuel" in text_after_removal, "Expected the remaining vehicle to still show"
    assert "HP12G9691" not in text_after_removal, "Removed vehicle should no longer show as selected"
    admin.close_wizard()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_039_040_041_042_arm_disarm_and_state_persist_across_navigation(administrator_page):
    """ADM-039/040/041/042: Vehicle selection and Arm/Disarm choice both
    persist correctly when navigating forward to Step 2 and back to
    Step 1."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.open_vehicles_dropdown()
        admin.select_vehicle("wailon_fuel")
        admin.close_vehicles_dropdown()
        admin.username_input().fill(username)
        admin.password_input().fill("ValidPassword123@")
        admin.confirm_password_input().fill("ValidPassword123@")
        admin.select_arm_disarm("Yes")
        admin.click_next_step()
        admin.page.wait_for_timeout(1000)
        admin.click_back()
        admin.page.wait_for_timeout(1000)

        assert admin.username_input().input_value() == username, "Username should persist after Back"
        assert admin.arm_disarm_radio("Yes").is_checked(), "Arm/Disarm 'Yes' should persist after Back"
        assert "wailon_fuel" in admin.wizard_dialog().inner_text(), "Vehicle selection should persist after Back"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_051_cancel_from_step1_creates_no_user(administrator_page):
    """ADM-051: Cancelling from Step 1 (before any Next Step click, so
    before the server-side save happens) creates no user at all."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    before_count = int(admin.user_count_text() or "0")

    admin.open_add_user_wizard()
    admin.open_vehicles_dropdown()
    admin.select_vehicle("HP12G9691")
    admin.close_vehicles_dropdown()
    admin.username_input().fill(username)
    admin.password_input().fill("ValidPassword123@")
    admin.confirm_password_input().fill("ValidPassword123@")
    admin.select_arm_disarm("No")
    admin.cancel_wizard()
    admin.page.wait_for_timeout(1000)

    admin.page.reload()
    admin.wait_until_ready()
    admin.page.wait_for_timeout(1000)
    after_count = int(admin.user_count_text() or "0")
    assert after_count == before_count, (
        f"Cancelling before Step 1's Next Step should create no user -- expected {before_count}, got {after_count}"
    )
    assert admin.user_row(username).count() == 0, f"'{username}' should not exist after cancelling Step 1"
