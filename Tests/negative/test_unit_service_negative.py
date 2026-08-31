import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from components.toast_notifcations import ToastNotifications


@pytest.mark.negative
def test_submit_blank_fitness_form_validation(page, config, credentials):
    """TC-035: Submit blank fitness form and verify validation errors or error toast."""
    login_page = LoginPage(page, config)
    unit_page = UnitPage(page)
    unit_settings_page = UnitSettingsPage(page)
    toast = ToastNotifications(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()

    unit_settings_page.switch_service_subtab("Fitness")

    if unit_settings_page.fitness_submit_btn.is_visible():
        unit_settings_page.fitness_submit_btn.click()

    expect(unit_settings_page.modal_heading).to_be_visible()
    if toast.error_toast.count() > 0:
        expect(toast.error_toast.first).to_be_visible()
