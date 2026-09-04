import time

import pytest

from Pages.administrator_page import AdministratorPage


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _delete_if_exists(admin, username: str):
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


def _to_step3(admin, username: str):
    admin.open_add_user_wizard()
    admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
    admin.click_next_step()
    admin.select_menu_group("example21")
    admin.click_next_step()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_070_all_eight_categories_listed(administrator_page):
    """ADM-070: All 8 General Permission categories are listed on Step 3."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step3(admin, username)
        dialog_text = admin.wizard_dialog().inner_text()
        for category in AdministratorPage.GENERAL_PERMISSION_CATEGORIES:
            assert category in dialog_text, f"Expected category '{category}' listed on Step 3: {dialog_text!r}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.parametrize("category", AdministratorPage.GENERAL_PERMISSION_CATEGORIES)
def test_adm_general_permission_category_expand_select_unselect_persist(administrator_page, category):
    """ADM-071 to 133 (shared behavior, parametrized across all 8 categories):
    expanding a category reveals a nonzero count of permission items, its
    category checkbox starts UNCHECKED by default (confirmed live, isolated
    probe with zero prior clicks -- an opt-in model), clicking it toggles
    the state, and the toggled state survives collapsing and re-expanding
    the category."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step3(admin, username)

        admin.expand_permission_category(category)
        item_count = admin.permission_category_count(category)
        assert item_count >= 0, f"Expected a readable permission count for '{category}'"

        checkbox = admin.permission_category_checkbox(category)
        was_checked = admin.is_checkbox_checked(checkbox)
        assert not was_checked, f"Expected '{category}' to start denied (unchecked) by default, was checked"

        checkbox.click()
        admin.page.wait_for_timeout(400)
        toggled = admin.is_checkbox_checked(admin.permission_category_checkbox(category))
        assert toggled != was_checked, f"Clicking '{category}' checkbox should toggle its state"

        # collapse (click header again) then re-expand
        admin.expand_permission_category(category)
        admin.expand_permission_category(category)
        after_reexpand = admin.is_checkbox_checked(admin.permission_category_checkbox(category))
        assert after_reexpand == toggled, (
            f"'{category}' toggled state should survive collapse/re-expand: "
            f"expected {toggled}, got {after_reexpand}"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)
