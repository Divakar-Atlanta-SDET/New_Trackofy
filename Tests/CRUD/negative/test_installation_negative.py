import pytest
from playwright.sync_api import expect

from ..installation_test_helpers import open_wizard, select_available_asset, select_available_vehicle


@pytest.mark.parametrize("missing, error_name", [
    ("asset", "asset_required_error"),
    ("vehicle", "vehicle_required_error"),
    ("installed_on", "installation_date_required_error"),
    ("installed_by", "installed_by_required_error"),
])
def test_save_is_blocked_when_required_field_is_missing(page, config, credentials, missing, error_name):
    _, wizard, _ = open_wizard(page, config, credentials)
    values = {"asset": True, "vehicle": True, "installed_on": "01/01/2025", "installed_by": "Test User"}
    values[missing] = None
    if values["asset"] is not None:
        select_available_asset(wizard)
    if values["vehicle"] is not None:
        select_available_vehicle(wizard)
    if values["installed_on"] is not None:
        wizard.enter_installed_on_date(values["installed_on"])
    if values["installed_by"] is not None:
        wizard.enter_installed_by(values["installed_by"])
    wizard.click_submit()
    expect(getattr(wizard, error_name)).to_be_visible()


def test_save_remains_blocked_when_only_some_required_fields_are_corrected(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    wizard.click_submit()
    select_available_asset(wizard)
    wizard.click_submit()
    expect(wizard.vehicle_required_error).to_be_visible()
    expect(wizard.installation_date_required_error).to_be_visible()
    expect(wizard.installed_by_required_error).to_be_visible()


@pytest.mark.skip(reason="The application rule for invalid/future/past installation dates is not specified.")
def test_prohibited_installation_date_is_rejected():
    pass


@pytest.mark.skip(reason="No supported API fault-injection/mocking contract exists in the current framework.")
def test_installation_save_api_failure():
    pass


@pytest.mark.skip(reason="Duplicate-installation policy is not confirmed by the business rules.")
def test_duplicate_installation_policy():
    pass


@pytest.mark.skip(reason="Dropdowns only accept existing options; no supported invalid-value injection contract exists.")
def test_invalid_asset_selection():
    pass


@pytest.mark.skip(reason="Dropdowns only accept existing options; no supported invalid-value injection contract exists.")
def test_invalid_vehicle_selection():
    pass


@pytest.mark.skip(reason="Installed By field business validation rules are not specified.")
def test_invalid_installed_by_value():
    pass


@pytest.mark.skip(reason="The application exposes no supported API/server-failure simulation hook in this framework.")
def test_expired_session_save():
    pass
