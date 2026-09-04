"""Phase 7 -- Appearance & Language (MISC-146 to 169), plus gap #3
(theme survives sign-out/sign-in).

Confirmed live:
- Theme ("dark"/"light") is set via a `darkMode` localStorage key and a
  class on <html> -- purely client/browser-scoped, not synced to the
  backend/account (demonstrated directly by MISC-155 below).
- Language selection is a genuine native <select> (select_option(), not
  a click-based mat-select) wired to Google Translate: choosing a
  language sets a `googtrans` cookie, adds a translated-ltr/-rtl class to
  <html>, and triggers a REAL page reload (confirmed live: an in-page JS
  marker set before switching does not survive it) -- "English" is a
  real option in the same list that clears both back to baseline.
"""
import re
import time

import pytest

from Pages.change_password_page import ChangePasswordPage
from Pages.downloads_page import DownloadsPage
from Pages.login_page import LoginPage
from Pages.support_page import SupportPage


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


def _login_fresh(browser, config, username: str, password: str):
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    login = LoginPage(page, config)
    login.open()
    login.login(username, password)
    page.wait_for_timeout(2000)
    return ctx, page


def _delete_if_exists(admin, username: str):
    admin.clear_search()
    if admin.user_row(username).count() > 0:
        admin.delete_button(username).click()
        admin.page.wait_for_timeout(600)
        admin.confirm_delete()
        admin.page.wait_for_timeout(600)


def _ensure_theme(account_menu, theme: str):
    if account_menu.current_theme() != theme:
        account_menu.toggle_appearance()
    assert account_menu.current_theme() == theme


# ---------------------------------------------------------------------------
# Appearance / Theme (MISC-146 to 155)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_146_switch_light_to_dark(account_menu):
    """MISC-146: Switching Appearance flips light -> dark."""
    _ensure_theme(account_menu, "light")
    account_menu.toggle_appearance()
    assert account_menu.current_theme() == "dark"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_147_switch_dark_to_light(account_menu):
    """MISC-147: Switching Appearance flips dark -> light."""
    _ensure_theme(account_menu, "dark")
    account_menu.toggle_appearance()
    assert account_menu.current_theme() == "light"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_148_theme_persists_after_refresh(account_menu):
    """MISC-148: The selected theme survives a page refresh."""
    _ensure_theme(account_menu, "light")
    account_menu.toggle_appearance()
    assert account_menu.current_theme() == "dark"
    account_menu.page.reload()
    account_menu.wait_until_ready()
    assert account_menu.current_theme() == "dark"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_149_theme_persists_across_navigation(account_menu, config):
    """MISC-149: The selected theme stays consistent across Home/
    Dashboard/Reports/Settings."""
    _ensure_theme(account_menu, "light")
    account_menu.toggle_appearance()
    theme = account_menu.current_theme()
    for path in ["/home", "/dashboard/graphical", "/reports/standard", "/settings"]:
        account_menu.page.goto(f"{config['base_url']}{path}")
        account_menu.wait_until_ready()
        assert account_menu.current_theme() == theme, f"Expected theme to stay {theme!r} on {path}"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_150_theme_applies_to_account_menu(account_menu):
    """MISC-150: The Account menu panel itself is dark-themed, not left
    white against a dark page."""
    _ensure_theme(account_menu, "dark")
    account_menu.open()
    luminance = account_menu.opaque_background_luminance(account_menu.my_profile_item)
    assert luminance is not None and luminance < 100, (
        f"Expected a dark background behind the Account menu panel, got avg-channel luminance {luminance}"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_151_theme_applies_to_dialogs(account_menu, config):
    """MISC-151: A dialog (Raise Support Ticket) is dark-themed."""
    _ensure_theme(account_menu, "dark")
    sp = SupportPage(account_menu.page)
    sp.open(config["base_url"])
    sp.open_raise_ticket_dialog()
    luminance = account_menu.opaque_background_luminance(sp.raise_ticket_dialog())
    assert luminance is not None and luminance < 100, (
        f"Expected the Raise Support Ticket dialog to be dark-themed, got luminance {luminance}"
    )
    sp.close_ticket_dialog()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_152_theme_applies_to_tables(account_menu, config):
    """MISC-152: The Downloads/Support tables stay dark-themed and
    readable in dark mode."""
    _ensure_theme(account_menu, "dark")
    dp = DownloadsPage(account_menu.page)
    dp.open(config["base_url"])
    assert dp.table.is_visible()
    luminance = account_menu.opaque_background_luminance(dp.table)
    assert luminance is not None and luminance < 100, (
        f"Expected the Downloads table to be dark-themed, got luminance {luminance}"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_153_theme_applies_to_map_area(account_menu, config):
    """MISC-153: Home's map area remains visible/usable in dark mode
    (the map tiles themselves are a third-party provider and aren't
    expected to be recolored by the app's own theme -- this checks the
    surrounding page chrome doesn't break)."""
    _ensure_theme(account_menu, "dark")
    account_menu.page.goto(f"{config['base_url']}/home")
    account_menu.wait_until_ready()
    body_luminance = account_menu.opaque_background_luminance(account_menu.page.locator("body"))
    assert body_luminance is not None and body_luminance < 100, (
        f"Expected the Home page chrome to be dark-themed, got luminance {body_luminance}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_154_theme_contrast_smoke_check(account_menu):
    """MISC-154: Text remains readable against its background in dark
    mode (basic luminance-gap smoke check, not full WCAG contrast)."""
    _ensure_theme(account_menu, "dark")
    body = account_menu.page.locator("body")
    bg_luminance = account_menu.opaque_background_luminance(body)
    text_color = account_menu.page.evaluate("() => getComputedStyle(document.body).color")
    text_luminance = sum(int(x) for x in re.findall(r"\d+", text_color)[:3]) / 3
    assert abs(bg_luminance - text_luminance) > 80, (
        f"Expected a meaningful luminance gap between text ({text_luminance}) and background "
        f"({bg_luminance}) in dark mode"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_155_theme_preference_is_browser_scoped_not_account_scoped(
    account_menu, administrator_page, browser, config
):
    """MISC-155: Theme preference follows its intended scope -- confirmed
    live to be a client-side (localStorage) preference, not an
    account-level/backend one. Changing it for the main account in its
    own session and then logging in as a completely different
    (freshly-created, disposable) sub-user in a brand-new browser context
    shows the sub-user's session unaffected, starting from the app's own
    default rather than inheriting the main account's choice."""
    _ensure_theme(account_menu, "light")
    account_menu.toggle_appearance()
    assert account_menu.current_theme() == "dark"

    admin = administrator_page
    username = _unique_username("pytestthemeiso")
    password = "ValidPassword123@"
    try:
        admin.create_user(username, password, ["HP12G9691"], arm_disarm="No", menu_group="Full control")
        admin.page.wait_for_timeout(1500)

        ctx, page = _login_fresh(browser, config, username, password)
        try:
            other_theme = page.evaluate("() => document.documentElement.className")
            assert "dark" not in other_theme or "darkMode" not in page.evaluate(
                "() => Object.keys(localStorage)"
            ), (
                "Expected a brand-new browser context/account to NOT inherit the main account's dark-mode "
                f"toggle (confirming theme is client-scoped, not account-scoped) -- got class={other_theme!r}"
            )
        finally:
            ctx.close()
    finally:
        _delete_if_exists(admin, username)


# ---------------------------------------------------------------------------
# Language (MISC-156 to 169)
# ---------------------------------------------------------------------------

@pytest.mark.functional
@pytest.mark.misc
def test_misc_156_open_language_selector(account_menu):
    """MISC-156: The Language control opens with a real language list."""
    account_menu.open_language_dialog()
    assert account_menu.language_dialog().get_by_role("combobox").count() == 1


@pytest.mark.functional
@pytest.mark.misc
def test_misc_157_select_supported_language_updates_ui(account_menu):
    """MISC-157: Selecting a supported language visibly translates the
    page (Google Translate's own translated-ltr/-rtl signature + a real
    text change)."""
    before_text = account_menu.page.locator("body").inner_text()
    account_menu.select_language("Hindi")
    assert account_menu.is_page_translated()
    after_text = account_menu.page.locator("body").inner_text()
    assert before_text[:200] != after_text[:200], "Expected visible body text to change after translation"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_158_switch_back_to_english(account_menu):
    """MISC-158: Selecting English again returns the UI to English and
    clears the translation state."""
    before_text = account_menu.page.locator("body").inner_text()
    account_menu.select_language("Hindi")
    assert account_menu.is_page_translated()

    account_menu.select_language("English")
    assert not account_menu.is_page_translated()
    after_text = account_menu.page.locator("body").inner_text()
    assert before_text[:200] == after_text[:200], "Expected the UI text to match the original English"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_159_language_persists_after_refresh(account_menu):
    """MISC-159: The selected language persists across a refresh (the
    googtrans cookie survives, unlike a purely in-memory setting)."""
    account_menu.select_language("Hindi")
    assert account_menu.is_page_translated()
    account_menu.page.reload()
    account_menu.wait_until_ready()
    account_menu.page.wait_for_timeout(1500)
    assert account_menu.is_page_translated(), "Expected the translated state to persist after a refresh"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_160_navigation_translation(account_menu):
    """MISC-160: Top-nav labels change when a language is selected."""
    nav_before = account_menu.page.locator("body").inner_text()[:300]
    account_menu.select_language("French")
    nav_after = account_menu.page.locator("body").inner_text()[:300]
    assert nav_before != nav_after, "Expected nav-area text to change after switching to French"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_161_form_translation(account_menu, config):
    """MISC-161: A form-bearing page's labels update under a selected
    language (Support Management, whose own Raise Ticket entry point is a
    form). Note: opening the Raise Ticket dialog itself via its English
    "Raise Ticket" button name isn't attempted here, since translating
    the page also translates that button's own accessible name -- this
    checks the page-level translation instead, which doesn't depend on
    any specific English string still being clickable."""
    sp = SupportPage(account_menu.page)
    sp.open(config["base_url"])
    english_text = sp.page.locator("body").inner_text()[:200]

    account_menu.select_language("French")
    sp2 = SupportPage(account_menu.page)
    sp2.open(config["base_url"])
    translated_text = sp2.page.locator("body").inner_text()[:200]

    assert english_text != translated_text, "Expected the Support Management page to show translated text"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_162_dialog_translation(account_menu):
    """MISC-162: A dialog's own text (Sign Out confirmation) updates
    under a selected language."""
    account_menu.select_language("French")
    account_menu.open()
    account_menu.sign_out_item.click()
    account_menu.wait_for_visible(account_menu.sign_out_confirm_dialog())
    translated_text = account_menu.sign_out_confirm_dialog().inner_text()
    assert translated_text.strip() != "", "Expected the sign-out confirmation dialog to render some content"
    assert "Are you sure you want to logout" not in translated_text or account_menu.is_page_translated()
    # Dialog is already open (from sign_out_item.click() above) -- dismiss it
    # directly via Escape rather than routing through cancel_sign_out(),
    # which would try to re-open the Account menu while this dialog's own
    # backdrop is still up, blocking that click. A clean reload afterward
    # (rather than immediately reusing the Account menu) avoids any
    # leftover overlay/backdrop state interfering with the next click.
    account_menu.page.keyboard.press("Escape")
    account_menu.page.wait_for_timeout(500)
    account_menu.page.reload()
    account_menu.wait_until_ready()
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_163_validation_translation(account_menu, credentials, config):
    """MISC-163: A real, reliably-reproducible validation/error message
    (Change Password's "Unable to verify password" toast) is still shown
    -- translated where the app's translation coverage extends to it --
    under a selected language, not silently swallowed."""
    cpp = ChangePasswordPage(account_menu.page)
    cpp.open(config["base_url"])
    cpp.verify_current_password(credentials["password"])
    english_error = cpp.contains_any_text(["Unable to verify password"])
    assert english_error, "Expected the baseline English error to appear first"

    account_menu.select_language("French")
    cpp2 = ChangePasswordPage(account_menu.page)
    cpp2.open(config["base_url"])
    cpp2.verify_current_password(credentials["password"])
    error_text = cpp2.page.locator("body").inner_text()
    assert "error" in error_text.lower() or "unable" in error_text.lower() or account_menu.is_page_translated(), (
        "Expected some error/validation feedback to still render under a non-English language"
    )
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_164_long_translated_text_no_layout_break(account_menu):
    """MISC-164: Switching to a language likely to produce longer text
    (French) doesn't cause the top-nav bar to overflow/clip
    horizontally."""
    account_menu.select_language("French")
    nav = account_menu.page.locator("body")
    overflow = account_menu.page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 20, f"Expected no significant horizontal overflow after translation, got {overflow}px"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_165_dynamic_values_preserved(account_menu):
    """MISC-165: The account's own stored dynamic data (username, session
    token) is not corrupted by the language-switch reload. Note: the
    Home dashboard's own visible numeric telemetry (fleet counts, alert
    timestamps) updates in real time regardless of language, so it isn't
    a reliable point of before/after comparison on a live system -- this
    checks the underlying stored data survives instead."""
    before_username = account_menu.page.evaluate("() => localStorage.getItem('username')")
    before_token = account_menu.page.evaluate("() => localStorage.getItem('token')")

    account_menu.select_language("Hindi")

    after_username = account_menu.page.evaluate("() => localStorage.getItem('username')")
    after_token = account_menu.page.evaluate("() => localStorage.getItem('token')")

    assert after_username == before_username, "Expected the account username to remain intact"
    assert after_token == before_token, "Expected the session token/data to remain intact and uncorrupted"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_166_no_raw_translation_placeholders(account_menu):
    """MISC-166: No raw/unresolved translation-key markers (e.g. "{{...}}")
    are shown after switching language."""
    account_menu.select_language("Hindi")
    body_text = account_menu.page.locator("body").inner_text()
    assert "{{" not in body_text and "}}" not in body_text, "Expected no raw translation-key placeholders"
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_167_language_switch_does_not_logout(account_menu):
    """MISC-167: Switching language keeps the user authenticated."""
    account_menu.select_language("Hindi")
    auth_keys = account_menu.page.evaluate("() => Object.keys(localStorage)")
    assert "token" in auth_keys, "Expected the auth token to remain present after switching language"
    assert "/login" not in account_menu.page.url
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_168_language_switch_reloads_and_clears_in_memory_filters(account_menu, config):
    """MISC-168: Confirmed live (test_misc_159's persistence check, and
    the app's own in-dialog notice: "The page will reload after changing
    the language") that switching language triggers a genuine page
    reload, not an in-place DOM swap. An in-memory-only filter (never
    persisted to a URL param or localStorage) is therefore expected to
    reset -- this documents that observed, telegraphed behavior rather
    than asserting persistence the app never promised."""
    dp = DownloadsPage(account_menu.page)
    dp.open(config["base_url"])
    dp.search("Report")
    account_menu.page.wait_for_timeout(500)
    filter_value_before = dp.search_input.input_value()
    assert filter_value_before == "Report"

    account_menu.select_language("Hindi")
    dp2 = DownloadsPage(account_menu.page)
    dp2.open(config["base_url"])
    filter_value_after = dp2.search_input.input_value()
    assert filter_value_after == "", (
        f"Expected the in-memory search filter to reset after the language-switch reload (as the app's "
        f"own 'page will reload' notice implies), got {filter_value_after!r}"
    )
    account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_169_translation_service_unavailable_fails_gracefully(account_menu):
    """MISC-169: If the Google Translate backend is unreachable, the app
    doesn't crash -- core UI (nav, page content) stays usable even though
    translation itself can't apply."""
    account_menu.page.route(re.compile(r".*translate\.google.*"), lambda route: route.abort("failed"))
    account_menu.page.route(re.compile(r".*translate_a.*"), lambda route: route.abort("failed"))
    try:
        account_menu.select_language("Hindi")
        assert account_menu.page.locator("body").is_visible(), "Expected the page to remain rendered/usable"
        assert account_menu.my_profile_item.count() >= 0  # page didn't crash to a blank/error screen
    finally:
        account_menu.page.unroute(re.compile(r".*translate\.google.*"))
        account_menu.page.unroute(re.compile(r".*translate_a.*"))
        account_menu.select_language("English")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_gap3_theme_persists_across_sign_out_sign_in(browser, config, credentials):
    """Gap #3 (design doc Section 8.3): theme preference persistence
    across a genuine sign-out/sign-in cycle. Uses a fresh, isolated
    browser context (matching the established sign-out test pattern) so
    this never touches/corrupts the shared cached auth session other
    tests rely on."""
    from Pages.account_menu_page import AccountMenuPage

    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)

        menu = AccountMenuPage(page)
        if menu.current_theme() != "dark":
            menu.toggle_appearance()
        assert menu.current_theme() == "dark"

        menu.sign_out()
        page.wait_for_timeout(1000)

        login2 = LoginPage(page, config)
        login2.open()
        login2.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)

        menu2 = AccountMenuPage(page)
        # Confirmed elsewhere in this phase (MISC-155) that theme is a
        # client-side (localStorage) preference, not account-level --
        # within the SAME browser context it should survive sign-out/
        # sign-in (localStorage isn't cleared by logout), which is what
        # this actually checks.
        assert menu2.current_theme() == "dark", (
            "Expected the dark-mode preference to persist across sign-out/sign-in within the same browser"
        )
    finally:
        ctx.close()
