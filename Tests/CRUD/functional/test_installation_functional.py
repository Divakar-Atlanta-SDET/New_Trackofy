import pytest
from playwright.sync_api import expect

from ..installation_test_helpers import open_wizard


def test_add_installation_form_opens(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    for control in (wizard.select_asset_dropdown, wizard.vehicle_dropdown,
                    wizard.installed_on_date_input, wizard.installed_by_input,
                    wizard.remarks_input, wizard.cancel_button, wizard.submit_button):
        expect(control).to_be_visible()


def test_required_fields_show_validation_when_saved_empty(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    wizard.click_submit()
    for error in wizard.required_errors():
        expect(error).to_be_visible()


@pytest.mark.parametrize("field", ["asset", "vehicle"])
def test_selection_dropdown_opens(page, config, credentials, field):
    _, wizard, _ = open_wizard(page, config, credentials)
    dropdown = getattr(wizard, f"{field}_dropdown" if field == "vehicle" else "select_asset_dropdown")
    dropdown.click()
    if not page.get_by_role("option").count():
        pytest.skip(f"No {field} records are available in the target environment.")
    expect(page.get_by_role("option").first).to_be_visible()


def test_installed_on_date_field_accepts_date(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    wizard.enter_installed_on_date("01/01/2025")
    expect(wizard.installed_on_date_input).to_have_value("01/01/2025")


def test_installed_by_and_remarks_accept_values(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    wizard.enter_installed_by("Test User")
    wizard.enter_remarks("Installation completed successfully")
    expect(wizard.installed_by_input).to_have_value("Test User")
    expect(wizard.remarks_input).to_have_value("Installation completed successfully")


def test_cancel_closes_form_without_saving(page, config, credentials):
    installation_page, wizard, _ = open_wizard(page, config, credentials)
    wizard.enter_remarks("unsaved installation")
    wizard.click_cancel()
    expect(wizard.submit_button).to_be_hidden()
    expect(installation_page.add_installation_button).to_be_visible()
