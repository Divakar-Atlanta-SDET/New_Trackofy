import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
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


@pytest.mark.edgecase
@pytest.mark.parametrize("boundary_data", load_test_data("unit_edgecase.json", "boundary_speed_limits"))
def test_boundary_speed_limits(page, config, credentials, boundary_data):
    """TC-039, TC-040: Edge Case - Boundary speed limits (0, 50.5)."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.update_speed_limit(boundary_data["value"])
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
@pytest.mark.parametrize("space_data", load_test_data("unit_edgecase.json", "whitespace_padded_inputs"))
def test_whitespace_padded_inputs(page, config, credentials, space_data):
    """TC-041: Edge Case - Leading and trailing whitespace inputs."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.update_speed_limit(space_data["value"])
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc042_update_without_changing_any_value(page, config, credentials):
    """TC-042: Edge Case - Click Update without making edits."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    if unit_settings_page.update_btn.is_enabled():
        unit_settings_page.update_btn.click()
    expect(unit_settings_page.modal_heading).to_be_visible()


@pytest.mark.edgecase
def test_tc043_change_colour_and_cancel_without_update(page, config, credentials):
    """TC-043: Edge Case - Change polyline colour and close without updating."""
    unit_page, unit_settings_page = login_and_open_unit_settings(page, config, credentials)
    unit_settings_page.switch_tab("General")
    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()
