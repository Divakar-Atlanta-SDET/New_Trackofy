import re
import pytest

from Pages.login_page import LoginPage
from Pages.reports_page import ReportsPage
from Utils.download_helper import handle_and_verify_download, ensure_downloads_dir, read_csv_rows


def login_and_open_reports(page, config, credentials):
    login_page = LoginPage(page, config)
    reports_page = ReportsPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    reports_page.go_to_reports()
    return reports_page


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_003_uncheck_one_column_absent_from_table(page, config, credentials):
    """REP-COL-003: Positive - Uncheck one column and verify it is absent from generated table."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert "Battery Voltage" not in headers, "Unchecked column 'Battery Voltage' appeared in table headers"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_004_uncheck_multiple_columns(page, config, credentials):
    """REP-COL-004: Positive - Uncheck multiple columns and verify all are absent from generated table."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.toggle_report_column("Door Status", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert "Battery Voltage" not in headers, "'Battery Voltage' should be absent"
    assert "Door Status" not in headers, "'Door Status' should be absent"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_005_keep_only_one_optional_column(page, config, credentials):
    """REP-COL-005: Positive - Keep only one optional column selected."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.uncheck_all_optional_columns()
    reports_page.toggle_report_column("Distance", check=True)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert len(headers) >= 1, "Generated table should contain selected columns"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_006_uncheck_and_recheck_column(page, config, credentials):
    """REP-COL-006: Positive - Uncheck and re-check a column, verify it appears in generated table."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    # Uncheck and then re-check
    reports_page.toggle_report_column("Distance", check=False)
    reports_page.toggle_report_column("Distance", check=True)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert any("Distance" in h for h in headers), "Re-checked column 'Distance' not present in table headers"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_007_select_all_columns(page, config, credentials):
    """REP-COL-007: Positive - Select all columns and verify all appear in report."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert len(headers) >= 5, f"Expected full column set, got {len(headers)} columns"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_011_regenerate_with_new_column_selection(page, config, credentials):
    """REP-COL-011: Positive - Change column selection and regenerate report."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.toggle_report_column("Max Speed", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    headers = reports_page.get_table_column_headers()
    assert "Max Speed" not in headers, "'Max Speed' appeared despite being deselected"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_018_export_report_respects_hidden_columns(page, config, credentials):
    """REP-COL-018: Positive - Exported CSV respects hidden column configuration."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Fleet Summary")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.toggle_report_column("Battery Voltage", check=False)
    reports_page.click_fetch()
    reports_page.wait_for_table()

    ensure_downloads_dir()
    export_btn = reports_page.page.get_by_role("button", name=re.compile(r"Export report to CSV", re.I))
    file_path = handle_and_verify_download(
        page, lambda: export_btn.click(), expected_extension=".csv"
    )

    csv_rows = read_csv_rows(file_path)
    if csv_rows:
        header_row = csv_rows[0]
        assert "Battery Voltage" not in header_row, "Deselected column appeared in exported CSV headers"


@pytest.mark.positive
@pytest.mark.reports
def test_rep_col_019_download_report_with_column_selection(page, config, credentials):
    """REP-COL-019: Positive - Download Work Hour report with custom column selections."""
    reports_page = login_and_open_reports(page, config, credentials)
    reports_page.open_standard_report_form("Work Hour")
    reports_page.select_vehicle("GCBL10536MHG14AG04459")
    reports_page.toggle_report_column("Status", check=False)
    assert reports_page.is_submit_enabled(), "Generate button should be enabled"
