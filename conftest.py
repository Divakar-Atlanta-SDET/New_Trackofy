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


def pytest_configure(config):
    config.addinivalue_line("markers", "functional: functional workflow tests")
    config.addinivalue_line("markers", "positive: positive scenario tests")
    config.addinivalue_line("markers", "negative: negative scenario tests")
    config.addinivalue_line("markers", "edgecase: edge case boundary tests")
    config.addinivalue_line("markers", "reports: reports module tests")
    config.addinivalue_line("markers", "report_generation: report generation tests")
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
def page(request, browser, config):
    from Utils.download_helper import attach_download_handler

    context = browser.new_context(base_url=config["base_url"], accept_downloads=True)

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
def authenticated_page(request, browser, config, auth_storage_state):
    from Utils.download_helper import attach_download_handler

    context = browser.new_context(
        base_url=config["base_url"], accept_downloads=True, storage_state=str(auth_storage_state)
    )
    page = context.new_page()
    attach_download_handler(page)
    errors = _track_server_errors(page)

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

