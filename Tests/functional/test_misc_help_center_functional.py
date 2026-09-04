"""Phase 9 -- Help Center (MISC-179 to 204).

Confirmed live: Bug #38 (Bug_Report.md, High) -- the main "Search
articles, guides and FAQs..." search always returns "0 found", even for
a guaranteed-matching term ("device", the literal name of a real,
independently-browsable category). Every Quick Link, Popular Section,
and Common Issue shortcut routes through this same broken search and
lands on the identical "0 found" dead end -- confirmed for one
representative item from each group. The sidebar's own separate
"Search contents..." mini-filter (which narrows the Categories &
Articles list) works correctly by contrast, which is what isolates the
bug to the main search integration rather than the underlying data.
"""
import pytest


@pytest.mark.functional
@pytest.mark.misc
def test_misc_179_open_help_center_from_launcher(authenticated_page, config):
    """MISC-179: Help Center opens from the 9-dot app launcher."""
    from Pages.help_center_page import HelpCenterPage

    authenticated_page.goto(f"{config['base_url']}/home")
    authenticated_page.wait_for_timeout(1000)
    hc = HelpCenterPage(authenticated_page)
    hc.open_via_launcher()
    assert hc.heading.is_visible()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_180_overview_content_visible(help_center_page):
    """MISC-180: The landing page shows Overview/categories, Quick Links,
    Popular Sections, and Common Issues."""
    body = help_center_page.visible_text()
    assert "Overview" in body
    assert "Quick links" in body
    assert "Popular sections" in body
    assert "Common issues" in body


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_bug38_main_search_always_returns_zero_results(help_center_page):
    """Regression pin for Bug #38 (Bug_Report.md, High): the main search
    always returns "0 found", even for "device" -- a term guaranteed to
    match (it's the real name of a browsable category with a real
    article under it). Asserts the confirmed-broken behavior; flip once
    fixed."""
    help_center_page.search("device")
    assert help_center_page.search_result_count() == 0, (
        "Bug #38: expected the main search to (still) return 0 results even for a guaranteed-matching "
        "term. If it now returns real results, the app has been fixed -- un-skip MISC-181/182/188-201."
    )
    assert help_center_page.is_no_results_shown()

    # Isolates the bug: the sidebar's own mini-filter works correctly for
    # the exact same term, proving the underlying data/other search path
    # is fine.
    help_center_page.sidebar_search_input.click()
    help_center_page.page.keyboard.type("device", delay=20)
    help_center_page.page.wait_for_timeout(800)
    assert "Device" in help_center_page.visible_text(), (
        "Expected the sidebar's own category filter to correctly find 'Device' for the same term"
    )


@pytest.mark.functional
@pytest.mark.misc
def test_misc_183_search_no_result_term(help_center_page):
    """MISC-183: A deliberately nonsense search term shows a no-result
    state. Note: due to Bug #38, this currently passes for the "wrong"
    reason (search always returns 0), but a no-result state for a
    genuinely unmatched term is also the correct, expected behavior on
    its own, so this remains meaningful."""
    help_center_page.search("xyz-no-result")
    assert help_center_page.is_no_results_shown()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_184_search_empty_handled_without_error(help_center_page):
    """MISC-184: Submitting an empty search is handled without a UI
    error/crash."""
    help_center_page.main_search_input.click()
    help_center_page.page.keyboard.press("Enter")
    help_center_page.page.wait_for_timeout(800)
    assert help_center_page.heading.is_visible(), "Expected the page to remain intact after an empty search"


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_185_search_special_characters_no_ui_error(help_center_page):
    """MISC-185: Searching special characters doesn't throw a visible UI
    error."""
    help_center_page.search("@#$")
    assert help_center_page.heading.is_visible()
    assert "error" not in help_center_page.visible_text().lower().split("no results found")[0]


@pytest.mark.functional
@pytest.mark.misc
def test_misc_186_open_device_category(help_center_page):
    """MISC-186: The Device category opens with its real article list."""
    help_center_page.open_category_and_wait("Device")
    body = help_center_page.visible_text()
    assert "Available Articles" in body
    assert "articles" in body.lower()


@pytest.mark.functional
@pytest.mark.misc
def test_misc_187_open_sensor_category(help_center_page):
    """MISC-187: The Sensor category opens with its own content."""
    help_center_page.open_category_and_wait("Sensor")
    body = help_center_page.visible_text()
    assert "Available Articles" in body


_BLOCKED_REASON = (
    "is blocked by Bug #38 (Bug_Report.md, High): Help Center's main search always returns 0 results, "
    "and this shortcut routes through that same broken search rather than opening real content. "
    "Un-skip once Bug #38 is fixed -- see test_misc_bug38_main_search_always_returns_zero_results."
)


@pytest.mark.skip(reason=f"MISC-188 (Quick Link: Device Setup) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_188_quick_link_device_setup():
    pass


@pytest.mark.skip(reason=f"MISC-189 (Quick Link: Sensor Configuration) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_189_quick_link_sensor_configuration():
    pass


@pytest.mark.skip(reason=f"MISC-190 (Quick Link: Reports) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_190_quick_link_reports():
    pass


@pytest.mark.skip(reason=f"MISC-191 (Quick Link: Alerts) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_191_quick_link_alerts():
    pass


@pytest.mark.skip(reason=f"MISC-192 (Quick Link: Video Telematics) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_192_quick_link_video_telematics():
    pass


@pytest.mark.skip(reason=f"MISC-193 (Quick Link: Live Tracking) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_193_quick_link_live_tracking():
    pass


@pytest.mark.skip(reason=f"MISC-194 (Popular section: Live Tracking & Map) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_194_popular_live_tracking():
    pass


@pytest.mark.skip(reason=f"MISC-195 (Popular section: Device & Protocol Help) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_195_popular_device():
    pass


@pytest.mark.skip(reason=f"MISC-196 (Popular section: Sensors & Parameters) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_196_popular_sensor():
    pass


@pytest.mark.skip(reason=f"MISC-197 (Popular section: Reports & Analytics) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_197_popular_reports():
    pass


@pytest.mark.skip(reason=f"MISC-198 (Common issue: Vehicle not showing live location) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_198_common_issue_live_location():
    pass


@pytest.mark.skip(reason=f"MISC-199 (Common issue: Report data is missing) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_199_common_issue_missing_report():
    pass


@pytest.mark.skip(reason=f"MISC-200 (Common issue: Alert is not triggering) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_200_common_issue_alert():
    pass


@pytest.mark.skip(reason=f"MISC-201 (Common issue: Sensor value looks incorrect) {_BLOCKED_REASON}")
@pytest.mark.functional
@pytest.mark.misc
def test_misc_201_common_issue_sensor():
    pass


@pytest.mark.functional
@pytest.mark.misc
def test_misc_202_home_button_returns_to_app(help_center_page, config):
    """MISC-202: The Home button returns to the main Trackofy application
    (not just an in-page 'overview' reset)."""
    help_center_page.home_button.click()
    help_center_page.page.wait_for_timeout(1500)
    assert "/help-center" not in help_center_page.page.url, (
        f"Expected Home to leave the Help Center, got {help_center_page.page.url!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.negative
def test_misc_203_bug39_browser_back_leaves_help_center_entirely(help_center_page):
    """Regression pin for Bug #39 (Bug_Report.md, Low): opening a
    category is a pure in-page state change (confirmed live: the URL
    stays exactly /help-center, no new history entry). MISC-203 expects
    Back to restore the Help Center landing state, but since no history
    entry was pushed for the category view, Back instead leaves Help
    Center entirely and lands on whatever page preceded it. Asserts the
    confirmed-broken behavior; flip once fixed."""
    landing_url = help_center_page.page.url
    help_center_page.open_category_and_wait("Device")
    assert help_center_page.page.url == landing_url, (
        "Expected opening a category to NOT change the URL (confirming no history entry is pushed)"
    )

    help_center_page.page.go_back()
    help_center_page.page.wait_for_timeout(1000)
    body = help_center_page.visible_text()
    assert "Quick links" not in body, (
        "Bug #39: expected Back to (still) leave Help Center entirely rather than restore its landing "
        f"state. If 'Quick links' is now shown, the app has been fixed. Got url={help_center_page.page.url!r}"
    )


@pytest.mark.functional
@pytest.mark.misc
@pytest.mark.responsive
def test_misc_204_help_center_responsive(help_center_page):
    """MISC-204: The Help Center sidebar/content remain usable across
    desktop, tablet, and mobile viewports."""
    page = help_center_page.page
    for width, height in [(1440, 900), (768, 1024), (390, 844)]:
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_timeout(500)
        assert help_center_page.heading.is_visible(), f"Expected the Help Center heading visible at {width}x{height}"
        assert "Quick links" in help_center_page.visible_text(), (
            f"Expected the main content still usable at {width}x{height}"
        )
