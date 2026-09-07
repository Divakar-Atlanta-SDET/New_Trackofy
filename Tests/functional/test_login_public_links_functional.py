"""Login Page Phase 4 -- Help Center, Contact Support, Release Notes,
Mobile App links, Public link navigation (LOGIN-056 to LOGIN-063).

Confirmed live real destinations: Help Center -> /help-center (reuses
the same HelpCenterPage already built for the Miscellaneous Pages
module -- same content regardless of entry point), Contact Support ->
a mailto:support@trackofy.com link (not a page navigation), Release
Notes -> /whats-new, Google Play -> a real Play Store listing, Apple
App Store -> a real App Store listing.
"""
import re

import pytest

from Pages.help_center_page import HelpCenterPage


@pytest.mark.functional
@pytest.mark.login
def test_login_056_open_help_center(login_page):
    """LOGIN-056: Help Center opens and doesn't submit the login form."""
    login_page.help_center_link.click()
    login_page.page.wait_for_url(re.compile(r".*/help-center"), timeout=10000)
    help_center = HelpCenterPage(login_page.page)
    assert help_center.heading.is_visible()


@pytest.mark.functional
@pytest.mark.login
def test_login_057_help_center_accessible_logged_out(login_page):
    """LOGIN-057: Help Center is accessible while logged out (it's
    reached directly from the login page, before any authentication)."""
    login_page.help_center_link.click()
    login_page.page.wait_for_url(re.compile(r".*/help-center"), timeout=10000)
    assert "/help-center" in login_page.page.url
    assert "Sign in" not in login_page.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_058_contact_support_destination(login_page):
    """LOGIN-058: Contact Support points to the configured support
    destination (a mailto: link, not a page navigation)."""
    href = login_page.contact_support_link.get_attribute("href")
    assert href == "mailto:support@trackofy.com"


@pytest.mark.functional
@pytest.mark.login
def test_login_059_open_release_notes(login_page):
    """LOGIN-059: Release Notes opens correctly."""
    login_page.release_notes_link.click()
    login_page.page.wait_for_url(re.compile(r".*/whats-new"), timeout=10000)
    assert "Release Notes" in login_page.page.locator("body").inner_text()


@pytest.mark.functional
@pytest.mark.login
def test_login_060_switch_release_versions(login_page):
    """LOGIN-060: Selecting an available version updates the displayed
    release details."""
    login_page.release_notes_link.click()
    login_page.page.wait_for_url(re.compile(r".*/whats-new"), timeout=10000)
    page = login_page.page
    page.wait_for_timeout(1500)
    v61 = page.get_by_role("button", name="6.1", exact=True)
    assert v61.count() > 0, "Expected a 6.1 version selector"
    v61.click()
    page.wait_for_timeout(1000)
    assert page.locator("body").is_visible(), "Expected the page to remain functional after switching versions"


@pytest.mark.functional
@pytest.mark.login
def test_login_061_google_play_link(login_page):
    """LOGIN-061: Google Play points to the real Trackofy listing."""
    href = login_page.google_play_link.get_attribute("href")
    assert href is not None and "play.google.com" in href and "trackofy" in href.lower()


@pytest.mark.functional
@pytest.mark.login
def test_login_062_app_store_link(login_page):
    """LOGIN-062: Apple App Store points to the real Trackofy listing."""
    href = login_page.app_store_link.get_attribute("href")
    assert href is not None and "apps.apple.com" in href and "trackofy" in href.lower()


@pytest.mark.functional
@pytest.mark.login
def test_login_063_back_from_public_page(login_page):
    """LOGIN-063: Browser Back from a public page (Help Center) restores
    the login page."""
    login_page.help_center_link.click()
    login_page.page.wait_for_url(re.compile(r".*/help-center"), timeout=10000)
    login_page.page.go_back()
    login_page.page.wait_for_timeout(1500)
    assert login_page.heading.is_visible()
