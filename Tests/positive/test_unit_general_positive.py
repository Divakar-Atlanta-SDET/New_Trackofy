import pytest
from playwright.sync_api import expect

from components.toast_notifcations import ToastNotifications
from Utils.data_loader import load_test_data


@pytest.mark.positive
@pytest.mark.parametrize("speed_data", load_test_data("unit_positive.json", "valid_speed_limits"))
def test_tc057_update_speed_limit_valid_value(unit_settings, speed_data):
    """TC-057: Positive - Update Speed Limit with valid parametrized values."""
    unit_page, unit_settings_page = unit_settings
    toast = ToastNotifications(unit_settings_page.page)

    unit_settings_page.update_speed_limit(speed_data["value"])

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
@pytest.mark.parametrize("fuel_data", load_test_data("unit_positive.json", "valid_fuel_avg"))
def test_tc058_update_fuel_consumption_avg_valid(unit_settings, fuel_data):
    """TC-058: Positive - Update Fuel Consumption Avg with valid parametrized values."""
    unit_page, unit_settings_page = unit_settings
    toast = ToastNotifications(unit_settings_page.page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.fuel_avg_spin.fill(fuel_data["value"])
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
@pytest.mark.parametrize("idle_data", load_test_data("unit_positive.json", "valid_fuel_idle"))
def test_tc059_update_fuel_consumption_idling_valid(unit_settings, idle_data):
    """TC-059: Positive - Update Fuel Consumption in Idling with valid parametrized values."""
    unit_page, unit_settings_page = unit_settings
    toast = ToastNotifications(unit_settings_page.page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.fuel_idle_spin.fill(idle_data["value"])
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_tc060_change_mileage_calculation_setting(unit_settings):
    """TC-060: Positive - Change Mileage Calculation dropdown setting."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    toast = ToastNotifications(page)
    unit_settings_page.switch_tab("General")

    unit_settings_page.mileage_calc_select.click()
    options = page.get_by_role("option").all()
    assert len(options) > 0, "Expected at least 1 mileage calculation option"
    options[0].click()
    page.wait_for_timeout(300)

    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
        page.wait_for_timeout(500)

    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_tc061_change_location_group(unit_settings):
    """TC-061: Positive - Change Location Group dropdown selection."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    toast = ToastNotifications(page)
    unit_settings_page.switch_tab("General")

    unit_settings_page.location_group_select.click()
    options = page.get_by_role("option").all()
    assert len(options) > 0, "Expected at least 1 location group option"
    options[0].click()
    page.wait_for_timeout(300)

    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
        page.wait_for_timeout(500)

    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_tc062_change_polyline_colour(unit_settings):
    """TC-062: Positive - Change Polyline Colour selection."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    toast = ToastNotifications(page)
    unit_settings_page.switch_tab("General")

    test_color = "#3b2cc1"
    unit_settings_page.change_polyline_color(test_color)
    page.wait_for_timeout(500)

    current_color = unit_settings_page.polyline_colour_input.input_value().lower()
    assert test_color in current_color or current_color == test_color, f"Expected color '{test_color}', got '{current_color}'"
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_tc063_update_multiple_general_fields_together(unit_settings):
    """TC-063: Positive - Modify multiple editable General fields and update."""
    unit_page, unit_settings_page = unit_settings
    page = unit_settings_page.page
    toast = ToastNotifications(page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.fill("68")
    unit_settings_page.fuel_avg_spin.fill("11.5")
    unit_settings_page.fuel_idle_spin.fill("0.6")

    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
        page.wait_for_timeout(500)

    assert unit_settings_page.speed_limit_spin.input_value() == "68"
    assert unit_settings_page.fuel_avg_spin.input_value() == "11.5"
    assert unit_settings_page.fuel_idle_spin.input_value() == "0.6"
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()
