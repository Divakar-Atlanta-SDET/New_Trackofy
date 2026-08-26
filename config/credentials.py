import os
from dotenv import load_dotenv
import pytest

load_dotenv()

@pytest.fixture(scope="session")
def credentials():
    return {
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD")
    }