import os
import re

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from config.settings import load_config
from Pages.login_page import LoginPage


load_dotenv()


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
    config.addinivalue_line("markers", "reports: reports module tests")
    config.addinivalue_line("markers", "report_generation: report generation tests")


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
def page(browser, config):
    context = browser.new_context(base_url=config["base_url"])

    page = context.new_page()

    yield page

    context.close()


@pytest.fixture
def authenticated_page(page, config, credentials):
    login_page = LoginPage(page, config)
    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    page.wait_for_url(re.compile(rf"{re.escape(config['base_url'])}/home/?$"), timeout=15000)
    return page


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
