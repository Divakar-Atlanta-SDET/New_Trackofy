"""Phase 1 -- Account Menu (MISC-001 to 012)."""
import pytest


@pytest.mark.functional
@pytest.mark.misc
def test_misc_001_open_account_menu(account_menu):
    """MISC-001: Clicking the avatar/icon opens the Account menu."""
    account_menu.open()
    assert account_menu.is_open(), "Expected the Account menu to open"
    dialog_text = account_menu.page.locator("body").inner_text()
    assert "Profile & preferences" in dialog_text


@pytest.mark.functional
@pytest.mark.misc
def test_misc_002_close_account_menu_by_reclicking(account_menu):
    """MISC-002: Clicking the avatar icon again closes the menu."""
    account_menu.open()
    assert account_menu.is_open()
    account_menu.menu_trigger.click()
    account_menu.page.wait_for_timeout(500)
    assert not account_menu.my_profile_item.is_visible(), "Expected the menu to close on re-click"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_003_close_menu_by_clicking_outside(account_menu):
    """MISC-003: Clicking outside the menu closes it without navigating."""
    account_menu.open()
    assert account_menu.is_open()
    before_url = account_menu.page.url
    account_menu.page.mouse.click(10, 10)
    account_menu.page.wait_for_timeout(500)
    assert not account_menu.my_profile_item.is_visible(), "Expected the menu to close on outside click"
    assert account_menu.page.url == before_url, "Clicking outside should not navigate"


@pytest.mark.functional
@pytest.mark.misc
def test_misc_004_open_my_profile(account_menu):
    """MISC-004: My Profile navigates to /profile."""
    account_menu.open_my_profile()
    assert "/profile" in account_menu.page.url
    assert "Profile & Account" in account_menu.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_005_open_downloads(account_menu):
    """MISC-005: Downloads navigates to /profile/downloads."""
    account_menu.open_downloads()
    assert "/profile/downloads" in account_menu.page.url
    assert "Downloads" in account_menu.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_006_open_support(account_menu):
    """MISC-006: Support navigates to /profile/support."""
    account_menu.open_support()
    assert "/profile/support" in account_menu.page.url
    assert "Support Management" in account_menu.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_007_open_change_password(account_menu):
    """MISC-007: Change Password navigates to /profile/change-password."""
    account_menu.open_change_password()
    assert "/profile/change-password" in account_menu.page.url
    assert "Verify your identity" in account_menu.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_008_toggle_appearance(account_menu):
    """MISC-008: Appearance toggles the theme immediately, without
    navigating away."""
    before_url = account_menu.page.url
    before_theme = account_menu.current_theme()
    account_menu.toggle_appearance()
    after_theme = account_menu.current_theme()
    assert after_theme != before_theme, f"Expected theme to toggle from {before_theme!r}"
    assert account_menu.page.url == before_url, "Appearance should not navigate"
    # restore original theme so it doesn't leak into other tests
    account_menu.toggle_appearance()
    assert account_menu.current_theme() == before_theme


@pytest.mark.functional
@pytest.mark.misc
def test_misc_009_open_language(account_menu):
    """MISC-009: Language opens a real dialog listing supported languages."""
    account_menu.open_language_dialog()
    dialog_text = account_menu.language_dialog().inner_text()
    for lang in ["English", "Hindi", "Arabic", "Japanese", "Korean", "Spanish", "French"]:
        assert lang in dialog_text, f"Expected '{lang}' listed in the Language dialog"
    account_menu.page.keyboard.press("Escape")


@pytest.mark.functional
@pytest.mark.misc
def test_misc_010_sign_out(browser, config, credentials):
    """MISC-010: Signing out (confirming the logout dialog) ends the
    session and clears auth-related localStorage keys."""
    from Pages.login_page import LoginPage
    from Pages.account_menu_page import AccountMenuPage

    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        login = LoginPage(page, config)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_timeout(2000)
        assert "/home" in page.url

        menu = AccountMenuPage(page)
        menu.sign_out()
        page.wait_for_timeout(1500)

        assert "/home" not in page.url, f"Expected to leave /home after confirmed sign-out, got {page.url!r}"
        auth_keys = page.evaluate("() => Object.keys(localStorage)")
        assert "token" not in auth_keys, f"Expected the auth token cleared from localStorage, got keys={auth_keys}"
    finally:
        ctx.close()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_010b_cancel_sign_out_keeps_session(account_menu):
    """Cancel on the sign-out confirmation keeps the session active."""
    account_menu.cancel_sign_out()
    account_menu.page.wait_for_timeout(500)
    assert "/home" in account_menu.page.url, "Expected to remain on /home after Cancel (still logged in)"
    # still authenticated: reopening the account menu should work normally
    account_menu.open()
    assert account_menu.is_open()


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.accessibility
def test_misc_011_account_menu_keyboard_navigation(account_menu):
    """MISC-011: The Account menu's items are reachable and operable via
    keyboard (Tab + Enter), not mouse-only."""
    account_menu.menu_trigger.focus()
    account_menu.page.keyboard.press("Enter")
    account_menu.page.wait_for_timeout(600)
    assert account_menu.is_open(), "Expected Enter on the focused trigger to open the menu"

    account_menu.page.keyboard.press("Tab")
    account_menu.page.wait_for_timeout(300)
    focused_text = account_menu.page.evaluate("() => document.activeElement && document.activeElement.innerText")
    assert focused_text, "Expected a real element to receive focus after Tab inside the open menu"
    account_menu.page.keyboard.press("Escape")


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_012_account_menu_responsive_tablet(account_menu):
    """MISC-012: At a tablet viewport width, the Account menu remains
    reachable and usable."""
    page = account_menu.page
    original_size = page.viewport_size
    try:
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(500)
        account_menu.open()
        assert account_menu.is_open(), "Expected the menu to open at tablet width (768x1024)"
        assert account_menu.my_profile_item.is_visible(), "Expected My Profile visible at tablet width"
        account_menu.close()
    finally:
        if original_size:
            page.set_viewport_size(original_size)


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
@pytest.mark.negative
def test_misc_012b_bug34_account_menu_unreachable_at_mobile_width(account_menu):
    """Regression pin for Bug #34 (Bug_Report.md, Miscellaneous Pages
    Module): at a phone-sized viewport (390x844), the account_circle
    trigger becomes invisible and no alternative control (hamburger menu,
    "Actions" panel) reaches My Profile/Support/Change Password/Language/
    Sign Out. This asserts the confirmed-broken (unreachable) state; it
    should start failing -- and be flipped to assert the menu IS reachable
    -- once the app is fixed.
    """
    page = account_menu.page
    original_size = page.viewport_size
    try:
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(800)
        assert not account_menu.menu_trigger.is_visible(), (
            "Bug #34: the Account menu trigger should currently (still) be invisible at mobile width. "
            "If it's now visible, the app has been fixed and this test should be flipped."
        )
        body_text = page.locator("body").inner_text()
        for missing_item in ["My Profile", "Support", "Change Password", "Sign Out"]:
            assert missing_item not in body_text, (
                f"Bug #34: '{missing_item}' should currently (still) be unreachable at mobile width, "
                f"but it appeared in the page text -- the app may have been fixed."
            )
    finally:
        if original_size:
            page.set_viewport_size(original_size)
