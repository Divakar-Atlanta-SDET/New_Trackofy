import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_045_046_047_forward_navigation_reaches_each_step(administrator_page):
    """ADM-045/046/047: Valid data at each step advances the wizard through
    Step 1 -> 2 -> 3 -> 4."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        assert "Menu access" in admin.wizard_dialog().inner_text() or "STEP 2" in admin.wizard_dialog().inner_text()

        admin.select_menu_group("example21")
        admin.click_next_step()
        assert "General permission" in admin.wizard_dialog().inner_text()

        admin.click_next_step()
        assert "Unit permission" in admin.wizard_dialog().inner_text()
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_048_049_050_back_chain_preserves_all_state(administrator_page):
    """ADM-048/049/050: Navigating Back from Step 4 all the way to Step 1
    preserves every prior selection at each step -- the revoked General
    Permission category, the selected Menu Group, and the Step 1 fields
    (username) all survive the full back-chain."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        admin.click_next_step()
        admin.expand_permission_category("Driver")
        driver_checkbox = admin.permission_category_checkbox("Driver")
        was_checked = admin.is_checkbox_checked(driver_checkbox)
        driver_checkbox.click()
        admin.page.wait_for_timeout(500)
        toggled_state = admin.is_checkbox_checked(driver_checkbox)
        assert toggled_state != was_checked, "Clicking the Driver category checkbox should toggle its state"
        admin.click_next_step()
        assert "Unit permission" in admin.wizard_dialog().inner_text(), "Expected to reach Step 4"

        admin.click_back()  # 4 -> 3
        admin.page.wait_for_timeout(1000)
        assert admin.is_checkbox_checked(admin.permission_category_checkbox("Driver")) == toggled_state, (
            "Driver permission's toggled state should survive Step 4 -> 3 navigation"
        )

        admin.click_back()  # 3 -> 2
        admin.page.wait_for_timeout(800)
        assert "example21" in admin.wizard_dialog().inner_text(), (
            "Selected menu group should survive Step 3 -> 2 navigation"
        )

        admin.click_back()  # 2 -> 1
        admin.page.wait_for_timeout(800)
        assert admin.username_input().input_value() == username, (
            "Username should survive Step 2 -> 1 navigation"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_052_no_cancel_button_past_step1_only_close_icon(administrator_page):
    """ADM-052: Confirmed live -- "Cancel" only exists on Step 1. Every
    later step (confirmed on Step 3) offers only "Back" and "Next Step";
    the X close icon is the only way to abandon the wizard from there.
    Per Bug #25 (Bug_Report.md), the user record was already persisted at
    the Step 1->2 transition regardless -- this test verifies the close
    icon's own behavior (closes cleanly, no error, no double-create), not
    that no user exists (that's the separate, already-pinned Bug #25)."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        admin.click_next_step()

        dialog_text = admin.wizard_dialog().inner_text()
        assert "Cancel" not in dialog_text, (
            f"Expected no 'Cancel' button on Step 3 (confirmed live it only exists on Step 1): {dialog_text!r}"
        )
        assert "Back" in dialog_text and "Next Step" in dialog_text

        admin.close_wizard()
        admin.page.wait_for_timeout(1000)
        assert not admin.wizard_dialog().is_visible(), "The X close icon should close the wizard cleanly from Step 3"
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_056_double_click_submit_creates_only_one_user(administrator_page):
    """ADM-056: Rapidly double-clicking Submit creates only one user, not
    two."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    before_count = int(admin.user_count_text() or "0")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        admin.click_next_step()
        admin.click_next_step()
        admin.open_units_dropdown()
        admin.select_unit("HP12G9691")
        admin.close_units_dropdown()
        admin.page.wait_for_timeout(500)

        submit_btn = admin.wizard_dialog().get_by_role("button", name="Submit")
        submit_btn.click()
        try:
            submit_btn.click(timeout=2000)
        except Exception:
            pass  # expected once the dialog closes after the first click registers
        admin.page.wait_for_timeout(2000)

        admin.page.reload()
        admin.wait_until_ready()
        admin.page.wait_for_timeout(1000)
        after_count = int(admin.user_count_text() or "0")
        assert after_count == before_count + 1, (
            f"Double-clicking Submit should create exactly 1 user, not more -- expected "
            f"{before_count + 1}, got {after_count}"
        )
    finally:
        _delete_if_exists(admin, username)
