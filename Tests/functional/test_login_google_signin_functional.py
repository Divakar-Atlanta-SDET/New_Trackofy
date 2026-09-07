"""Login Page Phase 3 -- Google Sign-In (LOGIN-050 to LOGIN-055).

Confirmed live and with the user: Google Sign-In does not exist in the
live app at all. There is no "Sign in with Google" button, no "Google"
text anywhere on the login page. Interestingly, a Google Identity
Services `g_state` cookie is still present after a page load, meaning
the underlying SDK is still loaded even though the UI entry point was
removed (a developer decision, not a bug). Every LOGIN-050 to 055 case
is therefore honestly skipped rather than faked -- there's nothing to
test.
"""
import pytest


@pytest.mark.functional
@pytest.mark.login
def test_login_050_no_google_signin_control(login_page):
    """LOGIN-050 (adjusted): confirmed live there is no "Sign in with
    Google" control on the login page -- pinned as the current real
    state (feature removed) rather than skipped, since this itself is
    a real, checkable fact."""
    assert "Google" not in login_page.visible_text(), (
        "Expected no Google Sign-In text on the login page (if this now fails, the feature may have returned)"
    )


@pytest.mark.functional
@pytest.mark.login
@pytest.mark.skip(reason="LOGIN-051 to 055: Google Sign-In does not exist in the live app (confirmed with the user) -- there is no control to exercise successful auth, cancellation, provider failure, popup blocking, or OAuth callback failure against")
def test_login_051_055_google_signin_flows():
    pass
