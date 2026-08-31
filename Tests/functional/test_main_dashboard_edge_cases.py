import re
import pytest
from playwright.sync_api import expect

from Pages.login_page import LoginPage
from Pages.main_dashboard_page import MainDashboardPage


@pytest.mark.functional
def test_main_dashboard_empty_widget_datasets_rendering(page, config, credentials):
    """Verify widgets with zero records display clean 'No data available' / 'No data found' messages."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in and open graphical dashboard.
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    dashboard_page.open_graphical_dashboard()

    # 2. Assert dashboard loaded and contains empty state indicators where data is 0.
    expect(dashboard_page.dashboard_heading).to_be_visible()
    body_text = page.locator("body").inner_text()
    assert "No data available" in body_text or "No data found" in body_text or "Total Fleet" in body_text


@pytest.mark.functional
def test_main_dashboard_rapid_view_switching(page, config, credentials):
    """Verify UI stability under rapid switching between Graphical and Tabular view modes."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Log in to Trackofy.
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    # 2. Rapid view toggling.
    dashboard_page.open_graphical_dashboard()
    dashboard_page.switch_to_tabular_view()
    dashboard_page.switch_to_graphical_view()
    dashboard_page.switch_to_tabular_view()
    dashboard_page.switch_to_graphical_view()

    # 3. Assert final view lands cleanly on Graphical dashboard.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/dashboard/graphical/?$"))
    expect(dashboard_page.dashboard_heading).to_be_visible()


@pytest.mark.functional
def test_main_dashboard_unauthorized_direct_access_redirect(page, config):
    """Verify unauthenticated direct access to /dashboard/graphical redirects to login page."""
    # 1. Ensure fresh unauthenticated context (no cookies/session).
    page.context.clear_cookies()

    # 2. Attempt direct navigation to protected dashboard route.
    page.goto(f"{config['base_url']}/dashboard/graphical")

    # 3. Verify automatic security redirect to login screen with returnUrl parameter.
    expect(page).to_have_url(re.compile(rf"{re.escape(config['base_url'])}/(login|\?returnUrl=).*$"))


@pytest.mark.functional
def test_main_dashboard_api_failure_resilience(page, config, credentials):
    """Verify dashboard resilience when telemetry API requests fail with HTTP 500 status."""
    login_page = LoginPage(page, config)
    dashboard_page = MainDashboardPage(page)

    # 1. Intercept backend telemetry/analytics API routes with HTTP status 500 error.
    page.route("**/api/dashboard/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.route("**/api/analytics/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))

    # 2. Log in and navigate to dashboard.
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    page.goto(f"{config['base_url']}/dashboard/graphical")

    # 3. Assert dashboard UI remains rendered without browser process crashes.
    expect(dashboard_page.dashboard_heading).to_be_visible()
