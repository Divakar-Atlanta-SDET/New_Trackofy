import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_tc066_verify_icon_tab_loads(unit_settings):
    """TC-066: Functional - Open Icon tab and verify Unit Type, Current Icon, and Available Icons display."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.icon_unit_type_select).to_be_visible()
    expect(unit_settings_page.current_icon_img).to_be_visible()
    expect(unit_settings_page.available_icons_heading).to_be_visible()
    expect(unit_settings_page.available_icons.first).to_be_visible()


@pytest.mark.functional
def test_tc067_verify_current_icon_is_displayed(unit_settings):
    """TC-067: Functional - Open Icon tab and check current icon matches Unit List icon."""
    unit_page, unit_settings_page = unit_settings
    list_icon_src = unit_page.table_rows.first.locator("img").first.get_attribute("src")
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.current_icon_img).to_be_visible()
    settings_icon_src = unit_settings_page.current_icon_img.get_attribute("src")
    assert list_icon_src == settings_icon_src, "Icon tab's current icon should match the Unit List row icon"


@pytest.mark.functional
def test_tc068_open_unit_type_dropdown(unit_settings):
    """TC-068: Functional - Click Unit Type dropdown in Icon tab."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.wait_for_visible(unit_settings_page.available_icons.first)
    unit_settings_page.icon_unit_type_select.click()
    options = unit_settings_page.dropdown_options
    unit_settings_page.wait_for_visible(options.first)
    assert options.count() > 0
    unit_settings_page.page.keyboard.press("Escape")


@pytest.mark.functional
def test_tc069_cancel_icon_change(unit_settings):
    """TC-069: Functional - Select another icon but do not update; close/reopen keeps original icon."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_src = unit_settings_page.current_icon_img.get_attribute("src")

    unit_settings_page.select_different_icon()
    unit_settings_page.close_modal()

    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    unit_settings_page.switch_tab("Icon")
    expect(unit_settings_page.current_icon_img).to_have_attribute("src", original_src)
