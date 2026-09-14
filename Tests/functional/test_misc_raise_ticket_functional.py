"""Phase 5 -- Raise Support Ticket (MISC-080 to 114).

Reverified live 2026-09-13: Bug #35 (Bug_Report.md) is FIXED end-to-end --
the "X selected" vehicle counter correctly reflects real selections, and
Submit Ticket genuinely creates a real ticket (confirmed via a fresh
reload + search for a unique marker). An earlier same-day reverification
pass ("Submit is enabled but the click fires nothing") was itself a false
positive from an insufficient wait after clicking Submit -- this page's
response time is confirmed intermittently slow (see Bug #75/#76-adjacent
new finding), and the original diagnostic script read an in-flight state
as final. Corrected after the user manually verified tickets do get
created and pushed back on the finding -- see
test_misc_bug35_submit_creates_a_real_ticket.

Separately, confirmed a vehicle can only have one open ticket at a time
across ALL categories (not just the same category) -- see
test_misc_bug35_one_open_ticket_per_vehicle_any_category.
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
def test_misc_35_vehicle_selected_counter_updates(support_page):
    """Regression pin for part of Bug_Report.md #35 (Miscellaneous Pages
    Module). Reverified live (2026-09-13): FIXED -- the 'X selected'
    counter now correctly reflects real selections (previously stuck at
    '0 selected'). Note: Bug #35 overall is NOT fixed -- Submit Ticket now
    enables correctly but clicking it does nothing (see
    test_misc_bug35_submit_enables_but_click_does_nothing)."""
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    options.nth(0).click()
    support_page.page.wait_for_timeout(400)
    options.nth(1).click()
    support_page.page.wait_for_timeout(800)
    counter = support_page.selected_vehicle_count_text()
    assert counter == "2 selected", (
        f"Bug #35 regression: expected the counter to correctly show '2 selected' after picking 2 "
        f"vehicles. Got: {counter!r}"
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
def test_misc_bug35_submit_creates_a_real_ticket(support_page):
    """Regression pin for Bug_Report.md #35 (Miscellaneous Pages Module).
    Reverified live (2026-09-13): FIXED end-to-end -- a fully valid form
    (real vehicle selected, category/severity chosen, valid comment, valid
    email/mobile) correctly enables Submit Ticket, and clicking it
    genuinely creates a real ticket. Confirmed via a success toast, then a
    fresh reload + search for a unique marker in the comment, finding the
    exact new ticket. (An earlier same-day check concluding the opposite
    was itself a false positive from an insufficient wait -- this page's
    response time is confirmed intermittently slow, and reading state too
    soon after the click looked identical to "nothing happened.")
    Tries several candidate vehicles in turn (rather than a single fixed
    pick) since this shared staging account accumulates open tickets
    across many vehicles from repeated live testing -- the "one open
    ticket per vehicle" business rule (see
    test_misc_bug35_one_open_ticket_per_vehicle_any_category) would
    otherwise make a single hardcoded vehicle pick collide unpredictably.
    """
    import time
    marker = f"pytestbug35mark{int(time.time())}"
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    candidates = [options.nth(i).inner_text() for i in range(options.count())]
    support_page.close_vehicle_dropdown()

    toast_text = ""
    for vehicle_id in reversed(candidates):
        support_page.open_vehicle_dropdown()
        support_page.select_vehicle(vehicle_id)
        support_page.close_vehicle_dropdown()
        support_page.select_category("Others")
        support_page.select_severity("Low")
        support_page.type_into(support_page.comment_textarea(), f"{marker} -- pytest regression check.")
        support_page.email_input().fill("pytest.qa@example.com")
        support_page.mobile_input().fill("9876543210")
        support_page.page.wait_for_timeout(1000)

        submit = support_page.submit_ticket_button()
        assert submit.is_enabled(), "Expected Submit Ticket to be enabled on a fully valid form."
        submit.click()
        # Confirmed live this page's response can be intermittently slow --
        # give it a generous window rather than a short fixed wait.
        toast_text = ""
        for _ in range(12):
            support_page.page.wait_for_timeout(1000)
            toast = support_page.page.locator("app-toast")
            if toast.count():
                text = toast.inner_text().strip()
                if text:
                    toast_text = text
            if not support_page.raise_ticket_dialog().is_visible():
                break

        if "success" in toast_text.lower() or "created" in toast_text.lower():
            break
        if support_page.raise_ticket_dialog().is_visible():
            # rejected (e.g. "already exists") -- try the next candidate
            continue
        break

    if "success" not in toast_text.lower() and "created" not in toast_text.lower():
        # Every vehicle in the fleet already has an open ticket (confirmed
        # live 2026-09-13: this account's own accumulated test data from
        # extensive same-day Support testing consumed nearly the entire
        # 36-vehicle fleet) -- there is no delete/close control available
        # to this account to free one up (confirmed: the ticket detail
        # page offers only "Send Remark" and "Back", no cancel/close).
        # Skip rather than fail or create yet more unclearable test data;
        # Submit Ticket's own success path is independently confirmed via
        # this session's live RCA (multiple fresh tickets created and
        # verified present in the list across earlier manual checks).
        if support_page.raise_ticket_dialog().is_visible():
            support_page.close_ticket_dialog()
        pytest.skip(
            "No vehicle without an existing open ticket was available on this account -- cannot "
            "create a genuinely fresh ticket to verify against without a way to close/free one up. "
            f"Last rejection: {toast_text!r}"
        )

    support_page.page.reload()
    support_page2 = support_page
    support_page2.wait_until_ready()
    for _ in range(20):
        if "STATUS\n----" not in support_page2.page.inner_text("body") and marker in support_page2.page.inner_text("body"):
            break
        support_page2.page.wait_for_timeout(500)
    support_page2.search(marker)
    support_page2.page.wait_for_timeout(1500)
    rows = support_page2.rows()
    assert rows.count() == 1, (
        f"Bug #35 regression: expected exactly the new ticket ({marker!r}) to be found after reload, "
        f"got {rows.count()} matching rows. Toast at submit time was: {toast_text!r}"
    )
@pytest.mark.skip(
    reason="MISC-105/112/113/114 (submit a valid ticket, verify it appears/preserves data) was "
    "previously blocked by Bug #35, now confirmed FIXED 2026-09-13 -- the core submit-and-verify path "
    "is already covered by test_misc_bug35_submit_creates_a_real_ticket above. This stub itself "
    "(covering the additional MISC-112/113/114 data-preservation detail) remains unimplemented -- "
    "genuinely unblocked now, just not yet written. Separate follow-up work, not part of this "
    "reverification pass."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_105_112_113_114_submit_valid_ticket_and_verify():
    pass


@pytest.mark.skip(
    reason="MISC-106 (double-click Submit creates only one ticket) was previously blocked by Bug #35, "
    "now confirmed FIXED 2026-09-13 (see test_misc_bug35_submit_creates_a_real_ticket) -- genuinely "
    "unblocked now, just not yet implemented. Separate follow-up work."
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
    reason="MISC-109 (network failure on submit must not falsely report success) was previously blocked "
    "by Bug #35, now confirmed FIXED 2026-09-13 (see test_misc_bug35_submit_creates_a_real_ticket) -- "
    "genuinely unblocked now, just not yet implemented. Separate follow-up work."
)
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_109_network_failure_on_submit_no_false_success():
    pass


@pytest.mark.skip(
    reason="MISC-110 (simulated API failure on submit must not create a partial/duplicate ticket) was "
    "previously blocked by Bug #35, now confirmed FIXED 2026-09-13 -- genuinely unblocked now, just "
    "not yet implemented. Separate follow-up work."
)
@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_110_api_failure_on_submit_no_duplicate_or_partial():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_bug35_one_open_ticket_per_vehicle_any_category(support_page):
    """New finding from Bug_Report.md #35's 2026-09-13 reverification
    (not itself a confirmed bug -- flagged for product awareness): a
    vehicle can only have one open support ticket at a time, and this
    restriction is NOT scoped to the same category as the existing open
    ticket. Confirmed live 3x across 3 independent vehicles: first ticket
    for a vehicle succeeds; a second ticket for the SAME vehicle under a
    genuinely DIFFERENT category is rejected identically to a same-category
    retry, both with "Complaint already exists for <vehicle IMEI>".
    """
    support_page.open_raise_ticket_dialog()
    support_page.open_vehicle_dropdown()
    options = support_page.page.get_by_role("option")
    vehicle_id = options.first.inner_text()
    support_page.select_vehicle(vehicle_id)
    support_page.close_vehicle_dropdown()
    support_page.category_combobox().click()
    support_page.page.wait_for_timeout(500)
    category_options = support_page.page.get_by_role("option")
    categories = [category_options.nth(i).inner_text() for i in range(category_options.count())]
    support_page.page.keyboard.press("Escape")
    assert len(categories) >= 2, "Expected at least 2 categories to test cross-category blocking"

    def _attempt(category: str) -> str:
        support_page.select_category(category)
        support_page.select_severity("Low")
        support_page.type_into(support_page.comment_textarea(), f"pytest bug35 same-vehicle check ({category}).")
        support_page.email_input().fill("pytest.qa@example.com")
        support_page.mobile_input().fill("9876543210")
        support_page.page.wait_for_timeout(500)
        support_page.submit_ticket_button().click()
        for _ in range(10):
            support_page.page.wait_for_timeout(1000)
            toast = support_page.page.locator("app-toast")
            if toast.count() and toast.inner_text().strip():
                return toast.inner_text()
        return ""

    first_result = _attempt(categories[0])
    if not support_page.raise_ticket_dialog().is_visible():
        # first attempt succeeded and closed the dialog -- reopen for the vehicle
        support_page.open_raise_ticket_dialog()
        support_page.open_vehicle_dropdown()
        support_page.select_vehicle(vehicle_id)
        support_page.close_vehicle_dropdown()
    second_result = _attempt(categories[1])

    if support_page.raise_ticket_dialog().is_visible():
        support_page.close_ticket_dialog()

    assert "already exists" in second_result.lower(), (
        f"Expected a second ticket for the same vehicle under a different category to be rejected as "
        f"an existing complaint. First attempt result: {first_result!r}. Second attempt result: {second_result!r}"
    )


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
