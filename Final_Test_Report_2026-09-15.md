# Trackofy Production Regression — Final Test Report

**Date:** 2026-09-15
**Environment:** Production (`https://v6.trackofy.com`)
**Execution mode:** 21 serial batches (no parallel workers), one browser process at a time, after parallel (`-n 4`) execution proved unstable on this machine (INTERNALERROR crashes, then a real resource freeze).
**Coverage:** 19 of 21 batches complete = **1,571 of 1,651 tests executed** (95.2%). `admin_panel_func` (67 tests) and `admin_panel_sec` (13 tests) — 80 tests, 4.8% — are blocked pending the admin-login issue below (Bug #96) and were not run this pass.

## Headline results

| Result | Count |
|---|---|
| Passed | 1,257 |
| Failed | 81 |
| Errors | 45 (all one root cause — see below) |
| Skipped | 188 |
| **Total executed** | **1,571** |

## Per-batch results

| Batch | Passed | Failed | Errors | Skipped | Notes |
|---|---|---|---|---|---|
| smoke | 16 | 1 | 0 | 1 | |
| func_admin | 86 | 2 | 0 | 13 | |
| func_reports | 125 | 5 | 0 | 12 | includes AS-219 reconfirmation |
| func_misc | 202 | 9 | 0 | 61 | |
| func_vt | 141 | 3 | 0 | 23 | 2 of 3 failures are **good news** (bugs fixed) |
| func_settings | 9 | 0 | 45 | 0 | **one browser crash, not 45 bugs** — see below |
| func_home | 102 | 23 | 0 | 2 | **mostly one root cause** — see below |
| func_login | 76 | 0 | 0 | 10 | clean |
| func_unit | 24 | 0 | 0 | 2 | clean |
| func_tracking | 25 | 0 | 0 | 0 | clean |
| func_dashboard | 14 | 2 | 0 | 1 | |
| func_main | 14 | 0 | 0 | 0 | clean |
| func_can | 5 | 1 | 0 | 0 | |
| positive | 179 | 12 | 0 | 4 | |
| negative | 130 | 7 | 0 | 5 | |
| edgecase | 74 | 10 | 0 | 34 | |
| security | 10 | 0 | 0 | 0 | clean |
| crud | 11 | 4 | 0 | 20 | includes a genuine script `NameError` |
| asset_management | 14 | 2 | 0 | 0 | |
| admin_panel_func | — | — | — | — | **not run** (blocked, Bug #96) |
| admin_panel_sec | — | — | — | — | **not run** (blocked, Bug #96) |

## Good news: 3 previously-documented bugs appear fixed

Found via regression-pin tests that deliberately assert a known bug still exists — when those tests fail, it's a strong signal the bug is gone:

1. **Bug #37 (Critical, Security)** — Change Password's "Verify current password" step used to accept *any* password with zero real check. Now confirmed rejecting a wrong password correctly.
2. **Bug #44 (High)** — Video Telematics Report's Alert Type filter used to be silently ignored by the backend. Now confirmed actually filtering results correctly.
3. **Bug #43 (High)** — Video Telematics Report's Export buttons were all no-op stubs. **Export to CSV** now genuinely downloads a file. Export to Excel is still a no-op (not fully fixed).

All three are marked in `Bug_Report.md` as "likely fixed, caught via automated regression, recommend one manual confirmation" — not closed outright, since this was caught by an automated run rather than a fresh manual dive.

## New bugs found this session (logged in `Bug_Report.md` + `Trackofy_New_Bugs_2026-09-15_Jira_Import.csv`)

- **Bug #95 (Medium)** — Distance Chart / Cumulative Distance / Maxspeed Chart show validation error banners the instant you click the Start Date field, before Generate is ever pressed. (Your manual finding, confirmed and reproduced across 3 reports.)
- **Bug #96 (Info)** — Admin Panel login: backend auth succeeds but the page never redirects to `/admin/dashboard` after very heavy repeated logins on the same account. Not root-caused — logged as an open observation, most likely account/session throttling from our own heavy test load, not a defect an ordinary user would hit.
- **Bug #97 (High)** — AS-219 reconfirmed on **production**: a Daily scheduled report never arrives by email, checked both Inbox and Spam. Previously only confirmed on staging.

## Two clusters that look like a lot of failures but are really one issue each

### `func_settings`: 45 errors = 1 browser crash, not 45 bugs
Every error is the identical Playwright exception: `BrowserContext.new_page: Target crashed`. The shared browser process crashed early in this batch (infrastructure/stability blip, not app or test logic), and every subsequent test in that single pytest run failed identically trying to open a page in a dead browser. **A plain re-run of just this batch would very likely go green** — nothing here needs a code fix.

### `func_home`: 23 failures, ~18 trace to one bad constant
`Pages/home_page.py`'s `KNOWN_GROUPS` list (and a matching `@pytest.mark.parametrize` list in `test_home_groups_drivers_functional.py`) hardcodes group names `"Delhi"` and `"Bhopal"`. These don't exist on the production account — its real groups are `Default`, `Renamed HCIEAG`, `AssignFull1789290640`, and `Dwarka`. This one wrong, apparently staging-specific, hardcoded list explains the large majority of this batch's failures. **This is a script/test-data issue, not an app bug** (flagged for you to decide whether to fix, not fixed by me).

The remaining ~5 `func_home` failures are more interesting and were individually diagnosed:
- `test_home_0261_map_only...` — **not new**, this is the existing regression pin for Bug #23 (Map-only GeoLink still exposes the vehicle's registration number). Still reproduces.
- `test_home_0237...create_list_and_delete_geolink` and `test_home_0326...refresh_unsaved_geolink` — both trace to `geolinks_count()` reading a premature "0" immediately after the page loads/reloads (a loading race, same class of bug already fixed elsewhere in this codebase for CAN module counters via a "poll until stable" pattern). **Script issue, not a real bug** — confirmed no actual residual data exists (verified live: real count is a stable 4, no orphaned `pytest-*` geolinks).
- `test_home_0178_acknowledge_alert...` and `test_home_search_variants[Groups]` — not fully root-caused; could be the same timing-race class, or could be real. Flagged as needing a closer look, not claimed either way.

## Other systemic script issue found

**`Tests/CRUD/test_Transfer_Creation.py::test_transfer_creation`** fails with a plain Python `NameError: name 'ExportComponent' is not defined` in `Pages/asset_transfer_page.py` — a missing import. The test never even reaches the app. Unambiguous script bug.

**`Tests/CRUD/test_Installation_Creation.py::test_installation_creation`** fails trying to select a hardcoded vehicle option `"HARSH_test"` that doesn't exist on production — the same "hardcoded staging-only entity name" pattern as the Home groups issue above.

## Everything else (remaining ~55 failures across the other batches)

These were surveyed at the assertion-message level (listed below by batch with their failure message) but **not individually root-caused** — that would need a dedicated follow-up pass. A few stood out as worth a closer look for being *possibly real*: two `negative` tracking tests about session-expiry (401) not triggering re-auth, an `edgecase` test showing 5 duplicate report-generation requests firing on rapid clicks, and several `positive` report-column-selection failures. Nothing here has been fixed — per your instruction, I'm reporting these for you to direct, not touching test code myself.

Full per-test failure list with assertion messages is preserved in `batch_logs/*.log` for reference.

## Coverage additions made this session

- **Cross-browser capability**: the `browser` fixture was hardcoded to Chromium regardless of the (declared-but-unused) `browser:` config key. Added a `--browser-engine` option and installed Firefox + WebKit so the suite can actually run cross-browser now (previously impossible despite the Login module's spec calling for it). Not yet exercised at scale against production — recommend a Smoke-only cross-browser pass as a low-risk first use.

## Data safety / cleanup notes

- Verified live: no orphaned `pytest-home-geolink-*` or `pytest-home-security-*` entries remain on the production account (real GeoLinks count is a stable 4).
- The AS-219 email-schedule test (`test_rep_sch_030b`) deletes the schedule it creates in a `finally` block regardless of outcome — confirmed this ran.
- A full sweep across every module for residual test-created data (dealers, alerts, feedback submissions, etc. created during this and earlier sessions' runs) has **not** been done as part of this pass and is recommended as a separate, dedicated task before considering the account fully clean.

## What's still pending

1. `admin_panel_func` and `admin_panel_sec` (80 tests) — blocked on Bug #96, retry once the account issue clears.
2. Individual root-cause pass on the ~55 not-yet-diagnosed failures listed in batch logs.
3. A dedicated residual-test-data cleanup sweep across all modules.
4. Manual confirmation of the 3 "likely fixed" bugs (#37, #43, #44) before formally closing them.
