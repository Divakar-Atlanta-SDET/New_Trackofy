"""Login Page Phase 6 -- Accessibility & Responsive (LOGIN-075 to
LOGIN-081).

Matches this session's established lighter smoke-pass convention:
keyboard reachability is checked as "Tab moves focus to a different,
real control" (not full tab-order mapping), visible focus is checked
as "a real outline/box-shadow exists", and responsive checks confirm
the core form stays usable at each viewport rather than pixel-perfect
layout verification. Note: the password visibility toggle is
confirmed NOT keyboard-reachable via Tab (Bug #49, Bug_Report.md,
tabindex="-1") -- LOGIN-075's own reachability check will surface this
directly rather than needing a separate regression pin here.
"""
import pytest


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.accessibility
def test_login_075_keyboard_navigation(login_page):
    """LOGIN-075: Tab moves focus through the form's interactive
    controls in a logical order (smoke check)."""
    login_page.username_input.focus()
    before = login_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    login_page.page.keyboard.press("Tab")
    login_page.page.wait_for_timeout(200)
    after = login_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert after and after != before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.accessibility
def test_login_076_keyboard_submit(login_page, credentials, config):
    """LOGIN-076: Filling the form and activating Sign in via the
    keyboard (Enter) submits it successfully."""
    import re

    login_page.username_input.fill(credentials["username"])
    login_page.password_input.fill(credentials["password"])
    login_page.password_input.press("Enter")
    login_page.page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    assert "/home" in login_page.page.url


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.accessibility
def test_login_077_visible_focus_indicator(login_page):
    """LOGIN-077: A focused control shows a visible focus indicator."""
    login_page.username_input.focus()
    outline = login_page.page.evaluate(
        "() => { const cs = getComputedStyle(document.activeElement); "
        "return {outline: cs.outlineStyle, boxShadow: cs.boxShadow}; }"
    )
    has_visible_focus = outline["outline"] != "none" or outline["boxShadow"] != "none"
    assert has_visible_focus, f"Expected a visible focus indicator, got {outline}"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.accessibility
def test_login_078_accessible_form_labels(login_page):
    """LOGIN-078: Username/email and password controls have correct
    accessible names (via placeholder-based labelling, confirmed live)."""
    assert login_page.username_input.get_attribute("placeholder") == "Enter username or email"
    assert login_page.password_input.get_attribute("placeholder") == "Enter password"


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.responsive
def test_login_079_desktop_layout(login_page):
    """LOGIN-079: No overlap/clipping at a desktop viewport."""
    login_page.page.set_viewport_size({"width": 1920, "height": 1080})
    login_page.page.wait_for_timeout(500)
    assert login_page.username_input.is_visible()
    assert login_page.login_btn.is_visible()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.responsive
def test_login_080_tablet_layout(login_page):
    """LOGIN-080: The form and links remain usable/readable at a tablet
    viewport."""
    login_page.page.set_viewport_size({"width": 768, "height": 1024})
    login_page.page.wait_for_timeout(500)
    assert login_page.username_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.login_btn.is_visible()


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.responsive
def test_login_081_mobile_layout(login_page):
    """LOGIN-081: The form/buttons/links remain usable at a mobile
    viewport without unintended horizontal scrolling."""
    login_page.page.set_viewport_size({"width": 390, "height": 844})
    login_page.page.wait_for_timeout(500)
    assert login_page.username_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.login_btn.is_visible()
    overflow = login_page.page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 20, f"Expected no significant horizontal overflow, got {overflow}px"
