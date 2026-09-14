import re
import pytest
from playwright.sync_api import expect

from Pages.unit_page import UnitPage
from Utils.data_loader import load_test_data


@pytest.mark.functional
def test_unit_list_page_loads_and_displays_table_and_count(authenticated_page):
    """TC-011: Verify Unit List loads successfully and displays unit count badge."""
    unit_page = UnitPage(authenticated_page)
    unit_page.open_unit_list()

    expect(unit_page.unit_list_heading).to_be_visible()
    expect(unit_page.unit_count_badge).to_be_visible()
    expect(unit_page.table).to_be_visible()
    assert unit_page.get_unit_count() > 0


@pytest.mark.functional
@pytest.mark.parametrize("filter_data", load_test_data("unit_functional.json", "unit_type_filters"))
def test_unit_list_type_filters(authenticated_page, filter_data):
    """TC-024: Functional - Filter Unit list by parametrized unit types (Car, Bus, Truck, Scooty)."""
    unit_page = UnitPage(authenticated_page)
    unit_page.open_unit_list()
    unit_page.filter_by_unit_type(filter_data["unit_type"])
    expect(unit_page.table).to_be_visible()


@pytest.mark.functional
def test_open_and_switch_unit_settings_tabs(unit_settings):
    """TC-013, TC-014: Open Unit Settings modal, switch all tabs, and close."""
    unit_page, unit_settings_page = unit_settings

    unit_settings_page.switch_tab("Icon")
    unit_settings_page.switch_tab("Sensors")
    unit_settings_page.switch_tab("Service")
    unit_settings_page.switch_tab("Alert")
    unit_settings_page.switch_tab("General")

    unit_settings_page.close_modal()
    expect(unit_page.unit_list_heading).to_be_visible()


@pytest.mark.functional
def test_unit_list_accessible_via_direct_url(authenticated_page, config):
    """Regression test for retest_bug_report.md NEW-1 (2026-09-11, confirmed
    app-wide on both Dashboard and Unit): a module must be reachable by
    navigating straight to its URL, not only via an in-app nav-link click.
    Deliberately uses page.goto() directly (not unit_page.open_unit_list(),
    which works around this exact bug by clicking the nav link instead) --
    this test exists specifically to catch a regression on direct URL
    access itself.

    Expected to FAIL until the underlying app bug is fixed: as of this
    writing, a direct goto("/unit") silently redirects to /home instead of
    loading the Unit list.
    """
    page = authenticated_page
    page.goto(f"{config['base_url']}/unit")
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/unit/?$"))
    expect(UnitPage(page).unit_list_heading).to_be_visible()


@pytest.mark.functional
def test_unit_list_survives_page_refresh(authenticated_page, config):
    """Regression test for retest_bug_report.md NEW-1 (2026-09-11): once on
    the Unit list, a plain browser refresh must keep the user there, not
    silently bounce them back to /home.

    Expected to FAIL until the underlying app bug is fixed.
    """
    page = authenticated_page
    unit_page = UnitPage(page)
    unit_page.open_unit_list()
    expect(unit_page.unit_list_heading).to_be_visible()

    page.reload(wait_until="load")
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/unit/?$"))
    expect(unit_page.unit_list_heading).to_be_visible()
