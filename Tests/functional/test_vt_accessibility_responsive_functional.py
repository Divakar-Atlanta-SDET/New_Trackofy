"""Video Telematics Phase 11 -- Accessibility & Responsive (VT-214 to
VT-222).

Lighter smoke pass matching the Miscellaneous Pages module's own
Phase 11 treatment: keyboard reachability is checked as "Tab moves
focus to a different, real control" (not full tab-order mapping),
visible focus is checked as "a real outline/box-shadow exists, not
outline:none with nothing else", and responsive checks confirm the
key surface remains visible/usable at tablet and mobile viewports
rather than pixel-perfect layout verification.
"""
import pytest


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_214_keyboard_dashboard_controls(vt_dashboard_page):
    """VT-214: Dashboard controls are keyboard reachable."""
    vt_dashboard_page.live_video_vehicle_select.focus()
    before = vt_dashboard_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    vt_dashboard_page.page.keyboard.press("Tab")
    vt_dashboard_page.page.wait_for_timeout(200)
    after = vt_dashboard_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert after and after != before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_215_keyboard_alert_form(vt_alert_page):
    """VT-215: The Create Alert dialog's controls are reachable via Tab
    in a logical order."""
    vt_alert_page.open_create_dialog()
    dialog = vt_alert_page.create_dialog()
    vt_alert_page.vehicle_combobox(dialog).focus()
    before = vt_alert_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    vt_alert_page.page.keyboard.press("Tab")
    vt_alert_page.page.wait_for_timeout(200)
    after = vt_alert_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert after and after != before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_216_keyboard_playback_controls(vt_playback_page):
    """VT-216: Playback filter controls are keyboard reachable."""
    vt_playback_page.vehicle_select.focus()
    before = vt_playback_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    vt_playback_page.page.keyboard.press("Tab")
    vt_playback_page.page.wait_for_timeout(200)
    after = vt_playback_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert after and after != before, "Expected Tab to move focus to a different control"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_217_keyboard_report_evidence(vt_report_page):
    """VT-217: Report evidence action icons are keyboard reachable."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    row = None
    for i in range(rows.count()):
        if vt_report_page.row_has_evidence(rows.nth(i)):
            row = rows.nth(i)
            break
    assert row is not None
    evidence_button = row.get_by_role("button").nth(1)
    evidence_button.focus()
    focused_html = vt_report_page.page.evaluate("() => document.activeElement && document.activeElement.outerHTML")
    assert focused_html and "mattooltip" in focused_html, "Expected the evidence icon itself to be focusable"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_218_evidence_icon_labels(vt_report_page):
    """VT-218: The eye/snapshots/play evidence icons carry real,
    descriptive tooltips (Angular Material's mattooltip, wired to
    aria-describedby for assistive tech), not just a raw icon name."""
    vt_report_page.generate()
    rows = vt_report_page.rows()
    row = None
    for i in range(rows.count()):
        if vt_report_page.row_has_evidence(rows.nth(i)):
            row = rows.nth(i)
            break
    assert row is not None
    buttons = row.get_by_role("button")
    expected_tooltips = ["View all evidence", "View snapshots", "Play video"]
    for i, expected in enumerate(expected_tooltips, start=1):
        tooltip = buttons.nth(i).get_attribute("mattooltip")
        assert tooltip == expected, f"Expected evidence icon {i} tooltip {expected!r}, got {tooltip!r}"
        described_by = buttons.nth(i).get_attribute("aria-describedby")
        assert described_by, f"Expected evidence icon {i} wired to an aria-describedby for assistive tech"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.accessibility
def test_vt_visible_focus_indicator(vt_dashboard_page):
    """Bug #46 (Bug_Report.md, Low): the vehicle/channel combobox
    controls' custom styling shows no visible focus indicator at all
    (no outline, no box-shadow, no focus-related ancestor class) --
    pinned here as the current real (broken) behavior."""
    vt_dashboard_page.live_video_vehicle_select.focus()
    outline = vt_dashboard_page.page.evaluate(
        "() => { const cs = getComputedStyle(document.activeElement); "
        "return {outline: cs.outlineStyle, boxShadow: cs.boxShadow}; }"
    )
    has_visible_focus = outline["outline"] != "none" or outline["boxShadow"] != "none"
    assert not has_visible_focus, (
        f"Bug #46: expected no visible focus indicator (if this now fails, the app has been fixed), got {outline}"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.responsive
def test_vt_219_dashboard_responsive(vt_dashboard_page):
    """VT-219: The Dashboard remains usable at a tablet viewport. (Mobile
    is covered by Bug #47's regression pin, test_vt_bug47_mobile_nav_drawer_traps_content,
    below -- the Dashboard's real content is hidden behind an
    auto-opened, undismissable navigation drawer at that width.)"""
    vt_dashboard_page.page.set_viewport_size({"width": 768, "height": 1024})
    vt_dashboard_page.page.wait_for_timeout(500)
    assert vt_dashboard_page.heading.is_visible(), "Expected the Dashboard usable at 768x1024"


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.responsive
def test_vt_220_alert_dialog_responsive(vt_alert_page):
    """VT-220: The Create Alert dialog remains usable at tablet and
    mobile viewports."""
    for width, height in [(768, 1024), (390, 844)]:
        vt_alert_page.page.set_viewport_size({"width": width, "height": height})
        vt_alert_page.page.wait_for_timeout(500)
        vt_alert_page.open_create_dialog()
        dialog = vt_alert_page.create_dialog()
        assert dialog.is_visible(), f"Expected the Create Alert dialog usable at {width}x{height}"
        vt_alert_page.cancel_dialog(dialog)
        vt_alert_page.page.wait_for_timeout(300)


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.responsive
def test_vt_221_playback_responsive(vt_playback_page):
    """VT-221: The Playback page's panels remain usable at a tablet
    viewport. (Mobile is covered by Bug #47's regression pin below.)"""
    vt_playback_page.page.set_viewport_size({"width": 768, "height": 1024})
    vt_playback_page.page.wait_for_timeout(500)
    assert vt_playback_page.heading.is_visible(), "Expected Playback usable at 768x1024"
    assert vt_playback_page.playback_files_heading.is_visible()
    assert vt_playback_page.playback_video_heading.is_visible()


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.responsive
def test_vt_bug47_mobile_nav_drawer_traps_content(vt_dashboard_page):
    """Bug #47 (Bug_Report.md, Medium): at a 390x844 mobile viewport,
    Video Telematics' left-nav renders as an open overlay drawer by
    default, leaving the real page heading present in the DOM but with
    a zero-width bounding box (not visible) -- and the drawer's own
    "Close navigation menu" button renders outside the viewport,
    un-clickable, so it can't even be dismissed. Pinned here as the
    current real (broken) behavior."""
    page = vt_dashboard_page.page
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(800)
    assert not vt_dashboard_page.heading.is_visible(), (
        "Bug #47: expected the Dashboard heading hidden behind the auto-opened drawer "
        "(if this now fails, the app has been fixed)"
    )
    close_button = page.get_by_role("button", name="Close navigation menu")
    assert close_button.count() > 0
    box = close_button.bounding_box()
    assert box is None or box["x"] < 0 or box["x"] + box["width"] > 390, (
        "Bug #47: expected the drawer's own Close button positioned outside the viewport"
    )


@pytest.mark.functional
@pytest.mark.video_telematics
@pytest.mark.responsive
def test_vt_222_report_responsive(vt_report_page):
    """VT-222: The Report page's filters and table remain usable at
    tablet and mobile viewports."""
    for width, height in [(768, 1024), (390, 844)]:
        vt_report_page.page.set_viewport_size({"width": width, "height": height})
        vt_report_page.page.wait_for_timeout(500)
        assert vt_report_page.heading.is_visible(), f"Expected the Report page usable at {width}x{height}"
        assert vt_report_page.generate_button.is_visible()
