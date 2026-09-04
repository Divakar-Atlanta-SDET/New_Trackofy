import os
import re
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from config.settings import load_config
from Pages.login_page import LoginPage
from Pages.unit_page import UnitPage
from Pages.unit_settings_page import UnitSettingsPage
from Pages.tracking_page import TrackingPage
from Pages.settings_page import SettingsSideMenu
from Pages.driver_page import DriverPage
from Pages.driver_performance_page import DriverPerformancePage
from Pages.vehicle_group_page import VehicleGroupPage
from Pages.vehicle_performance_page import VehiclePerformancePage
from Pages.location_control_page import LocationControlPage
from Pages.alert_config_page import AlertConfigPage, GeofenceAlertPage, AisAlertPage
from Pages.route_page import RouteManagementPage
from Pages.reports_page import ReportsPage
from Pages.home_page import HomePage
from Pages.administrator_page import AdministratorPage
from Pages.account_menu_page import AccountMenuPage
from Pages.profile_page import ProfilePage
from Pages.downloads_page import DownloadsPage
from Pages.support_page import SupportPage
from Pages.change_password_page import ChangePasswordPage
from Pages.help_center_page import HelpCenterPage
from Pages.feedback_page import FeedbackPage


load_dotenv()

AUTH_STATE_DIR = Path(__file__).parent / ".auth"
AUTH_STATE_MAX_AGE_SECONDS = 30 * 60


def _track_server_errors(page):
    """Record any 5xx response from an XHR/fetch call so the test fails with
    the response logged, instead of silently continuing past a real API error."""
    errors = []

    def _on_response(response):
        if response.request.resource_type not in ("xhr", "fetch") or response.status < 500:
            return
        try:
            body = response.text()
        except Exception:
            body = "<body unavailable>"
        errors.append(f"{response.request.method} {response.url} -> {response.status}\n{body}")

    page.on("response", _on_response)
    return errors


def _assert_no_server_errors(request, errors):
    if request.node.get_closest_marker("allow_server_error"):
        return
    assert not errors, "Application API returned Internal Server Error during test:\n\n" + "\n\n".join(errors)


class NetworkMonitor:
    def __init__(self, page):
        self.page = page
        self._events = []
        self._enabled = False
        self.page.on("response", self._handle_response)

    def _handle_response(self, response):
        if not self._enabled:
            return
        self._events.append(
            {
                "method": response.request.method,
                "resource_type": response.request.resource_type,
                "status": response.status,
                "url": response.url,
            }
        )

    def start(self):
        self._enabled = True

    def stop(self):
        self._enabled = False

    def clear(self):
        self._events.clear()

    def response_events(self, method=None, status=None, resource_type=None):
        events = self._events
        if method is not None:
            events = [event for event in events if event["method"] == method]
        if status is not None:
            events = [event for event in events if event["status"] == status]
        if resource_type is not None:
            events = [event for event in events if event["resource_type"] == resource_type]
        return events

    def discard_issues(self, method=None, status=None, url_contains=None):
        self._events = [
            event
            for event in self._events
            if not (
                (method is None or event["method"] == method)
                and (status is None or event["status"] == status)
                and (url_contains is None or url_contains in event["url"])
            )
        ]


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Environment to run tests against",
    )
    parser.addoption(
        "--session-mode",
        action="store",
        choices=["fresh", "single"],
        default="fresh",
        help=(
            "fresh (default): every test logs in via the UI from scratch, matching "
            "current/existing behavior. single: all tests share one cached login "
            "session (one real UI login per worker, reused) -- faster, but less "
            "representative of a real per-user session. Applies to every test via "
            "the `page` and `authenticated_page` fixtures, with no per-test changes "
            "needed."
        ),
    )


@pytest.fixture(scope="session")
def session_mode(request) -> str:
    return request.config.getoption("--session-mode")


def pytest_configure(config):
    config.addinivalue_line("markers", "functional: functional workflow tests")
    config.addinivalue_line("markers", "positive: positive scenario tests")
    config.addinivalue_line("markers", "negative: negative scenario tests")
    config.addinivalue_line("markers", "edgecase: edge case boundary tests")
    config.addinivalue_line("markers", "reports: reports module tests")
    config.addinivalue_line("markers", "report_generation: report generation tests")
    config.addinivalue_line("markers", "home: home module tests")
    config.addinivalue_line("markers", "admin: administrator module tests")
    config.addinivalue_line("markers", "misc: miscellaneous pages module tests")
    config.addinivalue_line("markers", "accessibility: accessibility smoke checks")
    config.addinivalue_line("markers", "responsive: responsive-viewport smoke checks")
    config.addinivalue_line(
        "markers", "allow_server_error: test intentionally mocks/triggers a server error, skip the global 5xx check"
    )



@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def config(request):
    environment = request.config.getoption("--env")

    return load_config(environment)


@pytest.fixture(scope="session")
def browser(playwright, config):
    browser = playwright.chromium.launch(
        headless=config["headless"]
    )

    yield browser

    browser.close()


@pytest.fixture
def page(request, browser, config, session_mode):
    from Utils.download_helper import attach_download_handler

    context_kwargs = {"base_url": config["base_url"], "accept_downloads": True}
    if session_mode == "single":
        # Lazily resolve auth_storage_state only in single-session mode, so
        # fresh mode (the default) never pays for the throwaway login that
        # fixture performs on its first use each session.
        auth_storage_state = request.getfixturevalue("auth_storage_state")
        context_kwargs["storage_state"] = str(auth_storage_state)

    context = browser.new_context(**context_kwargs)

    page = context.new_page()
    attach_download_handler(page)
    errors = _track_server_errors(page)

    yield page

    context.close()
    _assert_no_server_errors(request, errors)


@pytest.fixture(scope="session")
def auth_storage_state(worker_id, playwright, config, credentials):
    """One real UI login per pytest-xdist worker, cached to a worker-specific
    file so tests reuse the session instead of logging in through the UI every
    time. Keyed by worker_id (xdist gives each worker its own process/file, so
    there's no shared-file race -- 'master' when not running under xdist).
    """
    AUTH_STATE_DIR.mkdir(exist_ok=True)
    state_path = AUTH_STATE_DIR / f"state_{worker_id}.json"

    if state_path.exists() and time.time() - state_path.stat().st_mtime < AUTH_STATE_MAX_AGE_SECONDS:
        return state_path

    browser = playwright.chromium.launch(headless=config["headless"])
    context = browser.new_context(base_url=config["base_url"])
    page = context.new_page()
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    context.storage_state(path=str(state_path))
    browser.close()
    return state_path


@pytest.fixture
def authenticated_page(request, browser, config, credentials, session_mode):
    from Utils.download_helper import attach_download_handler

    context_kwargs = {"base_url": config["base_url"], "accept_downloads": True}
    if session_mode == "single":
        auth_storage_state = request.getfixturevalue("auth_storage_state")
        context_kwargs["storage_state"] = str(auth_storage_state)

    context = browser.new_context(**context_kwargs)
    page = context.new_page()
    attach_download_handler(page)
    errors = _track_server_errors(page)

    if session_mode == "fresh":
        # This fixture's contract is "already logged in" -- in fresh mode
        # there's no cached storage_state to provide that, so log in for
        # real here instead of leaving callers to do it themselves.
        login_page = LoginPage(page, config)
        login_page.open()
        login_page.login(credentials["username"], credentials["password"])
        page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)

    yield page

    context.close()
    _assert_no_server_errors(request, errors)


@pytest.fixture
def unit_settings(authenticated_page):
    """Log in, open the Unit List, and open Settings for the first unit.

    Returns (unit_page, unit_settings_page), both ready to use -- replaces the
    per-file `login_and_open_unit_settings(page, config, credentials)` helper
    duplicated across every Unit test file.
    """
    unit_page = UnitPage(authenticated_page)
    unit_settings_page = UnitSettingsPage(authenticated_page)
    unit_page.open_unit_list()
    unit_page.open_unit_settings_by_index(0)
    unit_settings_page.wait_for_modal_open()
    return unit_page, unit_settings_page


@pytest.fixture
def tracking(authenticated_page):
    """Log in and open the Tracking module, defaulted to the Live Tracking tab.

    Replaces the per-file `login_and_open_tracking(page, config, credentials)`
    helper duplicated across every Tracking test file.
    """
    tracking_page = TrackingPage(authenticated_page)
    tracking_page.open_tracking_page()
    tracking_page.switch_to_live_tracking()
    return tracking_page


@pytest.fixture
def settings_menu(authenticated_page):
    """Log in and open the Settings module. Returns the SettingsSideMenu,
    ready to navigate to any submodule (open_driver(), open_alert(...), etc.)."""
    menu = SettingsSideMenu(authenticated_page)
    authenticated_page.goto("/settings")
    menu.wait_for_visible(menu.driver_management_btn)
    return menu


@pytest.fixture
def driver_page(settings_menu):
    """Log in, open Settings, and land on the Driver list."""
    settings_menu.open_driver()
    page = DriverPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    # The table body can be present-but-still-empty for a moment while the
    # SPA populates it (confirmed live -- reading rows right after the
    # container becomes visible was flaky), so give it a beat to settle.
    page.page.wait_for_timeout(1000)
    return page


@pytest.fixture
def driver_performance_page(settings_menu):
    """Log in, open Settings, and land on the Driver Performance list.

    The table can briefly still hold the previous route's content right
    after navigating (confirmed live -- a table read immediately after
    open_driver_performance() occasionally returned Driver's own table),
    so wait for the real table body before handing the page back.
    """
    settings_menu.open_driver_performance()
    page = DriverPerformancePage(settings_menu.page)
    page.wait_for_visible(page.table.locator("tbody"))
    # A 1s wait here was still occasionally flaky (confirmed live -- read
    # the table before Angular finished populating it); this page in
    # particular needs more settle time than Driver's does.
    page.page.wait_for_timeout(3000)
    return page


@pytest.fixture
def vehicle_group_page(settings_menu):
    """Log in, open Settings, and land on the Vehicle Group list."""
    settings_menu.open_vehicle_group()
    page = VehicleGroupPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def vehicle_performance_page(settings_menu):
    """Log in, open Settings, and land on the Vehicle Performance list."""
    settings_menu.open_vehicle_performance()
    page = VehiclePerformancePage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def location_control_page(settings_menu):
    """Log in, open Settings, and land on the Location Control list."""
    settings_menu.open_location_control()
    page = LocationControlPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def alert_page(settings_menu):
    """Log in, open Settings, and land on the given alert type's list.
    Usage: alert_page("Speed Alert") -> a ready AlertConfigPage."""
    def _open(alert_type: str) -> AlertConfigPage:
        settings_menu.open_alert(alert_type)
        page = AlertConfigPage(settings_menu.page, alert_type)
        page.wait_for_visible(page.heading)
        page.page.wait_for_timeout(1500)
        return page
    return _open


@pytest.fixture
def geofence_alert_page(settings_menu):
    """Log in, open Settings, and land on the Geofence Alert list."""
    settings_menu.open_alert("Geofence Alert")
    page = GeofenceAlertPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def ais_alert_page(settings_menu):
    """Log in, open Settings, and land on the AIS Alert list."""
    settings_menu.open_alert("AIS Alert")
    page = AisAlertPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def route_page(settings_menu):
    """Log in, open Settings, and land on the Route Management list."""
    settings_menu.open_route_management()
    page = RouteManagementPage(settings_menu.page)
    page.wait_for_visible(page.heading)
    page.page.wait_for_timeout(1500)
    return page


@pytest.fixture
def reports_page(authenticated_page):
    """Log in and open the Reports module, defaulted to the Standard tab.

    Replaces the per-file `login_and_open_reports(page, config, credentials)`
    helper duplicated across every Reports test file.
    """
    reports_page = ReportsPage(authenticated_page)
    reports_page.go_to_reports()
    return reports_page


@pytest.fixture
def home_page(authenticated_page, config):
    """Log in and open the Home module (fleet monitoring dashboard)."""
    home_page = HomePage(authenticated_page)
    home_page.open(config["base_url"])
    return home_page


@pytest.fixture
def administrator_page(authenticated_page, config):
    """Log in and open the Administrator module (sub-user management)."""
    administrator_page = AdministratorPage(authenticated_page)
    administrator_page.open(config["base_url"])
    return administrator_page


@pytest.fixture
def account_menu(authenticated_page, config):
    """Log in and land on /home, ready to open the Account menu."""
    authenticated_page.goto(f"{config['base_url']}/home")
    menu = AccountMenuPage(authenticated_page)
    menu.wait_until_ready()
    # A fresh login shows a "Login successful" toast that can still be
    # settling/overlapping the top-right nav icons right after load
    # (confirmed live: the menu trigger intermittently failed to open when
    # this fixture is the very first thing a test does) -- give it a beat.
    authenticated_page.wait_for_timeout(1000)
    return menu


@pytest.fixture
def profile_page(authenticated_page, config):
    """Log in and open My Profile (/profile)."""
    profile_page = ProfilePage(authenticated_page)
    profile_page.open(config["base_url"])
    return profile_page


@pytest.fixture
def downloads_page(authenticated_page, config):
    """Log in and open Downloads (/profile/downloads)."""
    downloads_page = DownloadsPage(authenticated_page)
    downloads_page.open(config["base_url"])
    return downloads_page


@pytest.fixture
def support_page(authenticated_page, config):
    """Log in and open Support Management (/profile/support)."""
    support_page = SupportPage(authenticated_page)
    support_page.open(config["base_url"])
    return support_page


@pytest.fixture
def change_password_page(authenticated_page, config):
    """Log in and open Change Password (/profile/change-password)."""
    change_password_page = ChangePasswordPage(authenticated_page)
    change_password_page.open(config["base_url"])
    return change_password_page


@pytest.fixture
def help_center_page(authenticated_page, config):
    """Log in and open Help Center (/help-center)."""
    help_center_page = HelpCenterPage(authenticated_page)
    help_center_page.open(config["base_url"])
    return help_center_page


@pytest.fixture
def feedback_prompt(authenticated_page, config):
    """Log in and open the Feedback prompt. Confirmed live: the
    persistent floating "FEEDBACK" nav button that triggers it lives on
    /profile/* pages, not /home."""
    authenticated_page.goto(f"{config['base_url']}/profile/change-password")
    authenticated_page.wait_for_timeout(1500)
    feedback_page = FeedbackPage(authenticated_page)
    feedback_page.open_prompt()
    return feedback_page


@pytest.fixture
def feedback_form(feedback_prompt):
    """Log in and open the full Feedback form (via the prompt's Give
    Feedback link)."""
    feedback_prompt.open_form_from_prompt()
    return feedback_prompt


@pytest.fixture
def network_monitor(page):
    monitor = NetworkMonitor(page)
    yield monitor
    monitor.stop()


@pytest.fixture(scope="session")
def credentials():
    return {
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    }


@pytest.fixture
def cleanup_downloads():
    """
    Fixture that cleans up the root downloads/ folder after a test completes.
    Use this fixture in tests that trigger file downloads to ensure downloaded
    files are removed once assertions have been verified.

    Usage:
        def test_something(page, config, credentials, cleanup_downloads):
            ...
    """
    from Utils.download_helper import DOWNLOADS_DIR

    yield  # test runs here

    # Teardown: delete all files in downloads/ after the test
    if DOWNLOADS_DIR.exists():
        deleted = []
        for f in DOWNLOADS_DIR.iterdir():
            if f.is_file():
                f.unlink()
                deleted.append(f.name)
        if deleted:
            print(f"\n[cleanup_downloads] Removed {len(deleted)} file(s) from downloads/: {deleted}")

