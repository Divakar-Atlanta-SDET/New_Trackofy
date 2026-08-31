import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.tracking_page import TrackingPage


@pytest.mark.negative
def test_trk_nav_009_initial_tracking_load_failure(page, config, credentials):
    """TRK-NAV-009: Negative - Intercept initial tracking config API failure."""
    login_page = LoginPage(page, config)
    tracking_page = TrackingPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    tracking_page.open_tracking_page()
    expect(tracking_page.map_container).to_be_visible()
