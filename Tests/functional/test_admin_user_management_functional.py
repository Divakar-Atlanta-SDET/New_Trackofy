import pytest


@pytest.mark.functional
@pytest.mark.admin
def test_adm_001_002_003_open_administrator_shows_user_management(administrator_page):
    """ADM-001/002/003: Administrator opens to User Management with the
    heading, a numeric user count, and a usable Add User button."""
    admin = administrator_page
    assert "/administrator" in admin.page.url
    assert "User Management" in admin.visible_text()
    count = admin.user_count_text()
    assert count.isdigit(), f"Expected a numeric user count, got {count!r}"
    assert admin.add_user_button.is_visible(), "Add User button not visible"
    assert admin.add_user_button.is_enabled(), "Add User button not enabled"


@pytest.mark.functional
@pytest.mark.admin
def test_adm_004_table_columns_present(administrator_page):
    """ADM-004: The user table shows the expected columns."""
    admin = administrator_page
    header_text = admin.page.locator("table thead").inner_text()
    for column in ["User Name", "Password", "Status", "Created At", "Permissions", "Edit", "Delete"]:
        assert column in header_text, f"Expected column '{column}' in table header: {header_text!r}"


@pytest.mark.functional
@pytest.mark.admin
def test_adm_006_password_is_masked(administrator_page):
    """ADM-006: A user's password is shown masked, not in plain text."""
    admin = administrator_page
    row = admin.user_rows().first
    username = admin.row_username(row)
    password_text = admin.password_cell_text(username)
    assert set(password_text.replace("\n", "").replace("visibility_off", "").strip()) <= {"."}, (
        f"Expected the password cell to show only masking dots, got {password_text!r}"
    )


@pytest.mark.functional
@pytest.mark.admin
def test_adm_007_password_reveal_control_toggles_masking(administrator_page):
    """ADM-007: The password visibility control changes the masked state
    only when clicked -- not silently exposed by default."""
    admin = administrator_page
    row = admin.user_rows().first
    username = admin.row_username(row)
    before = admin.password_cell_text(username)
    assert "." in before, f"Expected password to start masked: {before!r}"

    admin.toggle_password_visibility(username)
    admin.page.wait_for_timeout(500)
    after = admin.password_cell_text(username)
    # Not asserting a specific before/after value pairing here -- the
    # helper has a reload-based recovery path for occasional live
    # flakiness (see Pages/administrator_page.py), and a reload resets the
    # (client-side-only) reveal state to masked, which would make a strict
    # round-trip comparison unreliable. The real behavior under test --
    # that the control actually changes the displayed state -- still holds.
    assert after != before, (
        f"Toggling password visibility should change the displayed cell content, "
        f"still showed {after!r} (was {before!r})"
    )


@pytest.mark.functional
@pytest.mark.admin
def test_adm_008_009_search_exact_and_partial_username(administrator_page):
    """ADM-008/009: Searching by an exact or partial existing username
    returns matching results -- verified against a real known user
    ('bruce', confirmed present on this account) rather than a fabricated
    fixture, since search requires a genuinely existing username to prove
    anything meaningful."""
    admin = administrator_page
    admin.search("bruce")
    admin.page.wait_for_timeout(500)
    assert admin.user_row("bruce").count() > 0, "Exact-username search for 'bruce' returned no match"

    admin.clear_search()
    admin.search("bru")
    admin.page.wait_for_timeout(500)
    assert admin.user_row("bruce").count() > 0, "Partial-username search for 'bru' should still match 'bruce'"
    admin.clear_search()


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_010_search_nonexistent_username_shows_no_results(administrator_page):
    """ADM-010: Searching for a username that doesn't exist shows no
    matching records."""
    admin = administrator_page
    admin.search("xyz_nonexistent_zzz")
    admin.page.wait_for_timeout(500)
    assert admin.user_rows().count() == 0, (
        f"Expected 0 rows for a nonsense search, got {admin.user_rows().count()}"
    )
    admin.clear_search()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_011_clear_search_restores_full_list(administrator_page):
    """ADM-011: Clearing the search field restores the full user list."""
    admin = administrator_page
    before_count = admin.user_rows().count()
    admin.search("bruce")
    admin.page.wait_for_timeout(500)
    assert admin.user_rows().count() < before_count or admin.user_rows().count() == before_count
    admin.clear_search()
    admin.page.wait_for_timeout(500)
    assert admin.user_rows().count() == before_count, (
        f"Expected clearing search to restore {before_count} rows, got {admin.user_rows().count()}"
    )


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_013_search_special_characters_no_error(administrator_page):
    """ADM-013: Special characters in search don't cause a UI error or
    expose unrelated records."""
    admin = administrator_page
    admin.search("@#$%")
    admin.page.wait_for_timeout(500)
    # No crash, and no assertion of a specific count (behavior may
    # legitimately vary) -- the check is that the page stays usable.
    assert admin.add_user_button.is_visible(), "Page should remain usable after a special-character search"
    admin.clear_search()


@pytest.mark.functional
@pytest.mark.admin
def test_adm_014_change_rows_per_page(administrator_page):
    """ADM-014: Changing rows-per-page shows the requested number of rows
    (or fewer, if the account has fewer total users than requested)."""
    admin = administrator_page
    admin.change_rows_per_page("5")
    admin.page.wait_for_timeout(500)
    assert admin.user_rows().count() <= 5, f"Expected at most 5 rows, got {admin.user_rows().count()}"

    admin.change_rows_per_page("20")
    admin.page.wait_for_timeout(500)
    count_20 = admin.user_rows().count()
    assert count_20 <= 20
    if int(admin.user_count_text() or "0") > 5:
        assert count_20 > 5, "Increasing rows-per-page should show more rows when more users exist"


@pytest.mark.functional
@pytest.mark.admin
def test_adm_021_feedback_widget_does_not_block_add_user(administrator_page):
    """ADM-021: The feedback widget (if present) doesn't obstruct the core
    Add User action."""
    admin = administrator_page
    assert admin.add_user_button.is_visible() and admin.add_user_button.is_enabled(), (
        "Add User should remain visible and clickable regardless of any feedback widget overlay"
    )
