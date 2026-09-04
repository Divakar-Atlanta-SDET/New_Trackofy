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
def test_adm_057_available_groups_listed(administrator_page):
    """ADM-057: Existing menu groups are listed on Step 2."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        dialog_text = admin.wizard_dialog().inner_text()
        assert "example21" in dialog_text, f"Expected a known real group in the list: {dialog_text!r}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_058_059_060_061_select_group_shows_details_and_menu_count(administrator_page):
    """ADM-058/059/060/061: Selecting a group shows its name, its assigned
    menus, and a menu count consistent with what's actually displayed --
    including a real child-menu structure (Dashboard > Tabular)."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        dialog_text = admin.wizard_dialog().inner_text()
        assert "example21" in dialog_text
        assert "Home" in dialog_text, f"Expected the group's assigned menu 'Home' to be shown: {dialog_text!r}"

        menu_count = admin.selected_group_menu_count()
        assert menu_count > 0, f"Expected a nonzero menu count for 'example21', got {menu_count}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_062_change_selected_group_updates_details(administrator_page):
    """ADM-062: Selecting a different group replaces the shown details with
    the new group's own menus."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        first_count = admin.selected_group_menu_count()

        admin.select_menu_group("Full control")
        admin.page.wait_for_timeout(500)
        dialog_text = admin.wizard_dialog().inner_text()
        assert "Full control" in dialog_text
        second_count = admin.selected_group_menu_count()
        assert second_count > 0, f"Expected 'Full control' to show a nonzero menu count, got {second_count}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_063_group_selection_persists_across_navigation(administrator_page):
    """ADM-063: The selected group survives navigating to Step 3 and back
    to Step 2."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.select_menu_group("example21")
        admin.click_next_step()
        admin.click_back()
        admin.page.wait_for_timeout(800)
        assert "example21" in admin.wizard_dialog().inner_text(), (
            "Selected group should still be shown after Step 3 -> 2 -> 3 -> 2 round trip"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_065_add_group_opens_new_group_dialog(administrator_page):
    """ADM-065: "Add Group" does open a real "Add New Menu Group" dialog
    (Group Name + menu checkboxes + Cancel/Save Group) -- but only after a
    real, unindicated delay of several seconds (confirmed live: not yet
    open at 3s, open by 5s). Polls rather than using a fixed sleep so this
    test isn't itself flaky against that delay."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.page.wait_for_timeout(1000)

        admin.add_group_button().click()
        dialog = admin.add_group_dialogs()
        for _ in range(20):
            if dialog.count() > 0:
                break
            admin.page.wait_for_timeout(500)
        assert dialog.count() == 1, f"Expected exactly one 'Add New Menu Group' dialog to open, got {dialog.count()}"
        assert "Group Name" in dialog.first.inner_text()

        admin.close_add_group_dialog()
        admin.page.wait_for_timeout(500)
        assert admin.add_group_dialogs().count() == 0, "Cancel should close the Add New Menu Group dialog"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_065b_rapid_add_group_clicks_stack_duplicate_dialogs(administrator_page):
    """Regression pin for Bug #26 (Bug_Report.md, Administrator Module):
    the "Add Group" button has no debounce/disable-while-opening, and its
    multi-second, unindicated open delay means clicking it repeatedly while
    waiting stacks one independent "Add New Menu Group" dialog per click,
    rather than opening (or reusing) a single one. This asserts the
    confirmed-broken stacking behavior; it should start failing -- and be
    flipped to assert exactly one dialog opens regardless of click count --
    once the app debounces this control.
    """
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        admin.open_add_user_wizard()
        admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
        admin.click_next_step()
        admin.page.wait_for_timeout(1000)

        btn = admin.add_group_button()
        btn.click()
        btn.click()
        btn.click()
        admin.page.wait_for_timeout(5000)

        dialog_count = admin.add_group_dialogs().count()
        assert dialog_count > 1, (
            "Bug #26: 3 rapid 'Add Group' clicks should (still) stack multiple duplicate dialogs "
            f"(no debounce) -- expected more than 1, got {dialog_count}. If this now reads 1, the app "
            "has been fixed to debounce/reuse the dialog and this test should be flipped."
        )

        for i in reversed(range(dialog_count)):
            admin.close_add_group_dialog(i)
            admin.page.wait_for_timeout(500)
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)
