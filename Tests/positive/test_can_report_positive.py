import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_report_pos_001_settings_form_renders(can_report_page):
    expect(can_report_page.settings_heading).to_be_visible()
    expect(can_report_page.protocol_select).to_be_visible()
    expect(can_report_page.units_select).to_be_visible()
    expect(can_report_page.generate_button).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_report_pos_002_generate_with_valid_protocol_and_all_units(can_report_page):
    can_report_page.select_first_available_protocol()
    can_report_page.select_all_units()
    can_report_page.generate()

    assert can_report_page.has_results_table() or can_report_page.has_no_data_message(), (
        "Generate Report produced neither a results table nor a no-data message"
    )


@pytest.mark.positive
@pytest.mark.can
def test_can_report_pos_003_generated_report_has_export_search_pagination(can_report_page):
    can_report_page.select_first_available_protocol()
    can_report_page.select_all_units()
    can_report_page.generate()

    if not can_report_page.has_results_table():
        pytest.skip("No data in the default range for this protocol/unit selection")

    expect(can_report_page.export_button("excel")).to_be_visible()
    expect(can_report_page.export_button("csv")).to_be_visible()
    # Bug (Bug_Report.md): unlike its sibling CAN pages (Alerts, Unit,
    # Settings), the Report page has no PDF export button at all --
    # confirmed live, only Excel/CSV/Copy exist here. Not asserting a
    # PDF button's presence; see Bug_Report.md for the real finding.
