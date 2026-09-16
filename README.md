# Trackofy QA Automation Framework

Playwright + Python + pytest test suite for Trackofy, a fleet-management web app. Strict Page Object Model: every locator lives in a `Pages/*.py` class, tests only call methods on page objects.

## Stack

- **Playwright (sync API)** for browser automation — Chromium, Firefox, and WebKit are all supported (see "Choosing a browser" below)
- **pytest** as the test runner, with `pytest-xdist` for parallel runs and `pytest-rerunfailures` for flake reruns
- **python-dotenv** for local credentials, **PyYAML** for per-environment config

## Setup

```powershell
python -m venv venv1
.\venv1\Scripts\Activate.ps1      # PowerShell. cmd.exe: venv1\Scripts\activate.bat. macOS/Linux: source venv1/bin/activate
pip install -r requirements.txt
playwright install chromium firefox webkit
```

Prefer `python -m pytest ...` over bare `pytest ...` if you're ever unsure the venv is active in your shell: if it isn't, a bare `pytest` can silently resolve to a *different*, globally-installed pytest instead of this project's pinned one, and a mismatched `pytest-xdist`/`pytest-rerunfailures` version pairing has caused real INTERNALERROR crashes before. `python -m pytest` (or the venv's full interpreter path, e.g. `.\venv1\Scripts\python.exe -m pytest ...`) always uses the right one regardless of activation state.

(`pytest.ini` sets `pythonpath = .`, so either form correctly finds `config`/`Pages`/etc. — this used to require `python -m pytest` specifically, since `--import-mode=importlib`, needed to let two same-named test files in different folders coexist, otherwise skips pytest's usual automatic rootdir-on-path behavior.)

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
TEST_RECIPIENT_EMAIL=              # optional: a real Gmail inbox for the scheduled-report-delivery test
TEST_RECIPIENT_EMAIL_PASSWORD=     # a Gmail App Password, not the account password
```

`.env` is git-ignored — never commit real credentials.

## Running tests

### Target environment

```bash
python -m pytest --env=staging     # config/environments/staging.yaml (default)
python -m pytest --env=prod        # config/environments/prod.yaml -- real production, be deliberate
```

### Running one module at a time

```bash
python -m pytest Tests/functional/test_reports_standard_functional.py   # one file
python -m pytest Tests/functional/test_reports_*.py                     # one module, all its test files (shell glob)
python -m pytest Tests/positive/                                        # one whole category directory
python -m pytest -k test_login_007                                      # one test by name
python -m pytest -m admin_panel                                         # one module, by marker (see marker list below)
```

### Sequential vs. simultaneous (avoiding a frozen machine)

By default pytest runs **sequentially** — one test, one browser, at a time. This is the safest mode on a normal dev machine.

```bash
python -m pytest                          # sequential (default) -- one browser process at a time
python -m pytest -n 4 --dist=loadscope    # simultaneous -- 4 parallel workers, own browser each
python -m pytest -n auto --dist=loadscope # simultaneous -- one worker per CPU core
```

`--dist=loadscope` keeps every test in the same file on the same worker, so tests that share mutable data (e.g. all the tests in one Settings/Alerts file) never race each other. **Always use `--dist=loadscope` when using `-n`** — plain `-n` without it can let two tests fight over the same shared account/entity list.

Parallel runs use noticeably more CPU/RAM (multiple simultaneous headless browser processes) and, on this project, have caused real machine slowdowns during a full 1,650-test production run. If that happens again: prefer **sequential batches** instead of parallel workers — run one category at a time (see commands above), which keeps only one browser alive at any moment. `run_batches.sh` at the project root does exactly this for the whole suite: it runs each test category as its own sequential `pytest` call, and safely skips any category that already finished if you re-run it after an interruption.

```bash
bash run_batches.sh   # whole suite, one category at a time, resumable
```

### Choosing a browser

```bash
python -m pytest                               # Chromium (default, matches config/environments/*.yaml)
python -m pytest --browser-engine=firefox
python -m pytest --browser-engine=webkit
```

Requires that engine's binary to be installed once via `playwright install <engine>`.

### Login behavior: fresh login per test vs. one shared login

```bash
python -m pytest                                    # --session-mode=fresh (default): every test logs in via the real UI from scratch
python -m pytest --session-mode=single              # one real UI login per worker, then every test in that worker reuses it (cached storage_state)
```

`fresh` is slower but closer to how a real user session behaves; `single` is faster and useful for quick local iteration, but a test can no longer assume it starts from a truly clean, brand-new session. Only the `page`/`authenticated_page` fixtures respect this flag — the dedicated Admin Panel/Video Telematics/CAN fixtures (`admin_authenticated_page`, `vt_authenticated_page`, `can_authenticated_page`) always do a real fresh login regardless, since they use separate accounts.

### Other useful flags

```powershell
$env:TRACKOFY_HEADLESS = "true"; python -m pytest    # PowerShell: force headless without editing the environment yaml
```
```bash
TRACKOFY_HEADLESS=true python -m pytest              # Git Bash / macOS / Linux: same, one line
```
```bash
python -m pytest --alluredir=allure-results    # already the default (set in pytest.ini) -- produces Allure results every run
allure generate allure-results -o allure-report --clean && allure open allure-report   # view the Allure report
```

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
conftest.py     Fixtures: browser/page setup, auth, per-module page-object fixtures, global 5xx-response guard, Allure failure-screenshot capture
run_batches.sh  Runs the whole suite as sequential, resumable per-category batches (see "Sequential vs. simultaneous" above)
batch_logs/     Per-category log output from run_batches.sh runs
```

## Conventions (see `CLAUDE.md`)

- Locators: prefer `get_by_role` / `get_by_label` / `get_by_text` over CSS/XPath, and keep them all inside the relevant `Pages/*.py` class — never inline in a test.
- Reusable UI pieces (navbar, logout, pagination, wizards) belong in `components/`, not duplicated per page.
- Tests validate the app against real user-facing behavior and API-returned data, not just "did the button click" — assert on what's actually shown/returned.
- Security scenarios are first-class, not an afterthought.
- Don't hardcode account-specific data (a specific vehicle/group/asset name) that only exists on one environment's account — prefer discovering it live (e.g. `HomePage.real_group_names()`, or picking whatever option is first in a dropdown) so the same test works across environments/accounts. A regression pin that deliberately asserts a *known bug's* current behavior (e.g. `test_vt_129_alert_type_specific` for Bug #44) is the one legitimate exception — that's pinning app behavior, not test data.

## Known framework debt

- `components/create_transfer_wizard.py` is stale relative to the real Asset Transfer form (confirmed live 2026-09-15): there's no "previous vehicle" dropdown (it's read-only text), the submit button was mislabeled, and required fields like Transfer Reason — plus asset-type-conditional fields for tyre assets — were never modeled. `Tests/CRUD/test_Transfer_Creation.py::test_transfer_creation` is skipped with the full explanation until someone scopes what this test should actually verify against the current form.

## Bug tracking

- `Bug_Report.md` — the full, numbered bug log with reproduction steps, impact, and reverification notes.
- `retest_bug_report.md` — narrative retest pass log per module.
- `Trackofy_New_Bugs_<date>_Jira_Import.csv` — one file per session's new findings in Jira-bulk-import format (dated by when that session ran).
- `Final_Test_Report_<date>.md` — end-of-run summary report for a full regression pass (pass/fail counts, root-caused clusters, script vs. app issues).
- `Trackofy_*_Module_Explanation.md` — per-module functional spec notes used to scope test coverage.
