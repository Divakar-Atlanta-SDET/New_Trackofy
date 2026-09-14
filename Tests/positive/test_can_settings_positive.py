import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_settings_pos_001_alert_configuration_form_renders(can_settings_page):
    expect(can_settings_page.config_heading).to_be_visible()
    expect(can_settings_page.protocol_select).to_be_visible()
    expect(can_settings_page.unit_select).to_be_visible()
    expect(can_settings_page.metric_select).to_be_visible()
    expect(can_settings_page.mode_select).to_be_visible()
    expect(can_settings_page.warning_limit_input).to_be_visible()
    expect(can_settings_page.critical_limit_input).to_be_visible()
    expect(can_settings_page.application_checkbox).to_be_visible()
    expect(can_settings_page.email_checkbox).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_settings_pos_002_configured_rules_table_renders(can_settings_page):
    expect(can_settings_page.rules_heading).to_be_visible()
    assert can_settings_page.row_count() > 0
    assert can_settings_page.configured_rule_count() == can_settings_page.pagination_total()


@pytest.mark.positive
@pytest.mark.can
def test_can_settings_pos_003_reset_clears_the_form(can_settings_page):
    can_settings_page.set_warning_limit("5")
    can_settings_page.set_critical_limit("10")
    can_settings_page.reset()
    assert can_settings_page.warning_limit_input.input_value() == ""
    assert can_settings_page.critical_limit_input.input_value() == ""


@pytest.mark.positive
@pytest.mark.can
def test_can_settings_pos_004_status_and_actions_columns_present(can_settings_page):
    headers = [
        can_settings_page.table.last.locator("thead th").nth(i).inner_text().strip()
        for i in range(can_settings_page.table.last.locator("thead th").count())
    ]
    for expected in ["Unit", "Metric", "Mode", "Warning", "Critical", "Status", "Actions"]:
        assert any(expected in header for header in headers), f"Missing column {expected!r} in {headers}"
