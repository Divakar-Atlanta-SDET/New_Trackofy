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


def _to_step4(admin, username: str):
    admin.open_add_user_wizard()
    admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], "No")
    admin.click_next_step()
    admin.select_menu_group("example21")
    admin.click_next_step()
    admin.click_next_step()
    admin.page.wait_for_timeout(1000)


def _selected_vehicles_line(admin) -> str:
    text = admin.wizard_dialog().inner_text()
    lines = text.splitlines()
    idx = lines.index("Vehicles")
    return lines[idx + 1] if idx + 1 < len(lines) else ""


@pytest.mark.functional
@pytest.mark.admin
def test_adm_134_unit_selector_lists_available_units(administrator_page):
    """ADM-134: The unit selector on Step 4 lists real, known vehicles."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        options_text = " ".join(
            admin.page.get_by_role("option").nth(i).inner_text() for i in range(admin.page.get_by_role("option").count())
        )
        admin.close_units_dropdown()
        assert "HP12G9691" in options_text, f"Expected a known real vehicle in the unit list: {options_text!r}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_135_136_select_one_and_multiple_units(administrator_page):
    """ADM-135/136: Selecting one unit shows it under 'Vehicles'; selecting
    a second adds to the same selection rather than replacing it."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        opts = admin.page.get_by_role("option")
        first_id = opts.nth(0).inner_text()
        second_id = opts.nth(1).inner_text()
        opts.nth(0).click()
        admin.page.wait_for_timeout(500)
        assert first_id in _selected_vehicles_line(admin)

        opts.nth(1).click()
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()
        selected_line = _selected_vehicles_line(admin)
        assert first_id in selected_line and second_id in selected_line, (
            f"Expected both '{first_id}' and '{second_id}' retained together, got: {selected_line!r}"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_137_change_selected_units(administrator_page):
    """ADM-137: Selecting a different unit changes the selection."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        opts = admin.page.get_by_role("option")
        first_id = opts.nth(0).inner_text()
        opts.nth(0).click()
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()
        assert first_id in _selected_vehicles_line(admin)

        admin.open_units_dropdown()
        opts2 = admin.page.get_by_role("option")
        second_id = opts2.nth(1).inner_text()
        opts2.nth(1).click()
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()
        selected_line = _selected_vehicles_line(admin)
        assert second_id in selected_line, f"Expected newly selected '{second_id}' present: {selected_line!r}"
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_138_remove_a_unit(administrator_page):
    """ADM-138: Re-clicking a selected unit's option removes it from the
    selection -- with zero units selected, the panel reverts to its
    'Select at least one unit' placeholder."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        opts = admin.page.get_by_role("option")
        vehicle_id = opts.nth(0).inner_text()
        opts.nth(0).click()
        admin.page.wait_for_timeout(500)
        assert vehicle_id in _selected_vehicles_line(admin)

        opts.nth(0).click()  # toggle off
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()
        assert vehicle_id not in _selected_vehicles_line(admin), "Unit should be removed from selection"
        assert "Select at least one unit" in admin.wizard_dialog().inner_text()
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_139_no_unit_selected_shows_placeholder_not_permission_panel(administrator_page):
    """ADM-139: With no unit selected, the permission panel shows a
    placeholder instead of a (meaningless, scope-less) permission list."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        dialog_text = admin.wizard_dialog().inner_text()
        assert "Select at least one unit" in dialog_text
        assert "Unit permissions will appear here" in dialog_text
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_140_141_142_unit_permission_checkboxes_default_unchecked_and_toggle(administrator_page):
    """ADM-140/141/142: Selecting a unit reveals the 'Unit' permission
    category (Change Advanced Settings, Change Icon, Manage Services), each
    starting UNCHECKED by default (confirmed live, isolated probe with zero
    prior clicks -- an opt-in model, same as General Permission), and each
    independently toggleable."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        admin.page.get_by_role("option").nth(0).click()
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()

        admin.expand_permission_category("Unit")
        for label in AdministratorPage.UNIT_PERMISSIONS:
            checkbox = admin.unit_permission_checkbox(label)
            assert not admin.is_checkbox_checked(checkbox), f"Expected '{label}' to start denied (unchecked) by default"

        target = AdministratorPage.UNIT_PERMISSIONS[0]
        checkbox = admin.unit_permission_checkbox(target)
        checkbox.click()
        admin.page.wait_for_timeout(400)
        assert admin.is_checkbox_checked(admin.unit_permission_checkbox(target)), (
            f"Clicking '{target}' should toggle it on"
        )
        # the other two permissions must be unaffected by toggling one
        for label in AdministratorPage.UNIT_PERMISSIONS[1:]:
            assert not admin.is_checkbox_checked(admin.unit_permission_checkbox(label)), (
                f"Toggling '{target}' should not affect '{label}'"
            )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)


@pytest.mark.functional
@pytest.mark.admin
def test_adm_143_unit_selection_and_permissions_persist_across_navigation(administrator_page):
    """ADM-143: Selected units and a toggled unit permission survive
    navigating Step 4 -> 3 -> 4."""
    admin = administrator_page
    username = _unique_username("pytestqa")
    try:
        _to_step4(admin, username)
        admin.open_units_dropdown()
        vehicle_id = admin.page.get_by_role("option").nth(0).inner_text()
        admin.page.get_by_role("option").nth(0).click()
        admin.page.wait_for_timeout(500)
        admin.close_units_dropdown()

        admin.expand_permission_category("Unit")
        target = AdministratorPage.UNIT_PERMISSIONS[0]
        admin.unit_permission_checkbox(target).click()
        admin.page.wait_for_timeout(400)

        admin.click_back()  # 4 -> 3
        admin.page.wait_for_timeout(800)
        admin.click_next_step()  # 3 -> 4
        admin.page.wait_for_timeout(800)

        assert vehicle_id in _selected_vehicles_line(admin), "Selected unit should survive Step 4->3->4"
        admin.expand_permission_category("Unit")
        assert admin.is_checkbox_checked(admin.unit_permission_checkbox(target)), (
            f"Toggled '{target}' state should survive Step 4->3->4"
        )
        admin.close_wizard()
    finally:
        _delete_if_exists(admin, username)
