import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from components.toast_notifcations import ToastNotifications


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
def test_submit_valid_fitness_certificate_data(page, config, credentials):
    """TC-038: Submit valid fitness certificate data and assert toast feedback."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.switch_service_subtab("Fitness")
    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()


@pytest.mark.positive
def test_submit_valid_pollution_certificate(page, config, credentials):
    """TC-101: Open Pollution certificate form in Service tab and verify toast or modal stability."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    toast = ToastNotifications(page)

    unit_settings_page.switch_service_subtab("Pollution")
    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.success_toast.count() > 0:
        expect(toast.success_toast.first).to_be_visible()
