# CAN Module — Test Plan

Generated from a live exploration of `https://staging.trackofy.com` using the
`CAN_TEST_USERNAME` / `CAN_TEST_PASSWORD` account (`.env`), which has the CAN
module enabled. Confirmed real routes (some differ from
`Trackofy_CAN_Module_Explanation.md`'s assumed paths):

| Section | Real URL | Explanation doc assumed |
|---|---|---|
| Dashboard | `/can/dashboard` | (matches) |
| Unit | `/can/units` | `/can/unit` |
| Trends | `/can/trends` | (matches) |
| Reports | `/can/report` | `/can/reports` |
| Alerts | `/can/alerts` | (matches) |
| Settings | `/can/settings` | (matches) |

Fleet under this account: **14 CAN units**, 5 protocols (JBM BCS 210, JBM Coach,
EEka CAN Protocol, CV800 D032P AC, 207 Photon R2), **1810** existing alerts,
**13** configured alert rules. A persistent, draggable/maximizable **Live Fleet
Map** ("CAN Tracking") is present on every CAN page.

Assumed starting state for every scenario below: fresh browser context, logged
out, then logged in via the CAN account unless stated otherwise.

---

## 1. Smoke

### 1.1 CAN nav entry and module landing
1. Log in with the CAN account.
2. Confirm a `cable` "CAN" link is visible in the main left nav (`get_by_role("link", name="CAN")`).
3. Click it.
- **Expected**: Navigates to `/can/dashboard`; the CAN sub-menu (Dashboard, Unit, Trends, Reports, Alerts, Settings) renders.

### 1.2 All six CAN sub-pages load without error
For each of Dashboard, Unit, Trends, Reports, Alerts, Settings:
1. Click the sub-menu link from within the CAN module.
- **Expected**: Correct URL, a page `heading` matching the section (e.g. "CAN Dashboard", "CAN Units", "CAN Report"), no unhandled error banner, no 5xx from any XHR/fetch (matches this repo's existing `_track_server_errors` convention).

### 1.3 Direct URL access to each CAN route
1. While logged in, `page.goto()` directly to each of the six real URLs above.
- **Expected**: Each loads the correct section directly (deep-linkable), not a redirect to `/home` or `/can/dashboard`.

---

## 2. Dashboard (`/can/dashboard`)

### Positive / Functional
- KPI cards render with numeric values for Total Assets, Online/Reporting, Offline/Stale, Protocols, Active Alerts (`get_by_text` / a KPI-card helper analogous to `ReportsPage.get_kpi_card_value`).
- Total Assets equals Online + Offline (data-sense check, mirrors the Reports-module cross-report validation done previously).
- "Protocol Wise Assets" bar chart and "Online vs Offline" donut chart render (assert their heading + some chart container is visible).
- Recent Alerts panel lists entries with Metric, Unit, Protocol, Timestamp, Level badge (Warning/Critical), Actual, Limit, Message; "View All" navigates to `/can/alerts`.
- "Open Units" link navigates to `/can/units`.
- CAN Unit table (below dashboard) renders with columns S.No/Unit/IMEI/Protocol/Last Contact/Params/Status/Warnings/Critical/Action; search, export (`table_view`/`description`/`picture_as_pdf`/`print`/`content_copy`), and pagination work.
- Refresh button re-fetches without a full page reload (network monitor: new XHR fired, page URL unchanged).
- AI Summary panel opens (button `AI\nSummary`) and shows urgent-attention units, fleet vitals, highlights.

### Negative / Edge case
- Refresh spam (rapid repeated clicks) does not duplicate KPI requests indefinitely or desync the cards from the table.
- Recent Alerts panel behavior when there are 0 alerts (a filtered/empty account, or after clearing — likely only testable via a different low-alert account; document as environment-dependent if not reachable).
- AI Summary panel behavior on slow/failed AI backend response (network mock).

### Data validation (explicit ask from the original CAN task)
- Cross-check: does "Total Assets" (14) match the Unit List's total row count (14, confirmed live) and the Live Fleet Map's fleet count (`directions_car\n14`, confirmed live)? All three agreed in this pass — worth a permanent regression assertion.
- Cross-check: do "Online/Reporting" (4) + "Offline/Stale" (10) sum to Total Assets (14)? Confirmed live: 4 + 10 = 14 -- consistent.

---

## 3. Unit (`/can/units`)

### Positive / Functional
- Unit List table renders with columns S.No, Unit, IMEI, Protocol, Type, Last Contact, Params (Live/Total), Values, Status, Action.
- Search filters the table by Unit/IMEI text.
- Apply Filter drawer opens with Protocol and Status filters, plus Reset/Apply.
- Sorting via column header `swap_vert` icons (Unit, IMEI, Protocol, Type, Last Contact, Params, Values, Status).
- Export (Excel/CSV/PDF via `table_view`/`description`/`picture_as_pdf`), Print, Copy.
- Pagination (rows-per-page 10/25/50/100, first/prev/next/last) — 14 total rows.
- Row "visibility" action opens the individual unit's detail view.

### Negative / Edge case
- Filter combination that matches no unit shows a clean empty state, not a broken table.
- Search for a non-existent IMEI/unit name returns "no results", not stale rows.
- Status filter (Online/Offline) count sanity-checks against the Dashboard KPI cards.

---

## 4. Trends (`/can/trends`)

### Positive / Functional
- "Data & Chart Settings" form: Protocol, Units (multi-select), From/From Time, To/To Time, Chart Type (Line confirmed as default/only observed option — verify other chart types exist), Show Markers checkbox, Normalize (mixed units) checkbox, Apply.
- Selecting Protocol filters/enables the Units combobox (protocol -> unit dependency, matches explanation doc's stated dependency).
- After Apply with valid Protocol + >=1 Unit + Metric + date range: "Metric Trend (multi-unit)" section renders one series per selected unit.
- "Multi Parameter Comparison (multi-unit)": Smart Default and Draw Comparison buttons; selecting multiple metrics x multiple units produces one series per metric-unit pair; mixed-unit series auto-normalize when the Normalize checkbox is checked.

### Negative / Edge case
- No protocol selected: Units combobox has no data / Apply stays disabled.
- Units selected without a Metric: "Select at least one unit and a metric" message shown (confirmed live text) instead of a chart.
- Invalid date range (From > To): should be blocked or show validation, not silently sent to the backend (mirrors Bug pattern already found in Reports module for date ranges).
- Selecting more than 5 units: explanation doc/live copy states "up to 5 units" — verify the UI actually caps selection at 5 and shows a clear message, not a silent truncation or backend error.
- No-data range for a valid unit/metric: chart area should show an empty state, not an infinite loader or JS error.

---

## 5. Reports (`/can/report`)

### Positive / Functional
- Report Settings form: Protocol, Units/Devices (multi-select, "All selected (14)" state confirmed reachable), From/From Time, To/To Time, Generate Report.
- Generate Report with valid filters returns a report table (Export/Search/Pagination per the common table pattern).
- "All selected" device state generates a report spanning all 14 units without truncation or hang (mirrors the Reports-module "Select All" hang previously found and later not-reproduced — worth checking fresh here since this is a materially different report/backend).

### Negative / Edge case
- No protocol/units selected: Generate Report should be disabled or show a clear validation error, not silently no-op or 500.
- Invalid date range (From > To, From == To, future dates): verify handling.
- No-data range for a valid protocol/unit selection: clean empty state, not a raw backend error (this exact failure mode was previously confirmed for 3 of the main Reports module's Standard reports — a prime regression risk to re-check here).

---

## 6. Alerts (`/can/alerts`)

### Positive / Functional
- Alert Log table: columns S.No, Level, Unit, IMEI, Protocol, Metric, Actual, Limit, Message, Last Contact; 1810 total rows confirmed live.
- Search, Refresh, Apply Filter (Protocol, Level, Unit filters with Reset/Apply), Export, Sorting via column headers, Pagination.
- Level badges correctly distinguish Warning vs Critical (visual/text check).

### Negative / Edge case / Data validation
- Filter by Level=Critical returns only Critical rows (no Warning rows leak through) — same class of bug as the previously-confirmed "Manage Plan search returns unrelated results" bug in the Admin Panel; worth a dedicated data-purity check here.
- Filter by a Protocol with 0 alerts shows a clean empty state.
- For a sampled alert row, `Actual` vs `Limit` should be internally consistent with the alert's Level (e.g. a "Warning"/"Critical" row where Actual doesn't actually breach Limit would be a data-sense bug, mirroring the Reports-module cross-column validation already applied — flag any row where Actual/Limit appear to contradict the stated Level, e.g. the confirmed live example `unknown pid count CRITICAL. Actual: 0, Limit: 0` -- Actual == Limit on a *Critical* row is suspicious and worth flagging if reproducible).

---

## 7. Settings (`/can/settings`)

### Positive / Functional
- Alert Configuration form: Protocol, Unit, Metric, Mode (High confirmed as a mode; verify other modes exist, e.g. Low), Warning Limit, Critical Limit, Notify via (Application/Email checkboxes), Reset, Save.
- Creating a rule with valid values adds a row to Configured Alert Rules (13 confirmed live) and the rules count updates.
- Configured Alert Rules table: S.No, Unit, Metric, Mode, Warning, Critical, Notify, Status, Actions; toggle Activate/Deactivate; delete via `delete_outline`; Search, Export, Pagination.

### Negative / Edge case
- Warning Limit >= Critical Limit (or otherwise logically inverted thresholds) should be rejected or warned about, not silently saved (a plausible "no validation on numeric config" bug class already seen elsewhere in this app, e.g. Bug #2/#3 in Bug_Report.md for Unit Custom Sensors).
- Saving with a required field missing (Protocol/Unit/Metric) should keep Save disabled or show inline validation.
- Duplicate rule (same Protocol+Unit+Metric+Mode) — does the app block it or silently create a duplicate row?
- Deleting a rule shows a confirmation and actually removes the row (not just visually, verify via refresh).

---

## 8. Live Fleet Map (persistent across CAN pages)

### Positive / Functional
- Map is present and shows `directions_car\n14` (matches fleet count).
- Drag-to-reposition and maximize/fullscreen both work.
- Maximized map exposes vehicle status categories, vehicle markers/clusters, Alerts & Notifications panel (Alerts/Acknowledged tabs), map controls, vehicle selection.
- Clicking a vehicle marker opens a popup with Vehicle/unit name, Status, Speed, Last Contact, Location, and action links (Playback, Alerts, Tracking, Details, Focus on map).

### Edge case
- Empty alerts state on the map panel shows "No Alerts Today" (or equivalent) rather than a blank panel.

---

## 9. Security (cuts across all sections)

- Direct URL access to any `/can/*` route while logged out redirects to login, not a blank/broken page.
- Direct URL access to `/can/*` routes using a **non-CAN** account (e.g. the main `TEST_USERNAME` account, which has no CAN nav link) — verify the app denies access or shows an empty/appropriate state rather than leaking CAN fleet data cross-account.
- CAN Alert Settings Save/Delete actions are not reachable via a crafted request without the appropriate session (basic authz smoke, consistent with this repo's existing `security` marker convention).

---

## 10. Proposed automation layout

Following this repo's existing per-module pattern (Page Object + `Tests/{smoke,positive,functional,negative,edgecase,security}/test_can_*.py`, `data/can.py` fixtures, `test_data/can_*.json` if needed):

```
Pages/can_dashboard_page.py
Pages/can_unit_page.py
Pages/can_trends_page.py
Pages/can_report_page.py
Pages/can_alerts_page.py
Pages/can_settings_page.py

Tests/smoke/test_can_smoke.py
Tests/positive/test_can_dashboard_positive.py
Tests/positive/test_can_unit_positive.py
Tests/positive/test_can_trends_positive.py
Tests/positive/test_can_report_positive.py
Tests/positive/test_can_alerts_positive.py
Tests/positive/test_can_settings_positive.py
Tests/functional/test_can_dashboard_functional.py
Tests/functional/test_can_trends_functional.py
Tests/functional/test_can_report_functional.py
Tests/negative/test_can_trends_negative.py
Tests/negative/test_can_report_negative.py
Tests/negative/test_can_settings_negative.py
Tests/edgecase/test_can_alerts_edgecase.py
Tests/security/test_can_security.py
```

A new `can_credentials` fixture (mirroring `admin_credentials`/`adas_credentials`
in `conftest.py`) and a `can_authenticated_page` fixture (mirroring
`admin_authenticated_page`, logging in with `CAN_TEST_USERNAME`/`CAN_TEST_PASSWORD`
and landing on `/can/dashboard`) would be added to `conftest.py`.

All locators will prefer `get_by_role` / `get_by_label` / `get_by_text` over CSS
or XPath, per this repo's established convention (`Pages/reports_page.py` etc.),
and only fall back to structural locators (e.g. `a[href^='/can/']`) where no
accessible role/name/text exists to key off, as already confirmed necessary
for a couple of the CAN sub-nav links during live exploration.

---

**Awaiting approval before generating any Page Object or test code.**
