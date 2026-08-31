import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.tracking_page import TrackingPage


@pytest.mark.edgecase
def test_trk_nav_010_viewport_resize(page, config, credentials):
    """TRK-NAV-010: Edge Case - Change browser viewport after opening Tracking."""
    login_page = LoginPage(page, config)
    tracking_page = TrackingPage(page)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    tracking_page.open_tracking_page()
    page.set_viewport_size({"width": 1024, "height": 768})
    expect(tracking_page.map_container).to_be_visible()
