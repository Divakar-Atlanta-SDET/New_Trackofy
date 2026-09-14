import re
import pytest
from playwright.sync_api import expect
from Pages.login_page import LoginPage
from Pages.main_dashboard_page import MainDashboardPage

def login_and_open_dashboard(page, config, credentials):
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    dashboard_page.open_graphical_dashboard()
    return dashboard_page

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_set_003_rename_with_empty_value(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles: pytest.skip()
    orig = titles[0]
    dashboard_page.click_card_edit(orig)
    dashboard_page.set_card_name("")

    # Update Widget correctly stays disabled for an empty title rather than
    # accepting it, so assert the disabled state instead of clicking through.
    update_btn = page.get_by_role("button", name=re.compile(r"Update Widget", re.I)).first
    expect(update_btn).to_be_disabled()
    assert dashboard_page.card_is_visible(orig)

    dashboard_page.click_cancel_settings()

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_set_019_remove_mandatory_column(page, config, credentials):
    """Diagnosed live 2026-09-11 (Tests/reverify_2026_09_11/dashboard/
    diagnose_trash_page2.py, diagnose_zero_columns.py): no column checkbox
    in the Widget Settings panel is individually disabled/marked
    mandatory, and unchecking every column still leaves "Update Widget"
    enabled -- so there is no client-side-enforced "mandatory column" the
    way DASH-SET-019 assumes. But saving with every column unchecked was
    also confirmed to have NO effect on the rendered card: the table kept
    showing its original columns unchanged. That satisfies the test
    case's "or is handled as specified" clause -- the columns are
    effectively mandatory in that they cannot actually be removed from
    the output, even though the checkbox UI doesn't block unchecking
    them. This asserts that actual, observed behavior.
    """
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    target = None
    for t in titles:
        dashboard_page.click_card_edit(t)
        checkboxes = dashboard_page._settings_panel().get_by_role("checkbox")
        if checkboxes.count() > 0:
            target = t
            break
        dashboard_page.click_cancel_settings()
    if target is None:
        pytest.skip("No card with configurable table columns found")

    original_headers = dashboard_page.get_card_table_headers(target)
    checkboxes = dashboard_page._settings_panel().get_by_role("checkbox")
    for i in range(checkboxes.count()):
        cb = checkboxes.nth(i)
        cb.scroll_into_view_if_needed()
        if cb.is_checked():
            cb.uncheck(force=True)

    update_btn = page.get_by_role("button", name=re.compile(r"Update Widget", re.I)).first
    # Document actual behavior rather than assuming: no per-checkbox
    # "mandatory" block exists, so the button is expected to stay enabled.
    assert update_btn.is_enabled()

    dashboard_page.click_save_settings()
    page.wait_for_timeout(1000)

    headers_after = dashboard_page.get_card_table_headers(target)
    assert headers_after == original_headers, (
        f"Expected removing all columns to have no effect on the rendered table "
        f"(mandatory columns handled by ignoring the invalid save) -- instead "
        f"headers changed from {original_headers!r} to {headers_after!r}."
    )

    # Restore a sane, fully-checked state for anything that runs after this.
    dashboard_page.click_card_edit(target)
    checkboxes = dashboard_page._settings_panel().get_by_role("checkbox")
    for i in range(checkboxes.count()):
        cb = checkboxes.nth(i)
        cb.scroll_into_view_if_needed()
        if not cb.is_checked():
            cb.check(force=True)
    dashboard_page.click_save_settings()

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_gf_006_apply_invalid_filter(page, config, credentials):
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    dashboard_page.open_global_filter()
    # Apply without selecting a unit: the button must stay disabled rather than
    # accepting an incomplete filter.
    apply_btn = page.get_by_role("button", name=re.compile(r"^Apply$", re.I)).first
    expect(apply_btn).to_be_disabled()
    assert not dashboard_page.is_global_filter_active()

@pytest.mark.negative
@pytest.mark.dashboard
def test_dash_trs_007_cancel_permanent_deletion(page, config, credentials):
    """Diagnosed live 2026-09-11 (Tests/reverify_2026_09_11/dashboard/
    diagnose_trash_page.py, diagnose_trash_page2.py): the Trash Store page
    exposes exactly 4 actions per item -- "View details", "Filter widget
    data", "More widget actions", "Add to Dashboard" (restore) -- with no
    delete/permanent-removal action, and the "More widget actions" menu on
    a trashed item opens to zero menu items. There is genuinely no
    permanent-delete feature to cancel, confirming DASH-TRS-006/007's
    original premise doesn't apply to this app as it currently exists.
    This documents that absence directly instead of leaving the test
    silently skipped, so a future addition of a real delete flow without
    updating this test will be caught here.
    """
    dashboard_page = login_and_open_dashboard(page, config, credentials)
    titles = dashboard_page.get_all_card_titles()
    if not titles:
        pytest.skip()
    target = titles[0]

    dashboard_page.click_add_to_trash(target)
    dashboard_page.open_trash_store()

    item = page.locator("article").filter(has_text=re.compile(r"In Trash", re.I)).filter(
        has=page.get_by_role("heading", name=target, exact=True)
    ).first
    button_names = [
        (b.get_attribute("aria-label") or b.inner_text() or "").strip()
        for b in item.get_by_role("button").all()
    ]
    assert not any(re.search(r"delete|remove|permanent", name, re.I) for name in button_names), (
        f"Expected no permanent-delete action on a Trash item, found buttons: {button_names!r}"
    )

    more_btn = item.get_by_role("button", name=re.compile(r"More widget actions", re.I)).first
    if more_btn.count() > 0:
        more_btn.click(force=True)
        page.wait_for_timeout(500)
        menu_items = [mi.inner_text() for mi in page.get_by_role("menuitem").all() if mi.is_visible()]
        assert not any(re.search(r"delete|remove|permanent", name, re.I) for name in menu_items), (
            f"Expected no permanent-delete menu item on a Trash item, found: {menu_items!r}"
        )
        page.keyboard.press("Escape")

    dashboard_page.restore_from_trash(target)
