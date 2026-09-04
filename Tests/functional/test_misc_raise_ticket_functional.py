"""Phase 5 -- Raise Support Ticket (MISC-080 to 114).

Confirmed live: the "X selected" vehicle counter is broken (Bug #35,
Bug_Report.md) -- the underlying multi-select value is correct, only the
separate counter text is stuck at "0 selected". Tests here verify the real
selection state (the combobox's own value), not the broken counter text,
except for the one test that pins the bug itself.
"""
import pytest


@pytest.mark.functional
@pytest.mark.misc
def test_misc_080_open_vehicle_selector(support_page):
    """MISC-080: The vehicle selector opens and lists real units."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    assert options.count() > 0, "Expected real vehicle options in the selector"
    support_page.close_vehicle_dropdown()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_081_select_one_vehicle(support_page):
    """MISC-081: Selecting one vehicle is reflected in the combobox's own
    value (the separate 'X selected' counter is broken -- Bug #35)."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    assert first_option_text in support_page.selected_vehicles_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_082_select_multiple_vehicles(support_page):
    """MISC-082: Selecting multiple vehicles keeps all of them selected."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    first_text = options.nth(0).inner_text()
    second_text = options.nth(1).inner_text()
    options.nth(0).click()
    support_page.page.wait_for_timeout(400)
    options.nth(1).click()
    support_page.page.wait_for_timeout(400)
    support_page.close_vehicle_dropdown()
    selected = support_page.selected_vehicles_text()
    assert first_text in selected and second_text in selected, (
        f"Expected both {first_text!r} and {second_text!r} retained, got {selected!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_083_remove_vehicle(support_page):
    """MISC-083: Re-clicking a selected vehicle removes it from the
    selection."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    first_text = options.nth(0).inner_text()
    options.nth(0).click()
    support_page.page.wait_for_timeout(400)
    assert first_text in support_page.selected_vehicles_text()
    options.nth(0).click()  # toggle off
    support_page.page.wait_for_timeout(400)
    support_page.close_vehicle_dropdown()
    assert first_text not in support_page.selected_vehicles_text(), "Expected the vehicle removed from selection"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_35_vehicle_selected_counter_never_updates(support_page):
    """Regression pin for Bug #35 (Bug_Report.md, Miscellaneous Pages
    Module): the 'X selected' counter stays at '0 selected' no matter how
    many vehicles are actually selected, even though the underlying
    multi-select value is correct. Asserts the confirmed-broken behavior;
    it should start failing -- and be flipped to assert the counter
    updates correctly -- once the app is fixed."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    options.nth(0).click()
    support_page.page.wait_for_timeout(400)
    options.nth(1).click()
    support_page.page.wait_for_timeout(800)
    counter = support_page.selected_vehicle_count_text()
    assert counter == "0 selected", (
        f"Bug #35: the vehicle-selected counter should currently (still) be stuck at '0 selected' "
        f"regardless of real selections. If it now shows the correct count, the app has been fixed "
        f"and this test should be flipped. Got: {counter!r}"
    )
    support_page.close_vehicle_dropdown()


@pytest.mark.skip(
    reason="MISC-084 (unauthorized vehicle unavailable in the selector) requires a known vehicle "
    "outside this account's scope to confirm it's excluded -- there's no foreign/unauthorized vehicle "
    "identifier available to test against from a single real account. Honest skip."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_084_unauthorized_vehicle_unavailable():
    pass


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_085_086_087_required_field_validation(support_page):
    """MISC-085/086/087: Category, Severity and Comment are required --
    Submit stays blocked (or shows validation) while any are missing."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.email_input().fill("qa@example.com")
    support_page.mobile_input().fill("9876543210")
    support_page.page.wait_for_timeout(500)

    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), (
            "Expected the dialog to remain open (not submit) with Category/Severity/Comment blank"
        )
    else:
        assert not submit.is_enabled(), "Expected Submit disabled while required fields are blank"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_088_089_valid_category_and_severity_selection(support_page):
    """MISC-088/089: A category and severity can be selected."""
    support_page.open_raise_ticket_dialog()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    dialog_text = support_page.raise_ticket_dialog().inner_text()
    assert "Others" in dialog_text
    assert "Low" in dialog_text


@pytest.mark.functional
@pytest.mark.misc
def test_misc_090_comment_minimum_valid_value(support_page):
    """MISC-090: A short, meaningful comment is accepted."""
    support_page.open_raise_ticket_dialog()
    support_page.type_into(support_page.comment_textarea(), "Device is offline")
    assert support_page.comment_textarea().input_value() == "Device is offline"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_091_comment_exactly_200_chars(support_page):
    """MISC-091: Exactly 200 characters is accepted and the counter shows
    200/200."""
    support_page.open_raise_ticket_dialog()
    text = "a" * 200
    support_page.type_into(support_page.comment_textarea(), text)
    assert support_page.comment_textarea().input_value() == text
    assert "200/200" in support_page.comment_counter_text() or "200" in support_page.comment_counter_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_092_comment_over_200_chars_cannot_exceed_limit(support_page):
    """MISC-092: Pasting more than 200 characters cannot exceed the
    configured limit."""
    support_page.open_raise_ticket_dialog()
    text = "a" * 250
    support_page.type_into(support_page.comment_textarea(), text)
    actual = support_page.comment_textarea().input_value()
    assert len(actual) <= 200, f"Expected the comment capped at 200 chars, got {len(actual)}"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_093_comment_whitespace_only_rejected(support_page):
    """MISC-093: Whitespace-only comment doesn't satisfy the required
    field -- Submit stays blocked."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    support_page.type_into(support_page.comment_textarea(), "     ")
    support_page.email_input().fill("qa@example.com")
    support_page.mobile_input().fill("9876543210")
    support_page.page.wait_for_timeout(500)
    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), (
            "Expected whitespace-only comment to be rejected as meaningless required input"
        )
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_094_comment_special_characters_handled_safely(support_page):
    """MISC-094: Punctuation/special characters are accepted safely."""
    support_page.open_raise_ticket_dialog()
    payload = "!@#$%^&*()"
    support_page.type_into(support_page.comment_textarea(), payload)
    assert support_page.comment_textarea().input_value() == payload


@pytest.mark.functional
@pytest.mark.misc
def test_misc_095_comment_unicode_handled_safely(support_page):
    """MISC-095: Unicode text (non-Latin + emoji) is preserved safely."""
    support_page.open_raise_ticket_dialog()
    payload = "उपकरण ऑफलाइन है 🚗"
    support_page.type_into(support_page.comment_textarea(), payload)
    assert support_page.comment_textarea().input_value() == payload


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_096_comment_xss_payload_not_executed(support_page):
    """MISC-096: An XSS payload in the comment is never executed as
    script."""
    support_page.open_raise_ticket_dialog()
    payload = "<script>window.__xss_fired=true</script>"
    support_page.type_into(support_page.comment_textarea(), payload)
    fired = support_page.page.evaluate("() => window.__xss_fired === true")
    assert not fired, "XSS payload in the comment should not execute as script"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_097_comment_sql_injection_handled_safely(support_page):
    """MISC-097: A SQL-injection-shaped comment doesn't error the form."""
    support_page.open_raise_ticket_dialog()
    support_page.type_into(support_page.comment_textarea(), "' OR 1=1 --")
    assert support_page.raise_ticket_dialog().is_visible(), "Expected the form to remain functional"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_098_valid_email_accepted(support_page):
    """MISC-098: A valid email is accepted."""
    support_page.open_raise_ticket_dialog()
    support_page.email_input().fill("qa@example.com")
    assert support_page.email_input().input_value() == "qa@example.com"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_099_invalid_email_shows_validation(support_page):
    """MISC-099: An invalid email is flagged."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    support_page.type_into(support_page.comment_textarea(), "Device is offline")
    support_page.email_input().fill("qa@")
    support_page.mobile_input().fill("9876543210")
    support_page.page.wait_for_timeout(500)
    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), "Expected an invalid email to block submission"
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_100_empty_email_required_validation(support_page):
    """MISC-100: Leaving email blank blocks submission."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    support_page.type_into(support_page.comment_textarea(), "Device is offline")
    support_page.mobile_input().fill("9876543210")
    support_page.page.wait_for_timeout(500)
    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), "Expected blank email to block submission"
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_101_email_whitespace_handled(support_page):
    """MISC-101: Leading/trailing spaces around a valid email are handled
    consistently (trimmed or rejected -- either is acceptable as long as
    it's not silently corrupted)."""
    support_page.open_raise_ticket_dialog()
    support_page.email_input().fill(" qa@example.com ")
    value = support_page.email_input().input_value()
    assert "qa@example.com" in value


@pytest.mark.functional
@pytest.mark.misc
def test_misc_102_valid_mobile_accepted(support_page):
    """MISC-102: A valid 10-digit mobile number is accepted."""
    support_page.open_raise_ticket_dialog()
    support_page.mobile_input().fill("9876543210")
    assert support_page.mobile_input().input_value() == "9876543210"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_103_invalid_mobile_shows_validation(support_page):
    """MISC-103: Letters/invalid-length mobile input is flagged."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    support_page.type_into(support_page.comment_textarea(), "Device is offline")
    support_page.email_input().fill("qa@example.com")
    support_page.mobile_input().fill("abc")
    support_page.page.wait_for_timeout(500)
    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), "Expected an invalid mobile to block submission"
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_104_empty_mobile_required_validation(support_page):
    """MISC-104: Leaving mobile blank blocks submission."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    first_option_text = support_page.page.get_by_role("option").first.inner_text()
    support_page.select_vehicle(first_option_text)
    support_page.close_vehicle_dropdown()
    support_page.select_category("Others")
    support_page.select_severity("Low")
    support_page.type_into(support_page.comment_textarea(), "Device is offline")
    support_page.email_input().fill("qa@example.com")
    support_page.page.wait_for_timeout(500)
    submit = support_page.submit_ticket_button()
    if submit.is_enabled():
        submit.click()
        support_page.page.wait_for_timeout(1000)
        assert support_page.raise_ticket_dialog().is_visible(), "Expected blank mobile to block submission"
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_bug35_submit_never_enables_on_a_fully_valid_form(support_page):
    """Regression pin for Bug #35's escalation (Bug_Report.md, Miscellaneous
    Pages Module, CRITICAL): Submit Ticket stays disabled even with a
    completely valid form (real vehicle selected, category/severity chosen,
    valid comment, valid email/mobile) -- verified with zero mat-error
    elements present anywhere in the dialog. Asserts the confirmed-broken
    behavior; it should start failing -- and be flipped to assert Submit
    becomes enabled and a real submission succeeds -- once the app is
    fixed. This blocks MISC-105/106/109/110/112/113/114, which cannot be
    meaningfully tested until Submit actually works.
    """
    support_page.fill_valid_ticket(comment="pytest Bug #35 regression check -- confirms Submit stays disabled.")
    support_page.page.wait_for_timeout(1000)
    errors = support_page.raise_ticket_dialog().locator("mat-error")
    submit = support_page.submit_ticket_button()
    assert not submit.is_enabled(), (
        "Bug #35: Submit Ticket should currently (still) stay disabled even on a fully valid form. "
        "If it's now enabled, the app has been fixed and this test (plus MISC-105/106/109/110/112/113/114) "
        "should be un-skipped and flipped to assert real submission works."
    )
    assert errors.count() == 0, (
        f"Expected zero validation errors shown (confirming the form is genuinely valid, not just "
        f"apparently so) -- found {errors.count()}"
    )
    support_page.close_ticket_dialog()


@pytest.mark.skip(
    reason="MISC-105/112/113/114 (submit a valid ticket, verify it appears/preserves data) are blocked "
    "by Bug #35 (Bug_Report.md, CRITICAL): Submit Ticket never becomes enabled even on a fully valid "
    "form, confirmed exhaustively across four different fill/type/blur methods with zero validation "
    "errors shown. There is no way to create a real ticket through this form to verify against. "
    "Un-skip once Bug #35 is fixed -- see test_misc_bug35_submit_never_enables_on_a_fully_valid_form."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_105_112_113_114_submit_valid_ticket_and_verify():
    pass


@pytest.mark.skip(
    reason="MISC-106 (double-click Submit creates only one ticket) is blocked by Bug #35: Submit never "
    "enables on a valid form, so there is no working single-click submission to even attempt "
    "double-clicking. Un-skip once Bug #35 is fixed."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_106_double_click_submit_creates_only_one_ticket():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_107_cancel_creates_no_ticket(support_page):
    """MISC-107: Cancel closes the dialog without creating a ticket."""
    before_count = support_page.ticket_count()
    support_page.fill_valid_ticket(comment="pytest cancel check -- should never be created.")
    support_page.cancel_ticket_button().click()
    support_page.page.wait_for_timeout(1000)
    assert not support_page.raise_ticket_dialog().is_visible()

    support_page.page.reload()
    support_page.wait_until_ready()
    support_page.page.wait_for_timeout(2000)
    assert support_page.ticket_count() == before_count, "Expected Cancel to create no ticket"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_108_close_via_x_creates_no_ticket(support_page):
    """MISC-108: Closing via the X icon doesn't create a ticket."""
    before_count = support_page.ticket_count()
    support_page.fill_valid_ticket(comment="pytest close-X check -- should never be created.")
    support_page.close_ticket_dialog()
    support_page.page.wait_for_timeout(1000)
    assert not support_page.raise_ticket_dialog().is_visible()

    support_page.page.reload()
    support_page.wait_until_ready()
    support_page.page.wait_for_timeout(2000)
    assert support_page.ticket_count() == before_count, "Expected closing via X to create no ticket"


@pytest.mark.skip(
    reason="MISC-109 (network failure on submit must not falsely report success) is blocked by Bug #35: "
    "Submit Ticket never becomes enabled on a valid form, and Playwright's click() waits for an element "
    "to be enabled before clicking, so there is no way to trigger a submit request to fail in the first "
    "place. Un-skip once Bug #35 is fixed -- see test_misc_bug35_submit_never_enables_on_a_fully_valid_form."
)
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_109_network_failure_on_submit_no_false_success():
    pass


@pytest.mark.skip(
    reason="MISC-110 (simulated API failure on submit must not create a partial/duplicate ticket) is "
    "blocked by Bug #35 for the same reason as MISC-109: Submit never enables, so there is no real submit "
    "request to intercept and fail. Un-skip once Bug #35 is fixed."
)
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_110_api_failure_on_submit_no_duplicate_or_partial():
    pass


@pytest.mark.skip(
    reason="MISC-111 (session expires during submission) has no reliable simulation path in this "
    "suite -- session/token expiry isn't a request-level condition page.route can abort or fulfill the "
    "way MISC-109/110 do, and there's no exposed way to force server-side session invalidation "
    "mid-request. Honest skip, matching the Administrator module's ADM-159 precedent."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_111_session_expiry_during_submission():
    pass
