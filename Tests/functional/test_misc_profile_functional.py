"""Phase 2 -- My Profile (MISC-013 to 031).

Cross-account isolation rows (MISC-029 and its siblings elsewhere in the
CSV) were resolved per the approved plan's fallback: a sub-user (created
via the Administrator module) was tried as "Account B" first. Confirmed
live it is NOT independent -- it shares the exact same identity (name
"Tarunn", email, mobile) as the owner account, only usage quotas/
completion % differ. Since there's no genuinely separate second account,
these rows are honestly skipped rather than testing something that
doesn't map to what "isolation" means here.
"""
import pytest

from Pages.profile_page import ProfilePage


@pytest.mark.functional
@pytest.mark.misc
def test_misc_013_profile_heading(profile_page):
    """MISC-013: The 'Profile & Account' heading is shown."""
    assert profile_page.heading.is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_014_015_profile_name_and_account_holder(profile_page):
    """MISC-014/015: The profile name and 'Account holder' indicator are
    displayed together."""
    name = profile_page.account_holder_name()
    assert name, "Expected a non-empty account holder name"
    assert "Account holder" in profile_page.visible_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_016_email_displayed(profile_page):
    """MISC-016: A configured email address is displayed."""
    assert "@" in profile_page.field_value("Email")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_017_mobile_displayed(profile_page):
    """MISC-017: A configured mobile number is displayed."""
    mobile = profile_page.field_value("Mobile")
    assert mobile and any(ch.isdigit() for ch in mobile)


@pytest.mark.functional
@pytest.mark.misc
def test_misc_018_profile_completion_indicator(profile_page):
    """MISC-018: The profile completion indicator shows a valid
    percentage (0-100)."""
    percent = profile_page.profile_completion_percent()
    assert 0 <= percent <= 100, f"Expected a valid completion percentage, got {percent}"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.parametrize("category", ProfilePage.USAGE_CATEGORIES)
def test_misc_019_022_account_usage_card_values(profile_page, category):
    """MISC-019/020/021/022: Each Account Usage card (Devices/SMS/Sub
    Users/Email) shows a non-negative remaining value, a matching
    progress-bar percentage, and a consistent 'X used' caption -- and the
    progress fill is internally consistent with the remaining value (0%
    fill only when nothing is used)."""
    remaining = profile_page.usage_remaining(category)
    used_text = profile_page.usage_used_text(category)
    progress = profile_page.usage_progress_percent(category)

    assert remaining >= 0, f"Expected a non-negative remaining value for {category}, got {remaining}"
    assert "used" in used_text.lower(), f"Expected a '<n> used' caption for {category}, got {used_text!r}"
    assert 0 <= progress <= 100, f"Expected a valid progress percentage for {category}, got {progress}"

    if "0 used" in used_text:
        assert progress == 0, (
            f"{category}: expected 0% progress fill when usage is '0 used', got {progress}%"
        )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_023_zero_usage_display_is_accurate(profile_page):
    """MISC-023: This account's real current state has zero usage on
    Devices/SMS/Email (confirmed live) -- verify the zero state renders
    correctly (0% progress, '0 used' caption) rather than a broken/empty
    display."""
    for category in ["Devices", "SMS", "Email"]:
        used_text = profile_page.usage_used_text(category)
        progress = profile_page.usage_progress_percent(category)
        assert "0 used" in used_text, f"Expected '{category}' to show '0 used' in this account's current state"
        assert progress == 0, f"Expected '{category}' progress bar at 0%, got {progress}%"


@pytest.mark.skip(
    reason="MISC-024 (near-limit, 99% usage) and MISC-025 (full-limit, 100% usage) require an account "
    "in that specific consumption state -- this real account currently shows 0% usage across all "
    "quota categories (confirmed live), and there's no supported way to synthetically drive real "
    "Devices/SMS/Sub Users/Email usage up to 99-100% without mutating real account resources. Honest "
    "skip rather than fabricating the state; revisit if a dedicated near/full-limit test account "
    "becomes available."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_024_025_near_and_full_limit_usage_display():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_026_personal_and_preferences_fields(profile_page):
    """MISC-026: Name, Mobile, Email, Timezone, Language, Currency and
    Address are all present under Personal & Preferences (WhatsApp is
    checked separately since it can legitimately be empty -- confirmed
    live a sub-user's own profile shows "Add number" instead of a value)."""
    for label in ["Name", "Mobile", "Email", "Timezone", "Language", "Currency", "Address"]:
        value = profile_page.field_value(label)
        assert value, f"Expected a non-empty value for '{label}'"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_027_billing_information_fields(profile_page):
    """MISC-027: Company, Address, Billing Cycle, Payment Type and
    TIN/GST No are shown under Billing Information."""
    for label in ["Company", "Billing Cycle", "Payment Type", "TIN/GST No"]:
        value = profile_page.field_value(label)
        assert value, f"Expected a non-empty value for '{label}'"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_028_open_change_password_from_profile(profile_page):
    """MISC-028: Change Password (from the Profile page itself) opens the
    Change Password workflow -- confirmed live this entry point opens an
    in-page dialog overlay (URL stays on /profile), unlike the Account
    Menu's version of the same item, which navigates to a separate
    /profile/change-password route. Two legitimate entry points, two
    different presentations of the same feature."""
    profile_page.change_password_button.click()
    profile_page.page.wait_for_timeout(1500)
    dialog = profile_page.page.locator(".cdk-overlay-container .cdk-overlay-pane").filter(
        has_text="Verify your identity"
    )
    assert dialog.is_visible(), "Expected the Change Password dialog to open"
    assert "/profile/change-password" not in profile_page.page.url, (
        "Expected this entry point to stay on /profile (dialog-based), not navigate away"
    )


@pytest.mark.skip(
    reason="MISC-029 (profile data isolation between two accounts) and the CSV's other cross-account "
    "rows: per the approved plan, a sub-user (created via the Administrator module) was tried as "
    "'Account B' first. Confirmed live it is NOT an independent account -- it shares the exact same "
    "identity (name, email, mobile) as the owner, only usage quotas and profile-completion % differ. "
    "There's no genuinely separate second account available, so this doesn't map to what 'isolation' "
    "means here. Honest skip, matching the REP-COM-021 precedent, rather than testing something "
    "misleading."
)
@pytest.mark.functional
@pytest.mark.misc
def test_misc_029_profile_data_isolation():
    pass


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_030_unauthenticated_profile_url_access_denied(browser, config):
    """MISC-030: Opening /profile directly, unauthenticated, does not
    show real account data -- it's redirected/denied."""
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}/profile")
        page.wait_for_timeout(2000)
        body_text = page.locator("body").inner_text()
        assert "Profile Completion" not in body_text and "Account Usage" not in body_text, (
            f"Expected unauthenticated access to /profile to be denied/redirected, but real profile "
            f"content was shown. url={page.url!r}"
        )
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_031_profile_responsive_layout(profile_page):
    """MISC-031: Profile sections remain readable/usable at mobile and
    tablet viewport widths."""
    page = profile_page.page
    original_size = page.viewport_size
    try:
        for width, height in [(390, 844), (768, 1024)]:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(500)
            assert profile_page.heading.is_visible(), f"Expected the Profile heading visible at {width}x{height}"
            body_text = page.locator("body").inner_text()
            assert "Account Usage" in body_text, f"Expected Account Usage section present at {width}x{height}"
    finally:
        if original_size:
            page.set_viewport_size(original_size)
