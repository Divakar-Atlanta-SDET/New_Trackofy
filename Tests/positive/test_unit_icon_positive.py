import pytest
from playwright.sync_api import expect


@pytest.mark.positive
def test_tc071_change_icon_to_another_available_icon(unit_settings):
    """TC-071: Positive - Select an available icon, click Update, and verify it's reflected in the Unit List."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_src = unit_settings_page.current_icon_img.get_attribute("src")
    original_index = unit_settings_page.get_selected_icon_index()

    new_index = unit_settings_page.select_different_icon()
    new_src = unit_settings_page.available_icons.nth(new_index).locator("img").get_attribute("src")
    expect(unit_settings_page.icon_update_btn).to_be_enabled()
    unit_settings_page.icon_update_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.close_modal()
    unit_page.wait_for_unit_page_ready()
    expect(unit_page.table_rows.first.locator("img").first).to_have_attribute("src", new_src)

    try:
        # revert so the shared test unit isn't left permanently changed
        unit_page.open_unit_settings_by_index(0)
        unit_settings_page.wait_for_modal_open()
        unit_settings_page.switch_tab("Icon")
        if original_index >= 0:
            unit_settings_page.select_available_icon(original_index)
        else:
            unit_settings_page.select_available_icon(0 if new_index != 0 else 1)
        if unit_settings_page.icon_update_btn.is_enabled():
            unit_settings_page.icon_update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()
    except Exception:
        pass


@pytest.mark.positive
def test_tc072_change_icon_and_persist_after_reopening(unit_settings):
    """TC-072: Positive - Change icon, update, close settings and reopen Icon tab; icon remains saved."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_index = unit_settings_page.get_selected_icon_index()

    new_index = unit_settings_page.select_different_icon()
    new_src = unit_settings_page.available_icons.nth(new_index).locator("img").get_attribute("src")
    unit_settings_page.icon_update_btn.click()
    unit_settings_page.wait_for_loading_to_finish()
    unit_settings_page.close_modal()

    try:
        unit_page.open_unit_settings_by_index(0)
        unit_settings_page.wait_for_modal_open()
        unit_settings_page.switch_tab("Icon")
        expect(unit_settings_page.current_icon_img).to_have_attribute("src", new_src)
    finally:
        # revert
        if original_index >= 0:
            unit_settings_page.select_available_icon(original_index)
        else:
            unit_settings_page.select_available_icon(0 if new_index != 0 else 1)
        if unit_settings_page.icon_update_btn.is_enabled():
            unit_settings_page.icon_update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()


@pytest.mark.positive
def test_tc073_icon_selection_persists_across_sessions(unit_settings):
    """TC-073: Positive - Verify a saved icon change survives a full page reload."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_index = unit_settings_page.get_selected_icon_index()

    new_index = unit_settings_page.select_different_icon()
    new_src = unit_settings_page.available_icons.nth(new_index).locator("img").get_attribute("src")
    unit_settings_page.icon_update_btn.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.page.reload()
    unit_page.wait_for_unit_page_ready()

    try:
        unit_page.open_unit_settings_by_index(0)
        unit_settings_page.wait_for_modal_open()
        unit_settings_page.switch_tab("Icon")
        expect(unit_settings_page.current_icon_img).to_have_attribute("src", new_src)
    finally:
        if original_index >= 0:
            unit_settings_page.select_available_icon(original_index)
        else:
            unit_settings_page.select_available_icon(0 if new_index != 0 else 1)
        if unit_settings_page.icon_update_btn.is_enabled():
            unit_settings_page.icon_update_btn.click()
            unit_settings_page.wait_for_loading_to_finish()
