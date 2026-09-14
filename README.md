# Trackofy QA Automation Framework

Playwright + Python + pytest test suite for Trackofy, a fleet-management web app. Strict Page Object Model: every locator lives in a `Pages/*.py` class, tests only call methods on page objects.

## Stack

- **Playwright (sync API)** for browser automation (Chromium)
- **pytest** as the test runner, with `pytest-xdist` for parallel runs and `pytest-rerunfailures` for flake reruns
- **python-dotenv** for local credentials, **PyYAML** for per-environment config

## Setup

```bash
python -m venv venv
source venv/Scripts/activate   # or venv/bin/activate on macOS/Linux
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in real credentials:

```
TEST_USERNAME=
TEST_PASSWORD=
ADMIN_TEST_USERNAME=      # Admin Panel account
ADMIN_TEST_PASSWORD=
ADAS_TEST_USERNAME=       # Video Telematics-entitled account
ADAS_TEST_PASSWORD=
CAN_TEST_USERNAME=        # CAN module-entitled account
CAN_TEST_PASSWORD=
```

`.env` is git-ignored — never commit real credentials.

## Running tests

```bash
pytest                                   # full suite, staging, headed per config default
pytest --env=staging                     # target environment (config/environments/<env>.yaml)
pytest Tests/functional/                 # one category
pytest -k test_login_007                 # one test by name
pytest -m admin_panel                    # one module, by marker
pytest -n auto                           # parallel, via pytest-xdist
TRACKOFY_HEADLESS=true pytest            # force headless without editing the yaml
```

`--session-mode=single` reuses one cached login per worker instead of logging in via the UI for every test (faster, less representative of a real session). Default is `fresh`.

Registered markers (`functional`, `positive`, `negative`, `edgecase`, `smoke`, `security`, `admin`, `admin_panel`, `can`, `video_telematics`, `reports`, `dashboard`, `home`, `misc`, `login`, `accessibility`, `responsive`, `allow_server_error`, ...) are declared in `conftest.py` and let you slice the suite by module or test shape.

## Layout

```
Pages/          Page Objects -- one class per app page/module. All locators live here.
components/     Shared UI components used across multiple pages (navbar, pagination, wizards, calendar...)
Tests/
  functional/   Core user-flow tests, organized per module
  positive/     Valid-input / happy-path scenarios
  negative/     Invalid-input / rejection scenarios
  edgecase/     Boundary conditions
  Smoke/        Fast, broad sanity checks
  security/     AuthZ, IDOR, injection, direct-URL-access tests
  Admin Panel/  Back-office (/admin/*) module, mirrors the same functional/security split
  CRUD/         Create/read/update/delete flows for installations & transfers
  asset_management/
config/         Environment config (config/environments/*.yaml) + credentials fixture
Utils/          Data loading and file-download helpers
data/           Static/generated test data used by Reports tests
test_data/      JSON fixtures consumed by specific test modules
test_cases/     Manual/planning test-case CSVs (design-time reference, not executed)
frs/, specs/    Requirements and test-plan reference docs
conftest.py     Fixtures: browser/page setup, auth, per-module page-object fixtures, global 5xx-response guard
```

## Conventions (see `CLAUDE.md`)

- Locators: prefer `get_by_role` / `get_by_label` / `get_by_text` over CSS/XPath, and keep them all inside the relevant `Pages/*.py` class — never inline in a test.
- Reusable UI pieces (navbar, logout, pagination, wizards) belong in `components/`, not duplicated per page.
- Tests validate the app against real user-facing behavior and API-returned data, not just "did the button click" — assert on what's actually shown/returned.
- Security scenarios are first-class, not an afterthought.

## Bug tracking

- `Bug_Report.md` — the full, numbered bug log with reproduction steps, impact, and reverification notes.
- `retest_bug_report.md` — narrative retest pass log per module.
- `Trackofy_New_Bugs_2026-09-13_Jira_Import.csv` — current session's new findings in Jira-bulk-import format.
- `Trackofy_*_Module_Explanation.md` — per-module functional spec notes used to scope test coverage.
