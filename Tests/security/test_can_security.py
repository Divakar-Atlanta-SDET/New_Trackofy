"""CAN module -- Security.

Unauthenticated direct-URL access uses the same fresh-context pattern
established for Video Telematics (Tests/functional/test_vt_security_functional.py)
and other modules this session. Cross-account access (a non-CAN account
hitting /can/* routes) uses the main TEST_USERNAME account, which is
confirmed live to have no CAN nav entry -- a genuine different-privilege
account, unlike the cross-account IDOR cases skipped elsewhere in this
suite for lack of a real second account.
"""
import pytest


@pytest.mark.security
@pytest.mark.can
@pytest.mark.negative
@pytest.mark.parametrize(
    "path,heading_name",
    [
        ("/can/dashboard", "CAN Dashboard"),
        ("/can/units", "CAN Units"),
        ("/can/trends", "CAN Trends"),
        ("/can/report", "CAN Report"),
        ("/can/alerts", "CAN Alerts"),
        ("/can/settings", "CAN Alert Settings"),
    ],
)
def test_can_sec_001_unauthenticated_direct_url_access_denied(browser, config, path, heading_name):
    ctx = browser.new_context(base_url=config["base_url"])
    page = ctx.new_page()
    try:
        page.goto(f"{config['base_url']}{path}")
        page.wait_for_timeout(2000)
        assert heading_name not in page.locator("body").inner_text(), (
            f"Unauthenticated access to {path} showed real CAN content (heading {heading_name!r})"
        )
    finally:
        ctx.close()


@pytest.mark.security
@pytest.mark.can
@pytest.mark.negative
def test_can_sec_002_non_can_account_has_no_can_nav_link(page, config, credentials):
    from Pages.login_page import LoginPage
    import re

    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    can_nav_link = page.get_by_role("link", name="CAN")
    assert can_nav_link.count() == 0 or not can_nav_link.first.is_visible(), (
        "The main (non-CAN) test account unexpectedly has a visible CAN nav link"
    )


@pytest.mark.security
@pytest.mark.can
@pytest.mark.negative
@pytest.mark.parametrize(
    "path,heading_name",
    [
        ("/can/dashboard", "CAN Dashboard"),
        ("/can/units", "CAN Units"),
        ("/can/report", "CAN Report"),
    ],
)
def test_can_sec_003_non_can_account_direct_url_access_denied(page, config, credentials, path, heading_name):
    from Pages.login_page import LoginPage
    import re

    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    page.goto(f"{config['base_url']}{path}")
    page.wait_for_timeout(2000)
    assert heading_name not in page.locator("body").inner_text(), (
        f"Non-CAN account was shown real CAN content ({heading_name!r}) at {path}"
    )
