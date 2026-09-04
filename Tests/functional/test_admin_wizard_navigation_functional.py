import time

import pytest


def _unique_username(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 10_000_000}"


@pytest.mark.functional
@pytest.mark.admin
@pytest.mark.negative
def test_adm_053_close_wizard_without_submit_still_creates_user(administrator_page):
    """Regression pin for Bug #25 (Bug_Report.md, Administrator Module):
    closing the Create User wizard via the X icon -- at any point after
    Step 1, confirmed even after progressing all the way to Step 4 without
    ever clicking Submit -- does not roll back the user that Step 1 already
    persisted server-side. This asserts the confirmed-broken behavior (the
    user count rises by one and the exact username becomes a real row) so
    it should start failing -- and be flipped to assert no user was
    created -- once the app properly rolls back an abandoned wizard.
    """
    admin = administrator_page
    username = _unique_username("pytestclosebug")
    before_count = int(admin.user_count_text() or "0")

    admin.open_add_user_wizard()
    admin.fill_step1(username, "ValidPassword123@", ["HP12G9691"], arm_disarm="No")
    admin.click_next_step()  # Step 1 -> 2: this is where the real save happens
    admin.page.wait_for_timeout(1000)
    admin.close_wizard()
    admin.page.wait_for_timeout(1000)

    admin.page.reload()
    admin.wait_until_ready()
    admin.page.wait_for_timeout(1000)
    after_count = int(admin.user_count_text() or "0")

    assert after_count == before_count + 1, (
        f"Bug #25: closing the wizard after Step 1 without ever clicking Submit should currently "
        f"(still) leave a permanently created user behind -- count was {before_count} before, "
        f"expected {before_count + 1} after, got {after_count}. If this is no longer true, the bug "
        "is fixed and this test should be flipped to assert the count is unchanged."
    )

    admin.change_rows_per_page("50")
    admin.page.wait_for_timeout(1000)
    all_usernames = " ".join(
        admin.user_rows().nth(i).inner_text() for i in range(admin.user_rows().count())
    )
    assert username in all_usernames, (
        f"Bug #25: expected '{username}' (closed mid-wizard, never submitted) to be a real row "
        f"in User Management -- it was not found among {admin.user_rows().count()} rows."
    )
