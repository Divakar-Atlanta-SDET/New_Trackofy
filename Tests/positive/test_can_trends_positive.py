import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.can
def test_can_trends_pos_001_settings_form_renders(can_trends_page):
    expect(can_trends_page.settings_heading).to_be_visible()
    expect(can_trends_page.protocol_select).to_be_visible()
    expect(can_trends_page.units_select).to_be_visible()
    expect(can_trends_page.chart_type_select).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_trends_pos_002_selecting_protocol_enables_units(can_trends_page):
    can_trends_page.select_first_available_protocol()
    expect(can_trends_page.units_select).to_be_enabled()


@pytest.mark.positive
@pytest.mark.can
def test_can_trends_pos_003_no_metric_shows_placeholder_message(can_trends_page):
    expect(can_trends_page.metric_trend_heading).to_be_visible()
    assert can_trends_page.contains_texts(["Select at least one unit and a metric"])


@pytest.mark.positive
@pytest.mark.can
def test_can_trends_pos_004_multi_parameter_comparison_section_renders(can_trends_page):
    expect(can_trends_page.multi_param_heading).to_be_visible()
    expect(can_trends_page.smart_default_button).to_be_visible()
    expect(can_trends_page.draw_comparison_button).to_be_visible()


@pytest.mark.positive
@pytest.mark.can
def test_can_trends_pos_005_show_markers_and_normalize_checkboxes_toggle(can_trends_page):
    markers_before = can_trends_page.show_markers_checkbox.is_checked()
    can_trends_page.safe_click(can_trends_page.show_markers_checkbox)
    assert can_trends_page.show_markers_checkbox.is_checked() != markers_before

    normalize_before = can_trends_page.normalize_checkbox.is_checked()
    can_trends_page.safe_click(can_trends_page.normalize_checkbox)
    assert can_trends_page.normalize_checkbox.is_checked() != normalize_before
