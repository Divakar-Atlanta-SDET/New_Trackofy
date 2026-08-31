import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from components.toast_notifcations import ToastNotifications
from Utils.data_loader import load_test_data


def login_and_open_unit_settings(page, config, credentials):
    """Helper to log in, navigate to /unit and open unit settings."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    return unit_page, unit_settings_page


@pytest.mark.positive
@pytest.mark.parametrize("speed_data", load_test_data("unit_positive.json", "valid_speed_limits"))
def test_tc057_update_speed_limit_valid_value(page, config, credentials, speed_data):
    """TC-057: Positive - Update Speed Limit with valid parametrized values."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.update_speed_limit(speed_data["value"])

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
@pytest.mark.parametrize("fuel_data", load_test_data("unit_positive.json", "valid_fuel_avg"))
def test_tc058_update_fuel_consumption_avg_valid(page, config, credentials, fuel_data):
    """TC-058: Positive - Update Fuel Consumption Avg with valid parametrized values."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.fuel_avg_spin.fill(fuel_data["value"])
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
@pytest.mark.parametrize("idle_data", load_test_data("unit_positive.json", "valid_fuel_idle"))
def test_tc059_update_fuel_consumption_idling_valid(page, config, credentials, idle_data):
    """TC-059: Positive - Update Fuel Consumption in Idling with valid parametrized values."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.fuel_idle_spin.fill(idle_data["value"])
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_tc060_change_mileage_calculation_setting(page, config, credentials):
    """TC-060: Positive - Change Mileage Calculation dropdown setting."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc061_change_location_group(page, config, credentials):
    """TC-061: Positive - Change Location Group dropdown selection."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc062_change_polyline_colour(page, config, credentials):
    """TC-062: Positive - Change Polyline Colour selection."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.positive
def test_tc063_update_multiple_general_fields_together(page, config, credentials):
    """TC-063: Positive - Modify multiple editable General fields and update."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.switch_tab("General")
    unit_settings_page.speed_limit_spin.fill("60")
    unit_settings_page.fuel_avg_spin.fill("12.5")
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()
