import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_053_close_wizard_without_submit_creates_no_user(administrator_page):
    """Regression pin for Bug_Report.md #25 (Administrator Module).
    Reverified live (2026-09-13, 4x total: 3 independent manual diagnostic
    runs plus this pin): FIXED -- Step 1 -> Step 2's "Next Step" no longer
    fires a save_subuser (or any other save-shaped) API call at all,
    confirmed via full network-response logging. Closing the wizard via the
    "X" icon after progressing all the way through Step 4 (menu group,
    permissions, unit selection) without ever clicking Submit now correctly
    creates no user -- the count is unchanged and the attempted username
    never appears in User Management. If this regresses (count rises, or
    the username reappears), the wizard is saving before final Submit again.
    """
    admin = administrator_page
    username = _unique_username("pytestclosebug")
    before_count = int(admin.user_count_text() or "0")

    admin.open_add_user_wizard()
    admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
    admin.click_next_step()  # Step 1 -> 2
    admin.select_menu_group("example21")
    admin.click_next_step()  # Step 2 -> 3
    admin.click_next_step()  # Step 3 -> 4
    admin.open_units_dropdown()
    admin.select_unit("HP12G9691")
    admin.close_units_dropdown()
    admin.page.wait_for_timeout(1000)
    admin.close_wizard()
    admin.page.wait_for_timeout(1000)

    admin.page.reload(); admin.reopen()
    admin.wait_until_ready()
    admin.page.wait_for_timeout(1000)
    after_count = int(admin.user_count_text() or "0")

    assert after_count == before_count, (
        f"Bug #25 regression: closing the wizard at Step 4 without ever clicking Submit should "
        f"create no user -- count was {before_count} before, expected it to stay {before_count}, "
        f"got {after_count}."
    )

    admin.change_rows_per_page("50")
    admin.page.wait_for_timeout(1000)
    all_usernames = " ".join(
        admin.user_rows().nth(i).inner_text() for i in range(admin.user_rows().count())
    )
    assert username not in all_usernames, (
        f"Bug #25 regression: '{username}' (closed mid-wizard, never submitted) should not appear "
        f"as a row in User Management, but it does."
    )
