import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_set_014_location_control_list_loads(location_control_page):
    """SET-014: Verify Location Control list loads without error."""
    expect(location_control_page.table).to_be_visible()


@pytest.mark.functional
def test_set_082_open_add_location_form(location_control_page):
    """SET-082: Open Add Location form."""
    location_control_page.open_add_location_form()
    expect(location_control_page.location_input).to_be_visible()
    expect(location_control_page.create_btn).to_be_disabled()
