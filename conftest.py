import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from config.settings import load_config


load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Environment to run tests against",
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
def page(browser):
    context = browser.new_context()

    page = context.new_page()

    yield page

    context.close()


@pytest.fixture(scope="session")
def credentials():
    return {
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD"),
    }