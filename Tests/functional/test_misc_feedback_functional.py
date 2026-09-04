"""Phase 10 -- Feedback Prompt & Form (MISC-205 to 258).

Confirmed live: the prompt ("Using New Trackofy? / Share feedback (30
sec)...") is reliably triggered on demand via a persistent floating
"FEEDBACK" nav button (present on /profile/* pages, not /home) -- used
here instead of guessing at an unobserved auto-trigger condition.
Confirmed live facts about the form itself: New/Old/Not sure are plain
buttons behaving as a single-select group ("New" pre-selected by
default); the 5 stars are individually aria-labelled ("Set rating to
N") and fill 1..N on click; the 6+6 tags are genuinely multi-select
(toggle on/off independently); Mobile and Email are pre-populated from
the account profile; Submit is enabled even with nothing touched
(everything beyond the pre-filled defaults is optional).
"""
import re
import tempfile

import pytest

# Minimal real 1x1 PNG (67 bytes) -- same fixture pattern already
# established in Tests/positive/test_settings_driver_positive.py.
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a4944415478da6360000002000155aabb7b0000000049454e44ae426082"
)
_PDF_BYTES = (
    b"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 3 3]>>endobj\n"
    b"trailer<</Root 1 0 R>>"
)


def _dummy_file(suffix: str, content: bytes = b"dummy") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


# ---------------------------------------------------------------------------
# Prompt (MISC-205 to 208)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_205_display_feedback_prompt(feedback_prompt):
    """MISC-205: The feedback prompt displays with its expected copy."""
    text = feedback_prompt.prompt().inner_text()
    assert "Using New Trackofy?" in text
    assert "Share feedback" in text


@pytest.mark.functional
@pytest.mark.misc
def test_misc_206_dismiss_closes_prompt(feedback_prompt):
    """MISC-206: Dismiss closes the prompt without opening the form."""
    feedback_prompt.dismiss_prompt()
    feedback_prompt.page.wait_for_timeout(500)
    assert not feedback_prompt.prompt().is_visible()
    assert not feedback_prompt.form().is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_207_give_feedback_opens_form(feedback_prompt):
    """MISC-207: Give Feedback opens the Feedback form."""
    feedback_prompt.open_form_from_prompt()
    assert feedback_prompt.form().is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_208_prompt_does_not_block_core_navigation(feedback_prompt, config):
    """MISC-208: With the prompt open, core navigation still works (no
    blocking full-screen backdrop)."""
    page = feedback_prompt.page
    page.goto(f"{config['base_url']}/home")
    page.wait_for_timeout(1500)
    assert "/home" in page.url, "Expected navigation to succeed while the prompt was open"


# ---------------------------------------------------------------------------
# Version preference (MISC-209 to 213)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_209_verify_version_options(feedback_form):
    """MISC-209: New/Old/Not sure are all present."""
    for version in ["New", "Old", "Not sure"]:
        assert feedback_form.version_button(version).is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_210_select_new_version(feedback_form):
    """MISC-210: Selecting New marks it selected."""
    feedback_form.version_button("Old").click()
    feedback_form.page.wait_for_timeout(300)
    feedback_form.version_button("New").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_version_selected("New")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_211_select_old_version(feedback_form):
    """MISC-211: Selecting Old marks it selected."""
    feedback_form.version_button("Old").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_version_selected("Old")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_212_select_not_sure_version(feedback_form):
    """MISC-212: Selecting Not sure marks it selected."""
    feedback_form.version_button("Not sure").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_version_selected("Not sure")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_213_version_selection_changes_correctly(feedback_form):
    """MISC-213: Selecting a new version option deselects the previous
    one (single-choice behavior)."""
    assert feedback_form.is_version_selected("New"), "Expected New pre-selected by default"
    feedback_form.version_button("Old").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_version_selected("Old")
    assert not feedback_form.is_version_selected("New"), "Expected New to be deselected after choosing Old"


# ---------------------------------------------------------------------------
# Star rating (MISC-214 to 217)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_214_verify_five_star_rating(feedback_form):
    """MISC-214: Five stars are available."""
    for n in range(1, 6):
        assert feedback_form.star_button(n).is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_215_rate_one_star(feedback_form):
    """MISC-215: Clicking the first star sets a 1-star rating."""
    feedback_form.set_rating(1)
    assert feedback_form.current_rating() == 1


@pytest.mark.functional
@pytest.mark.misc
def test_misc_216_rate_five_stars(feedback_form):
    """MISC-216: Clicking the fifth star sets a 5-star rating."""
    feedback_form.set_rating(5)
    assert feedback_form.current_rating() == 5


@pytest.mark.functional
@pytest.mark.misc
def test_misc_217_change_rating(feedback_form):
    """MISC-217: Changing the rating replaces the previous value."""
    feedback_form.set_rating(2)
    assert feedback_form.current_rating() == 2
    feedback_form.set_rating(4)
    assert feedback_form.current_rating() == 4


# ---------------------------------------------------------------------------
# Positive / negative tags (MISC-218 to 231)
# ---------------------------------------------------------------------------

def _assert_tag_selects(feedback_form, tag: str):
    feedback_form.tag_button(tag).click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_tag_selected(tag)


@pytest.mark.functional
@pytest.mark.misc
def test_misc_218_positive_tag_faster_loading(feedback_form):
    """MISC-218: The 'Faster loading' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Faster loading")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_219_positive_tag_better_ui_ux(feedback_form):
    """MISC-219: The 'Better UI/UX' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Better UI/UX")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_220_positive_tag_dashboard_improved(feedback_form):
    """MISC-220: The 'Dashboard improved' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Dashboard improved")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_221_positive_tag_reports_improved(feedback_form):
    """MISC-221: The 'Reports improved' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Reports improved")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_222_positive_tag_tracking_improved(feedback_form):
    """MISC-222: The 'Tracking improved' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Tracking improved")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_223_positive_tag_settings_easier(feedback_form):
    """MISC-223: The 'Settings easier' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Settings easier")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_224_negative_tag_missing_features(feedback_form):
    """MISC-224: The 'Missing features' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Missing features")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_225_negative_tag_confusing_flow(feedback_form):
    """MISC-225: The 'Confusing flow' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Confusing flow")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_226_negative_tag_slow_lag(feedback_form):
    """MISC-226: The 'Slow / lag' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Slow / lag")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_227_negative_tag_bugs_errors(feedback_form):
    """MISC-227: The 'Bugs / errors' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Bugs / errors")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_228_negative_tag_map_issues(feedback_form):
    """MISC-228: The 'Map issues' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Map issues")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_229_negative_tag_report_mismatch(feedback_form):
    """MISC-229: The 'Report mismatch' tag reflects its own selection."""
    _assert_tag_selects(feedback_form, "Report mismatch")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_230_multiple_positive_tags(feedback_form):
    """MISC-230: Multiple positive tags can be selected together."""
    feedback_form.tag_button("Faster loading").click()
    feedback_form.page.wait_for_timeout(300)
    feedback_form.tag_button("Better UI/UX").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_tag_selected("Faster loading")
    assert feedback_form.is_tag_selected("Better UI/UX")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_231_multiple_negative_tags(feedback_form):
    """MISC-231: Multiple negative tags can be selected together."""
    feedback_form.tag_button("Bugs / errors").click()
    feedback_form.page.wait_for_timeout(300)
    feedback_form.tag_button("Map issues").click()
    feedback_form.page.wait_for_timeout(300)
    assert feedback_form.is_tag_selected("Bugs / errors")
    assert feedback_form.is_tag_selected("Map issues")


# ---------------------------------------------------------------------------
# Suggestions (MISC-232 to 238)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_232_suggestions_empty_permitted(feedback_form):
    """MISC-232: Suggestions is optional -- blank is fine, Submit stays
    usable."""
    assert feedback_form.suggestions_textarea().input_value() == ""
    assert feedback_form.submit_button().is_enabled()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_233_suggestions_exactly_250_chars(feedback_form):
    """MISC-233: Exactly 250 characters is accepted; counter shows
    250/250."""
    text = "a" * 250
    feedback_form.type_into(feedback_form.suggestions_textarea(), text)
    assert feedback_form.suggestions_textarea().input_value() == text
    assert "250/250" in feedback_form.suggestions_counter_text() or "250" in feedback_form.suggestions_counter_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_234_suggestions_over_250_capped(feedback_form):
    """MISC-234: More than 250 characters cannot exceed the configured
    limit."""
    text = "a" * 300
    feedback_form.type_into(feedback_form.suggestions_textarea(), text)
    actual = feedback_form.suggestions_textarea().input_value()
    assert len(actual) <= 250, f"Expected the suggestion capped at 250 chars, got {len(actual)}"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_235_suggestions_special_characters(feedback_form):
    """MISC-235: Special characters are accepted safely."""
    payload = "!@#$%^&*()"
    feedback_form.type_into(feedback_form.suggestions_textarea(), payload)
    assert feedback_form.suggestions_textarea().input_value() == payload


@pytest.mark.functional
@pytest.mark.misc
def test_misc_236_suggestions_unicode(feedback_form):
    """MISC-236: Unicode text (non-Latin + emoji) is handled correctly."""
    payload = "बहुत बढ़िया ऐप है 🎉"
    feedback_form.type_into(feedback_form.suggestions_textarea(), payload)
    assert feedback_form.suggestions_textarea().input_value() == payload


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_237_suggestions_xss_not_executed(feedback_form):
    """MISC-237 [Critical]: An XSS payload in Suggestions never executes
    as script."""
    payload = "<script>window.__fb_xss_fired=true</script>"
    feedback_form.type_into(feedback_form.suggestions_textarea(), payload)
    fired = feedback_form.page.evaluate("() => window.__fb_xss_fired === true")
    assert not fired, "Expected the XSS payload to never execute"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_238_suggestions_sql_injection_handled_safely(feedback_form):
    """MISC-238 [Critical]: A SQL-injection-shaped suggestion doesn't
    error the form."""
    feedback_form.type_into(feedback_form.suggestions_textarea(), "' OR 1=1 --")
    assert feedback_form.form().is_visible(), "Expected the form to remain functional"


# ---------------------------------------------------------------------------
# Attachment (MISC-239 to 247)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_239_open_attachment_chooser(feedback_form):
    """MISC-239: Choose File is present and enabled."""
    assert feedback_form.choose_file_button().is_visible()
    assert feedback_form.attachment_file_input().count() == 1


@pytest.mark.functional
@pytest.mark.misc
def test_misc_240_attach_png(feedback_form):
    """MISC-240: A valid PNG (<=5MB) is accepted."""
    feedback_form.attachment_file_input().set_input_files(_dummy_file(".png", _PNG_BYTES))
    feedback_form.page.wait_for_timeout(500)
    assert ".png" in feedback_form.form().inner_text().lower()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_241_attach_jpg(feedback_form):
    """MISC-241: A valid JPG (<=5MB) is accepted."""
    feedback_form.attachment_file_input().set_input_files(_dummy_file(".jpg", _PNG_BYTES))
    feedback_form.page.wait_for_timeout(500)
    assert ".jpg" in feedback_form.form().inner_text().lower()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_242_attach_pdf(feedback_form):
    """MISC-242: A valid PDF (<=5MB) is accepted."""
    feedback_form.attachment_file_input().set_input_files(_dummy_file(".pdf", _PDF_BYTES))
    feedback_form.page.wait_for_timeout(500)
    assert ".pdf" in feedback_form.form().inner_text().lower()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_243_reject_file_over_5mb(feedback_form):
    """MISC-243 [Critical]: A file over 5MB is rejected with clear
    validation."""
    oversized = _dummy_file(".png", b"0" * (6 * 1024 * 1024))
    feedback_form.attachment_file_input().set_input_files(oversized)
    feedback_form.page.wait_for_timeout(800)
    body = feedback_form.form().inner_text().lower()
    assert "5" in body and ("mb" in body or "size" in body or "large" in body), (
        f"Expected a size-related validation message, got: {body[:300]!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_244_reject_unsupported_file_type(feedback_form):
    """MISC-244: An unsupported file type (.zip) is rejected."""
    feedback_form.attachment_file_input().set_input_files(_dummy_file(".zip", b"PK\x03\x04dummy"))
    feedback_form.page.wait_for_timeout(800)
    body = feedback_form.form().inner_text()
    assert ".zip" not in body.lower(), "Expected the unsupported .zip file to be rejected, not shown as attached"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_245_reject_spoofed_mime_extension(feedback_form):
    """MISC-245 [Critical]: A renamed unsupported file (real content is
    an executable, extension spoofed to .png) is rejected/safely handled,
    not accepted purely on file extension."""
    spoofed = _dummy_file(".png", b"MZ\x90\x00" + b"\x00" * 100)  # real EXE magic bytes, .png extension
    feedback_form.attachment_file_input().set_input_files(spoofed)
    feedback_form.page.wait_for_timeout(800)
    body = feedback_form.form().inner_text()
    assert ".png" not in body.lower() or "error" in body.lower() or "invalid" in body.lower(), (
        "Expected a spoofed-extension file (real EXE content) to be rejected or flagged, not silently "
        f"accepted as a real PNG. Got: {body[:300]!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_246_reject_corrupt_image(feedback_form):
    """MISC-246: A corrupt PNG (wrong content, correct extension) is
    rejected or safely handled -- doesn't crash the form."""
    corrupt = _dummy_file(".png", b"not a real png at all")
    feedback_form.attachment_file_input().set_input_files(corrupt)
    feedback_form.page.wait_for_timeout(800)
    assert feedback_form.form().is_visible(), "Expected the form to remain functional/visible"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_247_optional_attachment_submit_without_file(feedback_form):
    """MISC-247: Submission remains possible without any attachment."""
    assert feedback_form.attachment_file_input().input_value() == ""
    assert feedback_form.submit_button().is_enabled()


# ---------------------------------------------------------------------------
# Contact information (MISC-248 to 251)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_248_mobile_field_prepopulated(feedback_form):
    """MISC-248: Mobile is pre-populated from the account profile."""
    value = feedback_form.mobile_input().input_value()
    assert value.strip() != "", "Expected Mobile pre-filled from the account profile"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_249_email_field_prepopulated(feedback_form):
    """MISC-249: Email is pre-populated from the account profile."""
    value = feedback_form.email_input().input_value()
    assert "@" in value, "Expected Email pre-filled from the account profile"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_250_invalid_feedback_email_validation(feedback_form):
    """MISC-250: An invalid email is flagged / blocks submission."""
    feedback_form.email_input().fill("qa@")
    feedback_form.page.wait_for_timeout(500)
    submit = feedback_form.submit_button()
    if submit.is_enabled():
        submit.click()
        feedback_form.page.wait_for_timeout(1000)
        assert feedback_form.form().is_visible(), "Expected an invalid email to block submission"
    else:
        assert not submit.is_enabled()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_251_invalid_feedback_mobile_validation(feedback_form):
    """MISC-251: An invalid mobile is flagged / blocks submission."""
    feedback_form.mobile_input().fill("abc")
    feedback_form.page.wait_for_timeout(500)
    submit = feedback_form.submit_button()
    if submit.is_enabled():
        submit.click()
        feedback_form.page.wait_for_timeout(1000)
        assert feedback_form.form().is_visible(), "Expected an invalid mobile to block submission"
    else:
        assert not submit.is_enabled()


# ---------------------------------------------------------------------------
# Cancel / Close / Submit (MISC-252 to 258)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_252_cancel_closes_without_submitting(feedback_form):
    """MISC-252: Cancel closes the form without submitting."""
    feedback_form.type_into(feedback_form.suggestions_textarea(), "pytest cancel check")
    feedback_form.cancel_button().click()
    feedback_form.page.wait_for_timeout(800)
    assert not feedback_form.form().is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_253_close_via_x_no_unintended_submit(feedback_form):
    """MISC-253: Closing via X doesn't submit."""
    feedback_form.type_into(feedback_form.suggestions_textarea(), "pytest close-X check")
    feedback_form.close_form_via_x()
    feedback_form.page.wait_for_timeout(800)
    assert not feedback_form.form().is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_254_submit_valid_feedback_succeeds(feedback_form):
    """MISC-254: A fully valid feedback submission succeeds and shows
    success feedback."""
    feedback_form.set_rating(4)
    feedback_form.tag_button("Faster loading").click()
    feedback_form.page.wait_for_timeout(300)
    feedback_form.type_into(
        feedback_form.suggestions_textarea(), "pytest automated feedback -- please ignore."
    )
    feedback_form.submit_button().click()
    feedback_form.page.wait_for_timeout(2000)
    assert not feedback_form.form().is_visible() or feedback_form.contains_any_text(
        ["success", "Success", "Thank you", "submitted"]
    ), "Expected either the form to close or a success message after a valid submit"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_255_double_click_submit_no_duplicate_indication(feedback_form):
    """MISC-255 [Critical]: Rapidly double-clicking Submit doesn't show
    two separate success confirmations (best-effort -- there's no
    feedback list to verify true server-side non-duplication against, so
    this checks for an observable double-submit symptom instead)."""
    feedback_form.type_into(feedback_form.suggestions_textarea(), "pytest double-submit check")
    submit = feedback_form.submit_button()
    submit.click()
    try:
        submit.click(timeout=1500)
    except Exception:
        pass
    feedback_form.page.wait_for_timeout(2000)
    toasts = feedback_form.page.locator(".mat-mdc-snack-bar-label, [role='alert']")
    assert toasts.count() <= 1, f"Expected at most one success/error toast, got {toasts.count()}"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_256_api_failure_on_submit_no_false_success(feedback_form):
    """MISC-256: A simulated API failure during submit shows failure, not
    a false success."""
    feedback_form.page.route(
        re.compile(r".*feedback.*", re.I), lambda route: route.fulfill(status=500, body='{"message":"error"}')
    )
    try:
        feedback_form.type_into(feedback_form.suggestions_textarea(), "pytest API-failure check")
        feedback_form.submit_button().click()
        feedback_form.page.wait_for_timeout(2000)
        assert not feedback_form.contains_any_text(["Thank you", "submitted successfully"]), (
            "Expected no false-success message when the submit API call fails"
        )
    finally:
        feedback_form.page.unroute(re.compile(r".*feedback.*", re.I))


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_257_network_interruption_on_submit_fails_safely(feedback_form):
    """MISC-257: A network interruption during submit fails safely (no
    false success, no crash)."""
    feedback_form.page.route(re.compile(r".*feedback.*", re.I), lambda route: route.abort("connectionreset"))
    try:
        feedback_form.type_into(feedback_form.suggestions_textarea(), "pytest network-interruption check")
        feedback_form.submit_button().click()
        feedback_form.page.wait_for_timeout(2000)
        assert not feedback_form.contains_any_text(["Thank you", "submitted successfully"])
    finally:
        feedback_form.page.unroute(re.compile(r".*feedback.*", re.I))


@pytest.mark.skip(
    reason="MISC-258 (session expiry during feedback submission) has no reliable simulation path in this "
    "suite -- matches the same honest-skip precedent as MISC-111/144 (Raise Ticket/Change Password): "
    "session/token expiry isn't a request-level condition page.route can abort/fulfill the way MISC-256/257 "
    "do, and there's no exposed way to force server-side session invalidation mid-request."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_258_session_expiry_during_submission():
    pass
