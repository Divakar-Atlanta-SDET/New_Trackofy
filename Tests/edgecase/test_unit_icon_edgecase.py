import pytest
from playwright.sync_api import expect


@pytest.mark.edgecase
def test_tc064_switch_unit_type_before_selecting_icon(unit_settings):
    """TC-064: Edge Case - Change Unit Type and verify available icons list updates."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    original_type = unit_settings_page.icon_unit_type_select.inner_text().strip()
    original_srcs = [
        unit_settings_page.available_icons.nth(i).locator("img").get_attribute("src")
        for i in range(unit_settings_page.available_icons.count())
    ]

    unit_settings_page.icon_unit_type_select.click()
    options = unit_settings_page.dropdown_options
    other_option = options.filter(has_not_text=original_type).first
    if other_option.count() == 0:
        pytest.skip("Only one unit type available; cannot switch")
    other_option.click()
    unit_settings_page.wait_for_loading_to_finish()

    unit_settings_page.available_icons.first.wait_for(state="visible")
    new_srcs = [
        unit_settings_page.available_icons.nth(i).locator("img").get_attribute("src")
        for i in range(unit_settings_page.available_icons.count())
    ]
    assert new_srcs != original_srcs, "Available icons should update when unit type changes"


@pytest.mark.edgecase
def test_tc065_rapidly_switch_unit_types(unit_settings):
    """TC-065: Edge Case - Change unit type multiple times quickly; UI ends in a stable, consistent state."""
    unit_page, unit_settings_page = unit_settings
    unit_settings_page.switch_tab("Icon")
    unit_settings_page.icon_unit_type_select.click()
    options = unit_settings_page.dropdown_options
    count = min(options.count(), 3)
    if count < 2:
        pytest.skip("Not enough unit types available to switch between")
    unit_settings_page.page.keyboard.press("Escape")
    unit_settings_page.page.wait_for_timeout(300)

    for i in range(count):
        unit_settings_page.icon_unit_type_select.click()
        opts = unit_settings_page.dropdown_options
        opts.nth(i % opts.count()).click()
        unit_settings_page.page.wait_for_timeout(300)

    unit_settings_page.wait_for_loading_to_finish()
    expect(unit_settings_page.icon_unit_type_select).to_be_visible()
    expect(unit_settings_page.available_icons.first).to_be_visible()
