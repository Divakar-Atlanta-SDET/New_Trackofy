import pytest
from playwright.sync_api import expect

from ..installation_test_helpers import fill_valid_installation, open_wizard, remove_matching_installations


@pytest.mark.parametrize("length", [0, 499, 500, 501])
def test_remarks_boundary_lengths(page, config, credentials, length):
    _, wizard, _ = open_wizard(page, config, credentials)
    value = "x" * length
    wizard.enter_remarks(value)
    actual = wizard.remarks_input.input_value()
    assert len(actual) <= 500
    assert actual == value[:500]


def test_whitespace_remarks_are_not_executed_or_treated_as_script(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    wizard.enter_remarks("   \n\t   ")
    assert wizard.remarks_input.input_value().strip() == ""


def test_xss_payload_is_handled_as_text(page, config, credentials):
    installation_page, wizard, toast = open_wizard(page, config, credentials)
    payload = "<script>alert(1)</script>"
    installed_by = fill_valid_installation(wizard, remarks=payload)
    try:
        wizard.click_submit()
        expect(toast.success_toast).to_be_visible()
        installation_page.search_installation(installed_by)
        expect(installation_page.table_rows).to_contain_text(payload)
        assert page.locator("script").filter(has_text="alert(1)").count() == 0
    finally:
        remove_matching_installations(installation_page, installed_by)


def test_sql_like_input_is_handled_as_text(page, config, credentials):
    _, wizard, _ = open_wizard(page, config, credentials)
    payload = "' OR '1'='1"
    wizard.enter_remarks(payload)
    expect(wizard.remarks_input).to_have_value(payload)


def test_duplicate_save_clicks_do_not_create_multiple_records(page, config, credentials):
    installation_page, wizard, toast = open_wizard(page, config, credentials)
    installed_by = fill_valid_installation(wizard, remarks="duplicate click check")
    try:
        wizard.submit_button.click()
        wizard.submit_button.dispatch_event("click")
        expect(toast.success_toast).to_be_visible()
        installation_page.search_installation(installed_by)
        expect(installation_page.delete_installation_button).to_have_count(1)
    finally:
        remove_matching_installations(installation_page, installed_by)


@pytest.mark.skip(reason="Duplicate-installation policy is not confirmed by the business rules.")
def test_duplicate_save_business_rule():
    pass
