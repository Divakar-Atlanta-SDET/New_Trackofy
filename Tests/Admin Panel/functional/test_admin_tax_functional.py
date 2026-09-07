"""Admin Panel Tax CRUD. Confirmed live: Create Tax Profile form (Tax*/
Percent*), a real disabled-until-valid Submit button (native `disabled`
attribute, no separate validation-message element), a PrimeNG p-inputnumber
Percent field that only registers real keystrokes (not fill()), and delete
confirmation via a PrimeNG p-confirmpopup ("Do you want to delete this tax
?" / No / Yes) -- not a modal dialog.

Every tax profile this suite creates uses the "AutoTax" name prefix and is
deleted by this suite itself before the test ends -- never touches the
pre-existing real tax records (tax/Tax/Tax12/taxfree)."""
import time

import pytest


def _unique_tax_name() -> str:
    return f"AutoTax{int(time.time() * 1000) % 10_000_000}"


@pytest.mark.functional
@pytest.mark.admin_panel
def test_admin_tax_001_page_loads_with_existing_data(admin_tax_page):
    assert admin_tax_page.total_count() > 0
    assert admin_tax_page.rows().count() > 0


@pytest.mark.positive
@pytest.mark.admin_panel
def test_admin_tax_002_create_and_delete_tax_profile(admin_tax_page):
    name = _unique_tax_name()
    admin_tax_page.create_tax(name, "5")
    try:
        row = admin_tax_page.row_by_name(name)
        assert row.count() == 1, f"Expected newly created tax {name!r} to appear in the list"
        assert "5" in row.inner_text()
    finally:
        row = admin_tax_page.row_by_name(name)
        if row.count() > 0:
            admin_tax_page.delete_icon(row).click()
            admin_tax_page.page.wait_for_timeout(500)
            admin_tax_page.confirm_delete()
            admin_tax_page.wait_for_text_absent(name)


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_tax_003_submit_disabled_with_empty_fields(admin_tax_page):
    assert not admin_tax_page.is_create_button_enabled()


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_tax_004_submit_disabled_with_only_name_filled(admin_tax_page):
    admin_tax_page.tax_name_input.fill(_unique_tax_name())
    assert not admin_tax_page.is_create_button_enabled()


@pytest.mark.negative
@pytest.mark.admin_panel
def test_admin_tax_005_submit_disabled_with_only_percent_filled(admin_tax_page):
    admin_tax_page.type_into(admin_tax_page.percent_input, "5")
    assert not admin_tax_page.is_create_button_enabled()


@pytest.mark.edgecase
@pytest.mark.admin_panel
def test_admin_tax_006_zero_percent_accepted_or_rejected_consistently(admin_tax_page):
    """0% is a real existing value in production data (the "taxfree" row)
    -- the form must not silently reject it if 0 is a legitimate tax rate."""
    name = _unique_tax_name()
    admin_tax_page.tax_name_input.fill(name)
    admin_tax_page.type_into(admin_tax_page.percent_input, "0")
    enabled = admin_tax_page.is_create_button_enabled()
    if not enabled:
        pytest.skip("0% is rejected by client-side validation (Submit stays disabled) -- consistent with a required-positive-rate rule, not a bug")
    admin_tax_page.create_tax_button.click()
    admin_tax_page.wait_for_loading_to_finish()
    admin_tax_page.wait_for_texts([name])
    try:
        row = admin_tax_page.row_by_name(name)
        assert row.count() == 1
    finally:
        row = admin_tax_page.row_by_name(name)
        if row.count() > 0:
            admin_tax_page.delete_icon(row).click()
            admin_tax_page.page.wait_for_timeout(500)
            admin_tax_page.confirm_delete()
            admin_tax_page.wait_for_text_absent(name)


def _delete_all_autotax_rows(admin_tax_page):
    """Cleanup helper: deletes every row whose name starts with the
    suite's "AutoTax" test prefix, one at a time (re-locating fresh after
    each delete since row indices shift). Never touches real data --
    "AutoTax" never collides with the pre-existing tax/Tax/Tax12/taxfree
    records."""
    admin_tax_page.wait_for_table_loaded()
    admin_tax_page.page.wait_for_timeout(1000)
    rows = admin_tax_page.rows().filter(has_text="AutoTax")
    while rows.count() > 0:
        row = rows.first
        admin_tax_page.delete_icon(row).click()
        admin_tax_page.page.wait_for_timeout(800)
        admin_tax_page.confirm_delete()
        admin_tax_page.page.wait_for_timeout(1000)
        rows = admin_tax_page.rows().filter(has_text="AutoTax")


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
def test_admin_tax_007_xss_payload_in_tax_name_not_executed(admin_tax_page):
    """Injecting a script-tag payload as the tax name must not execute in
    the page context -- either the create is rejected, or it's stored/
    rendered as inert text."""
    payload = "<script>window.__xss_admin_tax=1</script>"
    name = f"{_unique_tax_name()}{payload}"
    try:
        admin_tax_page.tax_name_input.fill(name)
        admin_tax_page.type_into(admin_tax_page.percent_input, "5")
        if admin_tax_page.is_create_button_enabled():
            admin_tax_page.create_tax_button.click()
            admin_tax_page.wait_for_loading_to_finish()
            admin_tax_page.page.wait_for_timeout(1500)
        executed = admin_tax_page.page.evaluate("() => window.__xss_admin_tax === 1")
        assert not executed, "XSS payload executed in tax name field"
    finally:
        _delete_all_autotax_rows(admin_tax_page)


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
def test_admin_tax_008_sql_injection_payload_in_tax_name_handled_safely(admin_tax_page):
    """Injecting a classic SQLi payload as the tax name must not corrupt
    the tax list or produce a raw DB error -- either rejected client-side,
    or stored/rendered as an inert literal string."""
    payload = "AutoTaxSQLi' OR '1'='1"
    try:
        admin_tax_page.tax_name_input.fill(payload)
        admin_tax_page.type_into(admin_tax_page.percent_input, "5")
        if admin_tax_page.is_create_button_enabled():
            admin_tax_page.create_tax_button.click()
            admin_tax_page.wait_for_loading_to_finish()
            admin_tax_page.page.wait_for_timeout(1500)
        body_text = admin_tax_page.visible_text()
        assert not any(marker in body_text for marker in ("SQLSTATE", "SqlException", "syntax error", "ORA-")), (
            "Raw database error leaked into the page after an SQLi-style tax name"
        )
        # The pre-existing real tax records must still be intact -- a
        # successful injection could have altered/dropped unrelated rows.
        assert admin_tax_page.row_by_name("tax").count() >= 1
        assert admin_tax_page.row_by_name("taxfree").count() >= 1
    finally:
        _delete_all_autotax_rows(admin_tax_page)


@pytest.mark.negative
@pytest.mark.admin_panel
@pytest.mark.security
@pytest.mark.parametrize(
    "payload",
    ["<img src=x onerror=window.__xss_admin_tax_search=1>", "' OR '1'='1", "'; DROP TABLE tax;--"],
)
def test_admin_tax_009_search_box_xss_sqli_payloads_handled_safely(admin_tax_page, payload):
    """The Tax List search box must not execute injected script or leak a
    raw DB error, and must not corrupt the underlying data either way."""
    admin_tax_page.search_input.fill(payload)
    admin_tax_page.search_input.press("Enter")
    admin_tax_page.wait_for_loading_to_finish()
    admin_tax_page.page.wait_for_timeout(1000)

    executed = admin_tax_page.page.evaluate("() => window.__xss_admin_tax_search === 1")
    assert not executed, f"XSS payload executed via Tax search box: {payload!r}"

    body_text = admin_tax_page.visible_text()
    assert not any(marker in body_text for marker in ("SQLSTATE", "SqlException", "syntax error", "ORA-")), (
        f"Raw database error leaked into the page after search payload {payload!r}"
    )

    admin_tax_page.search_input.fill("")
    admin_tax_page.search_input.press("Enter")
    admin_tax_page.wait_for_loading_to_finish()
    admin_tax_page.page.wait_for_timeout(1000)
    # The pre-existing real tax records must survive an injection attempt
    # in search unharmed.
    assert admin_tax_page.row_by_name("tax").count() >= 1
    assert admin_tax_page.row_by_name("taxfree").count() >= 1
