import pytest
from playwright.sync_api import expect

from ..installation_test_helpers import (fill_valid_installation, open_wizard,
                                         remove_matching_installations,
                                         select_available_asset, select_available_vehicle)


@pytest.mark.parametrize("remarks", ["Installation completed successfully", ""])
def test_create_installation_with_valid_required_data(page, config, credentials, remarks):
    installation_page, wizard, toast = open_wizard(page, config, credentials)
    installed_by = fill_valid_installation(wizard, remarks=remarks)
    try:
        wizard.click_submit()
        expect(toast.success_toast).to_be_visible()
        installation_page.search_installation(installed_by)
        expect(installation_page.table_rows).to_contain_text(installed_by)
    finally:
        remove_matching_installations(installation_page, installed_by)


def test_saved_installation_persists_after_refresh(page, config, credentials):
    installation_page, wizard, toast = open_wizard(page, config, credentials)
    installed_by = fill_valid_installation(wizard, remarks="Persistence check")
    try:
        wizard.click_submit()
        expect(toast.success_toast).to_be_visible()
        installation_page.search_installation(installed_by)
        expect(installation_page.table_rows).to_contain_text("Persistence check")
        page.reload()
        installation_page.search_installation(installed_by)
        expect(installation_page.table_rows).to_contain_text("Persistence check")
    finally:
        remove_matching_installations(installation_page, installed_by)


def test_existing_asset_and_vehicle_can_be_selected(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    asset = select_available_asset(wizard)
    vehicle = select_available_vehicle(wizard)
    expect(wizard.select_asset_dropdown).to_contain_text(asset)
    expect(wizard.vehicle_dropdown).to_contain_text(vehicle)


def test_create_installation_with_exactly_500_character_remarks(page, config, credentials):
    installation_page, wizard, toast = open_wizard(page, config, credentials)
    installed_by = fill_valid_installation(wizard, remarks="x" * 500)
    try:
        wizard.click_submit()
        expect(toast.success_toast).to_be_visible()
        installation_page.search_installation(installed_by)
        expect(installation_page.table_rows).to_contain_text(installed_by)
    finally:
        remove_matching_installations(installation_page, installed_by)
