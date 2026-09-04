import pytest
from playwright.sync_api import expect
from Pages.alert_config_page import ALERT_SPECS

# SET-090/094/098/102/106/110/114/118/122/130: open each alert type's
# create/configuration form and confirm it opens with a vehicle-select field.
ALERT_TYPES_STANDARD = list(ALERT_SPECS.keys())


@pytest.mark.functional
@pytest.mark.parametrize("alert_type", ALERT_TYPES_STANDARD)
def test_alert_list_loads(alert_page, alert_type):
    page = alert_page(alert_type)
    expect(page.table).to_be_visible()


@pytest.mark.functional
@pytest.mark.parametrize("alert_type", ALERT_TYPES_STANDARD)
def test_alert_open_create_form(alert_page, alert_type):
    page = alert_page(alert_type)
    page.open_add_form()
    expect(page.vehicle_select).to_be_visible()
    expect(page.submit_btn).to_be_disabled()
    page.close_dialog()
