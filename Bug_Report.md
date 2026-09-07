# Bug Report — Application Issues Found via Automated Testing

Generated from the Dashboard and Unit module automated test suites. Each item
below is a confirmed **application/backend issue**, not a test or locator
defect — every test/locator problem uncovered along the way was fixed in the
test suite itself and is not listed here. Reproduction is against
`https://staging.trackofy.com` (API host `beta2.trackofy.com`).

## Dashboard Module

### 1. "Today" quick date-filter sends an empty date range
- **Test**: Dashboard card date-filter test (dashboard automation suite)
- **Symptom**: Selecting the "Today" quick filter on a dashboard card issues
  the underlying API request with empty `from_date`/`to_date` parameters
  instead of today's date, rather than filtering to the current day.
- **Impact**: The card silently shows unfiltered (all-time) data instead of
  today's data when a user picks "Today".

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- identical POST body with empty from_date/to_date across 3 independent fresh sessions.
## Unit Module — Custom Sensors

### 2. No validation on Configuration Expression (TC-120)
- **Test**: `Tests/negative/test_unit_sensors_negative.py::test_tc120_invalid_configuration_expression`
- **Symptom**: Entering a malformed Configuration Expression (e.g. missing
  operand/garbled syntax) does not disable **Save Config** and shows no
  inline validation error. The form accepts and submits invalid expressions.
- **Impact**: A user can save a sensor with a broken calculation expression
  with no warning; downstream sensor readings for that config will be wrong
  or fail silently.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- Save Config stayed enabled with no inline error across 3 different malformed expressions, each in a fresh session.
### 3. No maxlength or validation on Sensor Configuration Name (TC-106)
- **Test**: `Tests/edgecase/test_unit_sensors_edgecase.py::test_tc106_exceed_sensor_name_length`
- **Symptom**: The Sensor Configuration Name field has no `maxlength`
  attribute and accepts an unbounded string (tested with 300 characters) with
  no validation error.
- **Impact**: Unbounded input can be submitted to the backend; combined with
  the JS-side table rendering that silently truncates long names with `...`,
  this also produces confusing/unreadable rows in the Custom Sensors list.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- no maxlength attribute, full 300-char value accepted with no validation error, 3 fresh sessions.
### 4. Duplicate sensor name: raw SQL error leaks through the API (TC-104)
- **Test**: `Tests/edgecase/test_unit_sensors_edgecase.py::test_tc104_use_duplicate_sensor_configuration_name`
- **Symptom**: Saving a sensor with a name that already exists returns an
  **HTTP 500** from `POST https://sensor.misbackend.com/api/user/config`,
  with the raw, unhandled database error in the response body:
  ```
  {"message":"ERROR: duplicate key value violates unique constraint
  \"tbl_user_sensor_config_sys_service_id_sensor_name_key\" (SQLSTATE 23505)",
  "status":false}
  ```
- **Impact**: This is a server error (500), not a handled validation
  response (e.g. 400/409 with a clean message) — it indicates the backend
  isn't pre-checking for duplicates before the DB write, and is leaking
  internal schema/constraint details (table and column names) in an
  API response.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- byte-identical raw SQL 500 body on duplicate sensor name across 3 fresh sessions.
### 5. Intermittent 500 from `unit_general/get` on a plain settings reload
- **Test**: `Tests/positive/test_unit_sensors_positive.py::test_tc122_open_add_sensor_configuration`
  (reproduced independently multiple times across different tests)
- **Symptom**: `POST https://beta2.trackofy.com/api/unit_general/get` returns
  `500 {"message": "Server Error"}` during otherwise normal test flows
  (opening/reloading Unit Settings) — no error mocking involved. Reproduced
  both in serial runs and more frequently under concurrent load (multiple
  browser sessions open on the same unit at once).
- **Impact**: The Unit Settings General tab can silently fail to (re)load
  live data; the UI doesn't visibly surface this failure to the user. Also
  observed on `/api/unit-get-profile` and `/api/unit-get-service` under
  concurrent access to the same unit — suggests the backend has a
  concurrency/contention issue when the same unit's data is requested by
  multiple sessions close together, not just plain flakiness.

- **Reverification (2026-09-07, live 3x pass):** NOT REPRODUCED this pass (0/3) -- 3 fresh sessions x 5 sequential Unit Settings reloads (15 cycles total) all returned HTTP 200. Consistent with the bug's own documented intermittent/concurrency-dependent nature (a plain sequential-reload flow doesn't recreate the concurrent-access condition originally implicated) -- not reproducing under this test shape does not invalidate the original finding; kept as documented, not withdrawn.
## Tracking Module

### 6. Playback From/To Date: entered value is silently transposed (day/month swapped)
- **Test**: `Tests/positive/test_tracking_playback_positive.py` (see `_fmt_input`/`_fmt_display`
  helpers, needed to work around this in the test suite itself)
- **Symptom**: The From Date / To Date fields **display** dates as
  `DD/MM/YYYY` (confirmed: the default, untouched value for "today"
  rendered as `03/09/2026` for 3 September 2026). But any value a user
  enters — whether typed with real keystrokes or set programmatically — is
  **parsed as `MM/DD/YYYY`**. Typing "03/09/2026" intending 3 September
  gets silently reinterpreted as 9 March and redisplayed as `09/03/2026`.
  Reproduced identically with real keyboard input (`press_sequentially`),
  ruling out a test-tooling artifact.
- **Impact**: Whenever the intended day is ≤ 12, a user can silently select
  the wrong date for playback with no error or warning — day and month get
  swapped. (When the intended day is > 12, the mismatch would presumably
  surface as a parse/validation failure instead, which is a separate,
  better-behaved case.)
- **Also confirmed in Reports' Start/End Date fields**: entering "03/01/2026"
  intending 3 January (DD/MM) resolves to 1 March, and "03/10/2026"
  intending 3 October resolves to 10 March -- the same MM/DD
  misinterpretation, not isolated to Tracking's playback fields. This is
  what led to discovering bug #17 below (both dates collapsing onto March
  2026 is what surfaced the missing March telemetry partition).

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 on both Tracking Playback's From Date and Reports' Start Date fields.
### 7. "Playback View" preset doesn't reliably return to the Playback tab
- **Test**: `Tests/edgecase/test_tracking_state_edgecase.py::test_trk_state_004_switch_preset_while_playback_active`
- **Symptom**: From a fresh page load, clicking the "Playback View" preset
  button correctly opens the bottom panel on the Playback Tracking tab
  (confirmed via `TRK-NAV-003`). But once playback data has actually been
  loaded and the user then collapses the panel (Map Focus) and reopens it
  via "Playback View" again, the panel comes back showing the **Live
  Tracking** tab instead, even though the playback player controls (Play/
  Restart/speed selector) are still visible on the map above it.
- **Impact**: Inconsistent, state-dependent behavior for the same button —
  confusing for a user who just wants to get back to their loaded playback
  results after toggling the panel.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
## Settings Module — Location Control

### 8. Names are not unique-constrained across Settings entities
- **Test**: `Tests/negative/test_settings_location_control_negative.py::test_set_085_duplicate_location_name_not_prevented`,
  `Tests/negative/test_settings_cross_cutting_negative.py::test_set_196_duplicate_vehicle_group_name_not_prevented`
- **Symptom**: Creating a second record with a name identical to an
  existing one succeeds with no validation error or warning, leaving two
  separate rows sharing the same name. Confirmed on **both** Location
  Control and Vehicle Group -- this is a product-wide gap, not a single
  entity's isolated bug.
- **Impact**: Nothing distinguishes the two records in the UI by name alone
  (e.g. when assigning units to "one of" a duplicated location or group),
  which can lead a user to act on the wrong one.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 on both Location Control and Vehicle Group.
### 9. Assign Unit dialog: "Assign Units" button never enables (feature unusable)
- **Test**: `Tests/positive/test_settings_location_control_positive.py::test_set_086_assign_unit_to_location`
- **Symptom**: In Location Control's "Assign units to location" dialog, picking
  a vehicle from the "Select Vehicles" multi-select visibly registers on the
  option itself (`aria-selected="true"`) and updates the select's own
  displayed value text -- but the dialog's own "X selected" counter badge
  stays at **"0 selected"** regardless of how many options are clicked,
  toggled, or replaced (confirmed live across repeated single/double/triple
  clicks and multiple different vehicles). The **Assign Units** submit
  button stays permanently `disabled` as a result.
- **Impact**: A user cannot assign a unit to a location through this dialog
  at all -- the feature is unusable via the UI, not just awkward. This is
  the most severe finding in this module so far.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 10. POI Alert creation fails server-side despite a fully valid form
- **Test**: `Tests/negative/test_settings_alerts_negative.py::test_poi_alert_create_rejected_server_side`
- **Symptom**: In the "Create POI Alert" dialog, after selecting a unit, a
  POI, and a notification channel, the Angular form itself reports fully
  valid (`ng-valid` on every section and the form element) and the **Create
  Alert** button is enabled -- but clicking it returns an error toast
  reading **"Missing required fields"** and the dialog stays open.
  Reproduced consistently with a fresh unit/POI pair.
- **Impact**: A user cannot create a POI Alert through the UI at all, with
  no indication of which field the client considers satisfied but the
  server does not -- the form gives no actionable feedback.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 11. BMS Alert and Vehicle Odometer Alert: list never shows a newly created record
- **Test**: `Tests/negative/test_settings_alerts_negative.py::test_bms_and_odometer_list_not_refreshed`
- **Symptom**: Creating a BMS Alert or a Vehicle Odometer Alert configuration
  succeeds -- a "Saved" / "Service alert created successfully" success toast
  appears and the dialog closes -- but the list still reads "No BMS alerts
  found" / "No vehicle odometer alerts found" afterward, **even after a full
  page reload**. Reproduced consistently across repeated creations with
  different vehicles.
- **Impact**: A user has no way to see, edit, or delete a BMS/Odometer alert
  they just created through this page -- the record is either not actually
  persisted despite the success message, or the list is scoped by a hidden
  default filter that excludes it either way, the UI gives no way to verify
  or manage what was just configured.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 for both BMS Alert and Vehicle Odometer Alert.
### 12. Leaving the Create Route page (Save or Cancel) redirects to the Dashboard instead of back to Route Management
- **Test**: `Tests/positive/test_settings_route_positive.py::test_set_156_create_valid_route`,
  `Tests/functional/test_settings_route_functional.py::test_set_168_open_custom_route_tab`
- **Symptom**: Clicking **Save Route** on the Create Route page succeeds (a
  "Route saved successfully" toast appears and the route is genuinely
  created) but the app then navigates to **`/home`** (the main Dashboard)
  instead of back to `/settings/route` (Route Management), where the user
  was working. The same **`/home`** redirect was also reproduced from
  **Cancel** on the Custom Route sub-tab with no changes made at all --
  suggesting the create-route page's "return" navigation is generally
  hardcoded to the Dashboard rather than back to Route Management.
  Reproduced consistently.
- **Impact**: A user who just created a route (or simply backed out of the
  form) is unexpectedly bounced out of Settings entirely and has to
  re-navigate back to Route Management -- confusing, and inconsistent with
  every other Settings entity's create/cancel flow (all others return to
  their own list).

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 for both Save Route and Cancel.
### 12b. Driver list export downloads a file misnamed "Unit_List"
- **Test**: `Tests/functional/test_settings_cross_cutting_functional.py::test_set_184_export_contains_correct_data`
- **Symptom**: Exporting the Driver list to CSV produces correct driver data
  (Name, DL No, Assigned Unit, DOB, Email, Contact, Address columns with
  real driver rows) inside the file, but the downloaded **filename** reads
  `Unit_List_(<date>).csv` -- a name belonging to a different module (Unit),
  not Driver.
- **Impact**: A user exporting drivers gets a file that looks, by name
  alone, like it belongs to the wrong dataset -- confusing when managing
  multiple exports, and suggests the export filename isn't wired per-entity.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 12c. Create Driver: raw SQL truncation error leaks through the API when email is too long
- **Test**: found via `Tests/negative/test_settings_cross_cutting_negative.py::test_set_197_whitespace_handling_in_driver_name`
  (reproduced independently of the whitespace scenario the test was written for)
- **Symptom**: Submitting a valid-looking Create Driver form with an email
  address around 31+ characters returns an **HTTP 500** from
  `POST /api/add-driver` with the raw, unhandled SQL Server error in the
  response body:
  ```
  SQLSTATE[42000]: [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
  String or binary data would be truncated in table
  'atltracking.dbo.tbl_driver_master', column 'email'.
  ```
  No client-side length validation exists on the Email field to catch this
  before submit. Same class of issue as bug #4 (Unit Custom Sensors'
  duplicate-name SQL error) -- the backend isn't validating input length
  before the DB write, and leaks internal schema/connection details
  (table/column names, DB host, full SQL statement) in the API response.
- **Impact**: A realistic driver email (e.g. `firstname.lastname@company-name.com`)
  can trivially exceed whatever this column's length is, causing an
  unhandled server error instead of a clean validation message -- and the
  form gives no indication beforehand that Email has a length limit at all.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- identical SQLSTATE truncation error every time; also observed the same class of bug triggers off an over-length Name value, truncating at the name column instead -- worth noting as a related manifestation, not a separate bug.
### 13. Route Name is not actually enforced as mandatory
- **Test**: `Tests/negative/test_settings_route_negative.py::test_set_157_route_name_mandatory`
- **Symptom**: Leaving the route name blank and saving a route (with valid
  origin/destination) succeeds anyway -- a "Route saved successfully" toast
  appears and the route is created. The app appears to silently default the
  name to **"My Route"** rather than rejecting the submission, contradicting
  the documented requirement that route name is mandatory. Reproduced
  consistently.
- **Impact**: Route names lose their purpose as a unique, recognizable
  identifier (the create form's own hint text says "Enter a unique and
  recognizable route name") -- an account can accumulate multiple
  indistinguishable "My Route" entries with no way to tell them apart in
  the list.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 14. Driver create form: Address field is silently required
- **Test**: found while building `Tests/positive/test_settings_driver_positive.py`
- **Symptom**: The **Create Driver** button stays disabled until the Address
  field is filled, but Address carries no visible required-field indicator
  (no asterisk), unlike Name/Mobile/Email/DOB/DL fields which do.
- **Impact**: A user filling only the visibly-marked required fields will
  be stuck with a disabled Create button and no explanation why.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 15. Driver create form: Address field visually appears empty after typing
- **Found by**: manual testing (reported directly, not yet reproduced by an
  automated test)
- **Symptom**: The Address field is a multi-line textbox. After typing an
  address, the field appears empty -- the typed text is present (on the
  first line) but the box's visible viewport shows further down (around the
  last line), so with nothing typed below the first line the visible area
  looks blank.
- **Impact**: A user has no visual confirmation that their address was
  actually entered; combined with bug #14 above (no required-field
  indicator on this field), a user could reasonably conclude the field is
  optional, type nothing, and be blocked by a disabled Create button they
  can't explain -- or type an address, see what looks like an empty box,
  and re-type it, potentially duplicating content.
- **Follow-up**: worth an automated regression test (fill the field, assert
  the visible viewport/scroll position shows the entered text, e.g. via the
  input's `scrollTop` or a screenshot-based check) -- not yet added.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- and more severe than originally described: the typed text rendered fully invisible in the textarea, not just the lines past the first.
## Reports Module

### 17. Vehicle Summary, Trip Report and Cumulative Distance fail with a raw SQL error for any date range whose monthly telemetry table doesn't exist
- **Tests**: `Tests/negative/test_reports_standard_negative.py::test_rep_missing_telemetry_partition_table`
  (regression pin, `Trip Report` / `Cumulative Distance` @ Feb28-Mar10 2026), plus incidental hits from
  `Tests/edgecase/test_reports_standard_edgecase.py::test_rep_com_008_no_data_range_report` and
  `test_rep_std_no_data_range` (`Vehicle Summary` @ Jan 2020 and Jan 2026)
- **Symptom**: Generating any of these three reports for a date range whose month has no
  telemetry data returns an **HTTP 500** from `POST /api/v3/vehicle_summary`,
  `POST /api/v3/trip_report_new`, or `POST /api/v3/cumulative_distance`, with the raw SQL
  Server error in the response body, e.g.:
  ```
  SQLSTATE[42S02]: [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
  Invalid object name 'tbl_telemetry_mar26'.
  ```
  The backend stores telemetry in monthly-partitioned tables (`tbl_telemetry_<mon><yy>`)
  and these three reports' queries reference that month's partition table directly. When no
  partition exists for the requested month -- confirmed for `tbl_telemetry_mar26` (Mar 2026),
  `tbl_telemetry_jan26` (Jan 2026), and `tbl_telemetry_jan20` (Jan 2020, a genuinely
  data-free historical range) -- the query throws instead of returning zero rows. This is
  **not** limited to one specific month: it reproduces for any month (past, near-future, or
  a deliberately empty historical range) where the account has no telemetry, meaning it will
  hit in production for any customer/vehicle/period combination without data -- exactly the
  "no data" case a report UI most needs to handle gracefully. Confirmed across three
  different report types and three different months hitting the same missing-partition
  pattern, so this is a shared backend/data-provisioning issue in how these three reports'
  queries are built, not one report's or one month's isolated bug.
- **Impact**: These three reports are unusable -- with an unhandled server error exposing
  internal schema/connection details (table name, DB host, full SQL) instead of a report or
  a clean "no data" state -- for *any* date range touching an unpopulated month, which
  includes the ordinary "I picked a range with no data" case every report should support.
  Other reports queried against the exact same account/vehicle/range (Distance Chart, Idle,
  Alert, Running Summary, etc.) succeeded, confirming the break is specific to whichever
  reports build queries against the monthly partition table directly rather than going
  through a date-range-safe abstraction.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 across all three affected report types (Vehicle Summary, Trip Report, Cumulative Distance).
### 18. Fleet Summary KPI cards can display a stale value from an earlier, slower request
- **Test**: `Tests/negative/test_reports_kpi_table_negative.py::test_rep_kpi_023_no_stale_kpi_from_earlier_request`
  (regression pin)
- **Symptom**: The KPI cards (Total Units, Ignition On, Moving Units, etc.) are populated
  from a separate `POST /api/v3/fleet_summary_aggregate` call, independent of the table's
  `POST /api/v3/fleet_summary_new` call. There is no request-sequencing guard (no request
  ID/token check, no in-flight request cancellation) on the aggregate call: reproduced by
  triggering an all-vehicles Fleet Summary generation (slow -- artificially delayed 4s in
  the test to simulate real-world slowness), then immediately switching to a single-vehicle
  Fleet Summary generation (fast, resolves first). The UI correctly shows Total Units = 1
  right after the second (fast) request resolves, but once the first (slow) request's
  response finally arrives, it **overwrites the KPI cards back to Total Units = 36** -- the
  stale all-vehicles value -- even though the currently-selected filter and currently-shown
  table are for the single vehicle. Confirmed deterministically reproducible (not a one-off
  flake) across repeated runs.
- **Impact**: Any time a user changes report filters and re-generates before a previous,
  slower request has finished (a plausible action on a real network, not just an artificial
  delay), the KPI cards can silently revert to showing data for a filter combination the
  user is no longer looking at, while the table itself displays the correct, current data --
  i.e. the KPI cards and the report table can visibly disagree with each other after normal,
  ordinary use.

- **Reverification (2026-09-07, live 3x pass):** NOT REPRODUCED this pass -- the app now blocks the UI action needed to create the interleaving (the Filters/Generate control stays non-interactive until the in-flight slow request resolves), so the described request race could not be triggered via the UI across 6 attempts using 2 different methodologies. Possibly fixed since the original finding, or requires bypassing the UI with raw concurrent API calls to reach -- flagged for follow-up rather than closed outright.
### 19. A failed report-generation request leaves the UI permanently stuck on "Generating..."
- **Test**: `Tests/edgecase/test_reports_standard_edgecase.py::test_rep_rel_004_005_network_failure_then_retry_recovers`
  (regression pin)
- **Symptom**: If the report-table API call (`POST /api/v3/fleet_summary_new`) fails at the
  network level (e.g. connection dropped -- simulated in the test via aborting the request),
  the Generate button switches to a "Generating..." loading state and **never leaves it**.
  Confirmed it is still stuck after 20+ seconds, with no error message, no retry affordance,
  and the button itself becomes unqueryable by its normal accessible name ("Generate"/
  "Generate report") since its label is now permanently "Generating...". There is no
  timeout or failure handling on the frontend for this request at all.
- **Impact**: Any real network hiccup during report generation (not just an artificial
  network failure) permanently locks the user out of that report -- they cannot retry, see
  no explanation, and the only observed way to escape the stuck state is to leave the report
  form (Back) and start over. This directly fails the expected behavior "loading ends safely
  and an error/retry state is shown" -- neither happens.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 20. Fleet Summary with all vehicles selected hangs on "Generating..." forever, even though both backend calls succeed
- **Tests**: surfaced as cascading failures across
  `Tests/edgecase/test_reports_kpi_table_edgecase.py` (REP-KPI-016 through 021, 031/032),
  `Tests/edgecase/test_reports_downloads_edgecase.py::test_rep_dl_134_...`, and
  `Tests/functional/test_reports_generation_smoke.py`
- **Symptom**: Selecting **all** vehicles (36, via the "Select All" checkbox) for Fleet
  Summary and clicking Generate never renders a result. Confirmed live, reproduced twice:
  the Generate button permanently relabels to "Generating..." and stays stuck past 45+
  seconds -- but unlike Bug #19, this is **not** a network failure: both underlying API
  calls (`POST /api/v3/fleet_summary_aggregate` and `POST /api/v3/fleet_summary_new`)
  return **HTTP 200** within the wait window, and no browser console error or uncaught page
  exception was observed. The frontend receives successful data for the full fleet and
  simply never transitions out of the loading state to render the table/KPI cards. The
  table element that is present shows 10 rows the whole time, appearing to be a static
  loading skeleton (page size default) rather than real data -- `get_pagination_total()`
  reads back `0` throughout, confirming no real dataset ever gets bound to the view.
  Generating Fleet Summary for a **single** vehicle works normally and quickly (confirmed
  repeatedly throughout this test session); the break is specific to the full/all-vehicles
  selection.
- **Impact**: "Select All" is a first-class, prominently offered control on every Standard
  report's vehicle picker, and Fleet Summary is the flagship report exposing the account's
  headline KPI cards -- so this is the single most likely real workflow ("show me my whole
  fleet") to hit a completely broken, silent hang with zero error feedback and zero
  affordances (no cancel, no retry, no message) to escape it.

- **Reverification (2026-09-07, live 3x pass):** NOT REPRODUCED this pass -- an initial false positive (a stale "Generating..." label sitting in a closed, off-screen Filters drawer) was ruled out; on proper re-test, all-vehicles Fleet Summary rendered correctly with real data in 2.3-6.9s across 6 attempts (3 all-vehicles + 3 single-vehicle), no hang, no stuck skeleton rows, no zero pagination. Possibly fixed since the original finding.
---

## Home Module

### 21. KPI Settings' "Select All" paradoxically deselects down to the protected minimum when everything is already selected
- **Test**: `Tests/functional/test_home_kpi_functional.py::test_home_0058b_select_all_when_already_full_drops_to_minimum`
  (regression pin)
- **Symptom**: In the Home page's KPI Settings dialog, the "Select All" button/link correctly
  selects every KPI when starting from a partial selection. But clicking it again while
  **already** at full selection (10 of 10) does not stay at 10 (a true idempotent "select
  all") -- it drops the selection down to the account's protected minimum of 6, confirmed
  deterministically reproducible across repeated runs. The button's visible label stays
  "Select All" throughout (it does not relabel to "Deselect All" or similar), so there is no
  UI indication that clicking it again will remove KPIs rather than leave them selected.
- **Impact**: A user who opens KPI Settings (already fully configured, the account's
  default) and clicks "Select All" out of habit or to confirm everything is selected will
  instead silently lose 4 of their 10 configured KPIs from the header the moment they hit
  Save -- data loss from a control whose label promises the opposite of what it does.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 22. Two of a Group's five status chips ("Active" and "No Data") always filter Fleet to zero vehicles
- **Tests**: `Tests/functional/test_home_groups_drivers_functional.py::test_home_0109b_active_group_filter_yields_zero_bug`,
  `test_home_0109c_no_data_group_filter_yields_zero_bug` (regression pins)
- **Symptom**: On the Home page's Groups tab, each group card shows status chips
  ("Active (N)", "Running (N)", "Idle (N)", "Stopped (N)", "No Data (N)"), all
  presented as clickable filters. Running/Idle/Stopped correctly filter Fleet to
  a matching vehicle count (confirmed reconciling exactly). "Active" and "No
  Data", however, both always filter Fleet to **0** vehicles regardless of
  which group is clicked or how large the chip's own count is -- confirmed for
  "Active" across all 4 of this account's groups (Default 30, Delhi 3, Bhopal
  2, Dwarka 1, every one 0 results) and confirmed for "No Data" on both a
  large sample (Default, 11) and a single-vehicle group (Dwarka, 1), ruling out
  a small-N edge case. "Active" is a derived aggregate (Running + Idle) rather
  than a literal per-vehicle status value, and "No Data" likely maps to a
  different literal/null representation on the backend than the filter sends --
  in both cases the filter appears to search for an exact status match that no
  vehicle record actually satisfies, rather than the correct query.
- **Impact**: These are 2 of the 5 status filters offered on every group card
  (including the first, most prominent one, "Active"), and each chip's own
  label promises exactly the vehicles it fails to show -- a user clicking
  "Active (30)" or "No Data (11)" gets an empty list with no error, which reads
  as "none of your vehicles match" rather than the broken filter it actually
  is.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3, tested across 2 different groups x 2 chips per run (6 combinations total, all 3 runs).
### 23. A "Map only" GeoLink still exposes the vehicle's identifying registration number to anonymous visitors
- **Test**: `Tests/functional/test_home_geolinks_functional.py::test_home_0260_map_only_geolink_does_not_expose_vehicle_details`
  (regression pin)
- **Symptom**: The GeoLinks feature offers two access levels when creating a
  public share link, with the app's own labels: "Map only" ("Vehicle location
  without details") and "Map and details" ("Location with vehicle
  information"). Creating a "Map only" link, then opening its real public URL
  (`.../geolink/redirect?token=...`) in a genuinely unauthenticated browser
  context (no login, no cookies -- exactly how a recipient would open a
  shared link) shows the vehicle's full registration/identifying string (e.g.
  `GCBL10536MHG11CG06066`) directly on the page, alongside status and
  distance. This directly contradicts "Map only"'s own stated promise of
  "vehicle location **without details**".
- **Impact**: This is the security boundary the whole GeoLinks access-level
  control exists to enforce. Anyone who creates a "Map only" link believing
  they are sharing an anonymous location pin -- e.g. sharing a link with a
  customer or a delivery-tracking recipient who should not see the vehicle's
  registration/fleet-identifying number -- is actually exposing that
  identifying data to them regardless. This is a real information-disclosure
  issue via a control specifically marketed as more restrictive.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
---

## Administrator Module

### 25. Closing the Create User wizard without clicking Submit still permanently creates the user
- **Test**: `Tests/functional/test_admin_wizard_navigation_functional.py::test_adm_053_close_wizard_without_submit_still_creates_user`
  (regression pin)
- **Symptom**: The Create User wizard's Step 1 -> Step 2 transition ("Next
  Step") makes a real, immediate `POST /api/save_subuser` call and persists
  the user record right there -- confirmed live via network response
  logging, not an assumption. Every later step (menu group assignment,
  general permissions, unit permissions) is a *separate* API call
  (`/api/v1/groups/assign`, `/api/v1/set-user-permissions`) layered on top of
  that already-created user. Closing the wizard via the "X" icon at any
  point after Step 1 -- confirmed reproducible after progressing all the way
  to Step 4 without ever clicking the final "Submit" button -- does **not**
  roll back or delete that user. Confirmed with a direct before/after user
  count across a page reload (25 -> 26, and the exact closed-mid-wizard
  username was present as a real row in the table) -- this is not a stale
  UI artifact, it is a permanently persisted account.
- **Impact**: This directly contradicts the application's own design intent
  (per `Trackofy_Administrator_Module_Explanation.md` section 3: "A user
  should be considered created only after the final submission succeeds").
  An administrator who fills in Step 1, then decides to cancel or close the
  wizard for any reason -- before configuring menu access, permissions, or
  unit scope -- ends up with a real, logged-in-capable sub-user account
  sitting in User Management with **default/empty authorization** (no menu
  group, no general permissions, no unit permissions explicitly set),
  created without their knowledge or confirmation. Given this module's own
  stated purpose is strict access control, silently creating unauthorized-
  by-omission-but-still-real accounts through an abandoned form is a
  meaningful security and data-integrity issue, not just a UX rough edge.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 26. "Add Group" on the Create User wizard re-fetches its (static) menu list from the API on every click, with no loading indicator, and no debounce -- causing a multi-second open delay and stacked duplicate dialogs on repeat clicks
- **Tests**:
  `Tests/functional/test_admin_menu_access_functional.py::test_adm_065_add_group_opens_new_group_dialog`,
  `Tests/functional/test_admin_menu_access_functional.py::test_adm_065b_rapid_add_group_clicks_stack_duplicate_dialogs`
  (regression pin)
- **Symptom**: Step 2 (Menu Access) of the Create User wizard shows an "Add
  Group" button. Clicking it does eventually open an "Add New Menu Group"
  dialog (Group Name + a checklist of menus to include), but only after a
  real, unindicated delay -- confirmed live it had *not* appeared after 3
  seconds (my original investigation stopped there and wrongly concluded the
  button did nothing) but *had* appeared by 5 seconds. Root cause, per the
  user's own network inspection: the delay is a real API call fetching the
  menu list for the new-group form, re-issued fresh on every single click --
  despite the response being effectively static (the same available-menus
  list every time within a session), so nothing justifies re-fetching it
  instead of fetching once and reusing/caching it client-side. There is no
  spinner, disabled state, or any other loading feedback during this window,
  so the control looks inert rather than busy. Because there's also no
  debounce, clicking it multiple times while waiting fires that same
  redundant API call again each time and stacks one independent "Add New
  Menu Group" dialog per click -- confirmed live via `.cdk-overlay-pane`
  count going from 1 (the wizard itself) to 4 after 3 rapid clicks. Each
  stacked dialog must then be closed one at a time.
- **Impact**: Three compounding issues. (1) A static, cacheable menu list is
  re-fetched from the API on every open instead of once -- pure wasted
  network/server load with no user-visible benefit, and the direct cause of
  the delay. (2) No loading affordance during that delay makes the control
  look broken, which is exactly what invites a real user to click it again.
  (3) The lack of any debounce/disable-while-opening on the button means
  every extra click compounds into another full redundant API call plus
  another full dialog instance, degrading into a stack the user has to
  manually dismiss one-by-one -- a real performance and state-management
  defect, not just a cosmetic one. Fix suggestion: fetch the menu list once
  (cache it for the wizard's lifetime, or at least session-scope it) and
  disable/debounce the "Add Group" button while a fetch or dialog-open is
  already in flight.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 for the stacking defect; the open-delay is confirmed present every time (1.16-1.29s) though measured smaller than the originally reported ~5s.
### 27. Step 4's unit selector is a separate, unfiltered picker over the entire fleet, disconnected from Step 1's vehicle scope (confirmed harmless, UX-only)
- **Test**: `Tests/functional/test_admin_authorization_functional.py::test_authz_bug27_unit_permission_without_scope_is_inert`
- **Symptom**: Step 1's vehicle selector is explicitly documented (design
  doc, "Step 1 -- Personal Info", 4.1 Vehicle Selection) as establishing
  "the user's vehicle scope for the configuration." Step 4's unit selector
  is a completely independent multi-select showing the *entire* fleet --
  confirmed live: with only `HP12G9691` selected in Step 1, Step 4 still
  listed 30+ other vehicles never chosen in Step 1 (`GCBL10536MHG26DG07485`,
  `GCBL10536MHG28GG12907`, etc.), with no visual indication of which
  options are actually in the Step-1 scope and which aren't. Reported
  directly by the user, who asked why a vehicle already selected in Step 1
  needs to be selected again from scratch in Step 4.
- **Resolved (Phase 8 effective-authorization test)**: created a sub-user
  scoped to one vehicle only in Step 1, granted a Step 4 Unit Permission
  (Manage Services) for a *second*, never-assigned vehicle, then logged in
  as that sub-user and checked the real fleet list. The unscoped vehicle
  was correctly absent -- the Step 4 permission had no effect without Step
  1 scope, exactly as the design doc's model intends. **The possible
  scope-bypass concern originally raised here is ruled out**; enforcement
  is correct.
- **Impact (final, UX/data-integrity only)**: An administrator can still
  spend time configuring detailed per-vehicle Unit Permissions for a
  vehicle that was never granted to the sub-user in Step 1, with no
  warning that the configuration is inert -- confusing and wastes
  administrator effort, but confirmed harmless from a security standpoint.
  Worth a UX fix (filter Step 4's list to Step 1's scope, or at least
  visually flag out-of-scope options) but not a security bug.

### 28. [CRITICAL] Clicking "Edit" on a user row opens a completely different, unrelated user's data
- **Test**: `Tests/functional/test_admin_submit_flow_functional.py::
  test_adm_28_edit_opens_wrong_users_data` (regression pin). Reproduced
  live at least three times, independently, across fully separate browser
  sessions/pytest runs.
- **Symptom**: Created a new sub-user (e.g. `pytestedita2868711`), searched
  User Management down to exactly that one matching row (confirmed via
  `matching_record_count=1` and reading the row's own username cell back:
  `'pytestedita2868711'`), then clicked that exact row's "Edit user" button.
  The dialog that opened was titled **"Edit Units for Tarunn"** -- a
  pre-existing, completely unrelated username, not the one clicked or
  searched. Repeated with a second, differently-named fresh user in an
  independent test run (separate browser session, separate login): same
  result, same wrong username ("Tarunn") both times. The dialog itself
  (Assigned Units / Vehicles / Cancel / Save) is real and functional -- it
  is simply bound to the wrong user's data.
- **Re-verified after user pushback (important)**: the user reasonably
  questioned whether this was actually a stale/leftover dialog artifact
  rather than a real bug, since this app is separately confirmed (Bug #26)
  to leave orphaned dialogs sitting in `.cdk-overlay-container` without
  cleaning them up. Re-tested with an explicit check: counted
  `.cdk-overlay-pane` elements immediately before clicking Edit (**0**,
  confirming a completely clean overlay state -- no possibility of a
  stale leftover) and immediately after (**exactly 1**, genuinely
  visible). That single, freshly-created pane still showed "Edit Units for
  Tarunn" instead of the clicked user. This rules out the stale-dialog
  explanation -- the wrong-user binding is a real defect, not a test
  artifact.
- **Impact**: An administrator clicking Edit on a specific, deliberately
  chosen user can silently end up editing a different real user's unit
  assignments instead -- with the dialog title being the only signal
  something is wrong, easy to miss in normal use. If Save is clicked in
  this state, it would modify the wrong user's vehicle access. This is a
  serious data-integrity and access-control bug: an admin could
  unknowingly grant or revoke vehicle access for the wrong account
  entirely. Given "Tarunn" reproduced consistently across independent
  sessions rather than varying, this looks like a stale/uninitialized
  reference in the edit dialog's data-binding (e.g. defaulting to some
  fixed prior state) rather than a random race condition -- worth the
  product team prioritizing given the severity.
- **Supporting evidence**: the regression-pin test for this bug
  (`test_adm_28_edit_opens_wrong_users_data`) also triggered a real backend
  500 error caught by this suite's global server-error check:
  `POST https://beta2.trackofy.com/api/v1/get-permission-types -> 500
  {"message": "Server Error"}`. This fired during the same Edit-click
  interaction and is plausibly the same root cause surfacing twice: the
  edit flow resolving to a bad/stale user reference, which then fails
  server-side when that reference is used to fetch permission types.
  The same `get-permission-types -> 500` recurred again independently
  during Phase 9 (Permissions dialog, Unit Permission tab, after selecting
  a vehicle), this time alongside a second endpoint also 500ing:
  `POST https://beta2.trackofy.com/api/v1/groups/list -> 500`. Both
  reproductions correlate with the Unit Permission tab's checkbox for the
  selected vehicle failing to render at all -- ADM-169 was skipped for
  this reason (see `test_admin_edit_permissions_functional.py`). Given two
  independent endpoints failing on this same tab/flow across separate
  sessions, this looks like a real, if intermittent, backend stability
  issue specifically affecting the Unit Permission tab's data loading, not
  just a one-off.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3, including the stale-dialog-artifact control (0 overlay panes immediately before the Edit click, exactly 1 immediately after) ruling out the alternate explanation in every attempt.
### 29. Menu Access is only enforced by hiding nav items -- direct URL navigation reaches modules a SUB-USER was never granted
- **Scope note (important)**: this is about a **sub-user** account created
  through the Administrator wizard, logged in on its own -- NOT the
  administrator/owner account itself. The owner naturally has full access
  to everything including `/administrator`; that is expected and is not
  what this bug is about. Confirmed with the user directly: they manually
  tested reachability using their own owner/admin account, which is a
  different scenario from this finding and does not conflict with it.
- **Test**: `Tests/functional/test_admin_authorization_functional.py::
  test_authz_bug29_direct_url_bypasses_menu_access` (regression pin)
- **Symptom**: Created a sub-user with menu group "example21", which grants
  only Home/Dashboard/Tracking -- confirmed live the top nav for this
  *sub-user* shows exactly those three modules; Unit, Reports, Settings,
  Administrator and Video Telematics are all correctly absent from the
  nav. However, navigating this same logged-in sub-user directly to
  `/settings/driver` loads the real Settings page shell (empty module list,
  "No settings found" / "Menu access follows assigned permissions" --
  no Driver data rendered, so no immediate data leak there). More
  seriously, navigating directly to `/administrator` loads the real
  Administrator / User Management page shell (heading, table, pagination
  controls, search -- a fully functional page, showing "0 users") for a
  sub-user whose menu group never included Administrator at all and who,
  per the module's own design, should never be able to reach Administrator
  under any configuration (it is meant to be exclusively an
  owner/administrator surface). Neither URL redirected away or showed an
  access-denied state; both stayed on the requested URL and rendered a
  real page.
- **Impact**: Menu Access is implemented as client-side nav-item hiding
  only, not as an enforced route guard. A sub-user who knows or guesses a
  module's URL can reach pages they were never granted -- for
  `/administrator` specifically this means any sub-user, regardless of
  configuration, can load the User Management page shell. The "0 users"
  shown appears to be safely scoped (no other admin's real sub-user data
  was exposed in this repro), so the immediate data-exposure risk observed
  is limited, but the page being reachable at all defeats the point of
  Menu Access as an authorization boundary and is exactly the scenario
  the design doc's own ADM-069 test case ("Verify direct URL block") is
  meant to catch. Recommend server/route-level enforcement, not just
  hiding the nav link.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 30. General Permission category "User" (Create User wizard, Step 3) is relabelled "Global" in the Permissions dialog's General Permission tab
- **Test**: not yet automated as a regression pin -- a minor consistency
  note found while building Phase 9 (Edit/Permissions coverage).
- **Symptom**: The Create User wizard's Step 3 lists a General Permission
  category named "User" (4 permissions: Edit User, Change Password, Delete
  User, Create user -- confirmed live). The exact same category, in the
  same account, on the same user, reopened via the row's "Permissions"
  (manage_accounts icon) action's General Permission tab, is labelled
  "Global" instead.
- **Impact**: Minor -- same underlying permission set, just an
  inconsistent label between two surfaces that edit the same data. Could
  confuse an administrator trying to find "User" permissions again after
  first seeing them during creation. Low priority, cosmetic/consistency
  fix.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 31. Unicode (non-Latin) characters in a username are corrupted to literal "?" characters
- **Test**: `Tests/functional/test_admin_data_integrity_functional.py::test_adm_unicode_username_handled_cleanly`
  (regression pin)
- **Symptom**: Created a sub-user with a Chinese-character username
  (`用户<unique suffix>`). After creation and a fresh page reload, the
  username displayed in User Management is `??<unique suffix>` -- the two
  Chinese characters became two literal question marks. This is real
  character corruption, not a missing-font rendering issue: a font that
  lacks CJK glyphs shows empty "tofu" boxes, not the literal `?`
  character, so the `?`s indicate the actual character data was replaced
  during some step of the save/reload/render pipeline (a classic sign of
  a text encoding mismatch, e.g. non-UTF-8 handling somewhere in the
  request, storage, or response path).
- **Impact**: Any administrator creating a sub-user with a non-Latin
  username (a very ordinary thing to do for a non-English-speaking team)
  gets that username silently and permanently mangled. This is a data-
  integrity bug, not cosmetic -- the original username is lost and
  replaced with `??...`, which could also affect login (unclear whether
  the stored/hashed credential still matches the original Unicode string
  the administrator typed, or the corrupted one) and is worth the product
  team's attention.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 32. "User already exists" error for common usernames the account doesn't actually have -- username uniqueness appears to be checked globally, not per-account, with a misleading error message
- **Test**: not yet automated as a regression pin -- reported directly by
  the user, then confirmed live.
- **Symptom**: Reported directly by the user: attempting to create a
  sub-user named "test" in an account whose *only* existing user is
  "bruce" fails with the error toast `user_alread_exist` [sic, app's own
  typo]. Confirmed live and reproduced with several other common/generic
  words: "test", "admin", and "demo" **all** fail with the identical
  "already exists" error despite none of them existing anywhere in this
  account (confirmed via a full list read before and after, showing only
  "bruce"). By contrast, a more specific candidate ("user1") was accepted
  and created a real user normally. The underlying `POST
  /api/save_subuser` call for the rejected candidates returns HTTP **200**
  (success) -- the error is being surfaced from data inside a
  200-status response body, not a proper 4xx error status, which is a
  separate minor API-design smell.
- **Impact**: This strongly suggests username uniqueness is enforced
  **globally across the entire Trackofy platform** (all accounts/tenants),
  not scoped to the administrator's own account -- "test"/"admin"/"demo"
  are presumably already taken by *some* account somewhere in the system.
  If that's the intended design, the error message is still a real
  usability bug: "user already exists" reads as "already exists in your
  account" on a screen titled "User Management" scoped to this
  administrator's own users, and there is nothing in the UI clarifying
  the check is actually global. An administrator has no way to tell a
  genuine same-account duplicate apart from an unrelated global
  namespace collision, and no guidance on what to do about it beyond
  guessing a different name. Recommend either scoping the uniqueness
  check per-account (if that's actually the intent) or, at minimum,
  wording the error to make clear the collision is with a username taken
  elsewhere on the platform, not within this administrator's own users.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 (9/9 individual attempts across "test"/"admin"/"demo") -- confirmed HTTP 200 with status:false, message:"user_alread_exist" [sic] every time.
### 33. [Low] No show/hide (eye) toggle on the Password / Confirm Password fields in the Create User wizard
- **Test**: `Tests/functional/test_admin_create_user_step1_functional.py::
  test_adm_bug33_no_password_visibility_toggle_in_wizard` (regression pin)
- **Symptom**: Reported directly by the user. Confirmed live: Step 1's
  Password and Confirm Password inputs are plain `type="password"` fields
  with no visibility-toggle button/icon anywhere in their container --
  checked all 7 buttons in the wizard dialog and none relate to
  password visibility. This is inconsistent with the rest of the module:
  the User Management table's own password column has a working "Show
  password" reveal toggle per row (confirmed and tested in Phase 1), so
  the capability exists in this app generally, just not on the entry
  form itself.
- **Impact**: Low priority, but a real usability pain point -- while
  typing a new password (and its confirmation) during user creation, the
  administrator has no way to visually verify what they typed, other than
  retyping carefully or making a typo that only surfaces later as a
  mismatched-password error. Recommend adding the same reveal-toggle
  pattern already used in the User Management table to both password
  fields in the Create User wizard (and, if applicable, in the Edit/
  Permissions surfaces if a password field exists there too).

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
---

## Miscellaneous Pages Module

### 34. At mobile viewport widths, the Account menu (My Profile, Support, Change Password, Language, Sign Out) is not reachable through any UI control
- **Test**: `Tests/functional/test_misc_account_menu_functional.py::
  test_misc_012_account_menu_responsive` (regression pin)
- **Symptom**: At a 390x844 (phone-sized) viewport, the desktop
  `account_circle` avatar button that opens the Account menu becomes
  genuinely invisible (confirmed live: `visible=False`, though the
  element still exists in the DOM). In its place, the responsive layout
  shows a hamburger ("menu") toggle and an inline "Actions" panel listing
  only Applications, Appearance (relabelled "Light Mode" here), Chatbot,
  Downloads, and Notifications. Clicking the hamburger toggle does not
  reveal the missing items -- it only opens/closes the same primary nav
  list already visible (Home/Dashboard/Unit/Tracking/Reports/Settings/
  Administrator/Video Telematics). No alternative control anywhere in the
  mobile layout was found that opens My Profile, Support, Change
  Password, Language, or Sign Out.
- **Impact**: A user on a phone-sized viewport cannot access their
  profile, raise or view support tickets, change their password, change
  their language, or **sign out** -- Sign Out being unreachable is a real
  usability and security concern (a shared/borrowed mobile device can't
  be logged out of through the normal UI at all). Downloads and
  Appearance are the only Account-menu-equivalent items that did carry
  over into the mobile "Actions" panel; the rest were simply dropped from
  the responsive layout rather than relocated.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 35. [CRITICAL, escalated] Raise Support Ticket cannot be submitted -- "X selected" vehicle counter never updates, and Submit stays permanently disabled even when every field is genuinely valid
- **Test**: not yet automated as a regression pin -- to be added to Phase 5
  (`Tests/functional/test_misc_raise_ticket_functional.py`).
- **Symptom (original, display-only)**: In the Raise Support Ticket
  dialog's Unit Selection section, the vehicle multi-select genuinely
  works correctly at the component level -- confirmed live: after
  selecting 3 vehicles, the underlying `mat-select`'s own displayed value
  correctly lists all three (`GCBL10536MHG26DG08215, 869630055281111,
  GCBL10536MHG01DG07317`) and each clicked option's `aria-selected`
  attribute correctly flips to `"true"` (persists correctly on reopening
  the dropdown too). However, the separate "X selected" counter text
  shown above the selector (design doc §6.1: "A selected-count indicator
  is shown") stays permanently at **"0 selected"** no matter how many
  vehicles are actually selected.
- **Escalation -- Submit never enables**: while building out the full
  submission flow, found that **the Submit Ticket button never becomes
  enabled**, even with a completely valid form: a real vehicle selected
  (confirmed `aria-selected="true"`), Category and Severity chosen
  (confirmed selected text replaces the placeholders), a valid Comment
  (confirmed its own 33/200 counter updates correctly), and valid
  Email/Mobile values. Verified exhaustively across four different input
  methods (`fill()`, `fill()` + Tab, real keyboard `type()`, and
  click-to-focus + `type()` + click-elsewhere-to-blur) -- Submit stayed
  disabled every time. Checked for validation errors directly (`mat-error`
  elements): **zero found**. Checked Angular's own computed CSS state on
  the Email field: `ng-dirty ng-valid ng-touched` -- Angular itself
  considers that field valid. Despite every individual field passing its
  own validation with no visible error anywhere, the Submit button's
  `disabled` attribute never clears.
- **Likely shared root cause**: the same broken "selected units" tracking
  that produces the stuck "0 selected" counter is the most likely
  explanation for Submit never enabling too -- if the button's enablement
  logic checks that same broken counter/array (rather than the mat-select's
  real value) for "at least one unit selected," a component-level
  selection that never registers in that specific tracked variable would
  explain both symptoms with one bug, not two.
- **Impact**: If this reproduces for real users the way it does for this
  automated (but otherwise standard Playwright fill/type/click)
  interaction, **it may not be possible to raise a support ticket at all**
  through this form -- a serious functional failure of a core, explicitly
  "Critical priority" feature per the design doc's own priority model
  (§17: state-changing operations). Recommend the product team verify
  manually with a real mouse/keyboard session; if confirmed there too,
  this blocks every downstream submission-dependent test case
  (MISC-105/106/109/110/112/113/114) and, more importantly, blocks real
  users from getting support.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 36. [Low] Raise Support Ticket's Comment field ignores any programmatic value change -- only real keystrokes register
- **Test**: `Pages/base_page.py::type_into()` (workaround) is used by all
  Comment-field tests in
  `Tests/functional/test_misc_raise_ticket_functional.py` (MISC-090/091/
  092/093/094/095/096/097/099/100/103/104 and `fill_valid_ticket()`).
- **Symptom**: The Comment textarea in the Raise Support Ticket dialog
  never registers a value set via a standard programmatic `value` +
  `input`-event write (confirmed live with Playwright's `fill()`): the
  textarea's own value stays empty immediately after the call, its
  Angular-managed class list stays `ng-untouched ng-pristine ng-invalid`
  (i.e. Angular's form control never even observes an attempt), and the
  "X/200" counter stays at "0/200". The field is not disabled or
  readonly. Simulating genuine keystrokes (Playwright's
  `press_sequentially`, i.e. real `keydown`/`keypress`/`keyup` per
  character) works correctly and updates the value, the counter, and
  Angular's dirty/touched state as expected.
- **Likely root cause**: the field (or a directive on it, e.g. the
  character counter) appears to update its bound value from a keyboard
  event handler (`keyup`/`keydown`) rather than the standard `input` or
  `(ngModelChange)`/reactive-forms `valueChanges` binding, so any
  non-keystroke value assignment -- programmatic writes, and by the same
  mechanism likely also **paste** (right-click/context-menu paste,
  browser autofill/form-fill extensions, voice-to-text, and some mobile
  keyboards' predictive/swipe input, none of which dispatch a full
  per-character `keydown`/`keyup` sequence) -- would silently fail to
  register, leaving the field looking empty/untouched even though the OS
  clipboard paste "succeeded" visually for a moment.
- **Impact**: Low in isolation (typing normally works fine), but worth a
  real fix: a real user who pastes a longer description (e.g. copying an
  error message or VIN) into this field, or whose browser/OS autofills
  it, may find their input silently doesn't register -- confusing,
  and easy to miss since there's no error, the field just doesn't fill.
  Recommend binding the counter/control to the standard `input` event
  (or Angular's `(ngModelChange)`/reactive `valueChanges`) instead of a
  keyboard-event handler.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 under the literal repro steps, with a nuance worth carrying into the Jira ticket: this looks like a load/binding timing race on dialog-open rather than an absolute rejection of all programmatic writes -- adding a short settle delay before fill() made it succeed consistently in a follow-up check. press_sequentially remains the only consistently reliable input path either way.
### 37. [CRITICAL] Change Password: "Verify" always rejects the correct current password -- the feature is completely unusable
- **Test**: to be added as a regression pin in Phase 6
  (`Tests/functional/test_misc_change_password_functional.py`).
- **Symptom**: On the Change Password page (`/profile/change-password`),
  Stage 1 ("Verify your identity") asks for the account's current
  password before unlocking Stage 2 (New Password / Confirm New
  Password, both genuinely `disabled` in the DOM until Stage 1 passes).
  Entering the account's real, correct, currently-working password and
  clicking Verify **always** returns a toast: "Unable to verify
  password. Please try again." -- Stage 2 stays disabled. Confirmed on
  two independent accounts:
  1. The main test account (`tarun_01`) -- entered the exact password
     used to log in successfully moments earlier (both via `fill()` and
     via real keystrokes, with `input_value()` checked to genuinely match
     before clicking Verify).
  2. A brand-new sub-user, created live via the Administrator module's
     Create User wizard with a fresh password, that immediately logged in
     successfully with that same password in a brand-new browser context
     -- then had that identical password rejected by Verify on this page.
- **Ruled out**: this is not a Playwright-interaction-method artifact
  (unlike Bug #36's textarea) -- confirmed with real keystrokes and a
  verified `input_value()` match immediately before submitting, on an
  account whose password was set seconds earlier by this same test.
- **Impact**: Change Password is explicitly a Critical-priority module
  per the design doc, and as far as this suite can exercise it, **no
  user can change their password through this UI at all** -- Stage 1
  never passes for anyone, so Stage 2 (where the actual new password
  would be entered) is permanently unreachable. This blocks MISC-121
  through MISC-145 entirely (every case that depends on Stage 2 being
  enabled). Recommend the product team verify the current-password
  verification endpoint/logic directly -- this looks like a
  server-side bug (wrong hash comparison, wrong field mapping, or a
  broken endpoint) rather than anything client-side, since the exact
  authenticating password is rejected.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 38. [High] Help Center's main search always returns "0 found" -- breaks the primary search box and every Quick Link, Popular Section, and Common Issue shortcut
- **Test**: to be added as a regression pin in Phase 9
  (`Tests/functional/test_misc_help_center_functional.py`).
- **Symptom**: The Help Center's main search ("Search articles, guides
  and FAQs..." at the top of the page) never returns a real result --
  confirmed by searching for `"device"`, a term guaranteed to match: it's
  the literal name of a real category ("Device") that itself contains one
  real, independently-browsable article ("L-400 Overview", confirmed by
  clicking that category directly in the sidebar). Even this trivially-
  matching search returns "0 found / No results found / Try another
  keyword."
  This same broken search is what backs every one of the page's labeled
  shortcuts -- clicking any Quick Link (Device Setup, Sensor
  Configuration, Reports, Alerts, Video Telematics, Live Tracking),
  Popular Section (Live Tracking & Map, Device & Protocol Help, Sensors &
  Parameters, Reports & Analytics), or Common Issue (Vehicle not showing
  live location, Report data is missing, Alert is not triggering, Sensor
  value looks incorrect) does not open any real content -- it silently
  triggers the same broken search and lands on the identical "0 found"
  dead end, confirmed for one representative item from each of the three
  groups.
- **Ruled out / isolates the bug**: the sidebar's own separate "Search
  contents..." mini-filter (which narrows the Categories & Articles list
  itself) works correctly -- searching "sensor" there correctly filters
  the sidebar down to just the Sensor category. This proves the
  underlying article/category data is real and at least one search code
  path functions -- the bug is specific to the main search integration
  (and everything wired to reuse it), not a data or content problem.
- **Impact**: 14 of this section's labeled shortcuts (6 Quick Links + 4
  Popular Sections + 4 Common Issues) and the primary search box itself
  are effectively non-functional -- a user trying to quickly reach help
  content via any of the page's own suggested starting points gets a
  dead "no results" screen instead. Direct category browsing (the
  sidebar's Device/Sensor list) is unaffected and works correctly, so
  the page isn't completely broken, but its main discovery aids are.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 on the core main-search claim; secondary Quick Link/Popular Section/Common Issue checks came back 2/3 clean (1 attempt hit an unrelated infra navigation timeout, not a bug inconsistency).
### 39. [Low] Help Center's category/article navigation doesn't push browser history -- Back leaves the page entirely instead of stepping back within it
- **Test**: `test_misc_203_browser_back_from_article_restores_state`
  (`Tests/functional/test_misc_help_center_functional.py`).
- **Symptom**: Opening a category (e.g. clicking "Device" in the
  sidebar) shows its article list purely as an in-page state change --
  confirmed live the URL stays exactly `/help-center` before and after
  (no query param, hash, or path change). Since no new history entry is
  pushed, clicking the browser's Back button doesn't step back to the
  Help Center landing view as the design doc expects -- it leaves Help
  Center entirely and lands on whatever page was open before Help Center
  was ever navigated to (confirmed live: landed on `/home`, the fleet
  dashboard).
- **Impact**: Low -- a user browsing a category and instinctively hitting
  Back to return to the Help Center landing page instead gets kicked out
  of Help Center altogether, which is surprising but not damaging (no
  data loss, easily recoverable by reopening Help Center). Recommend
  either pushing a real history entry (query param/hash) per in-page
  navigation, or intercepting Back within Help Center to step back
  through its own internal view stack first.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
---

## Video Telematics Module

### 40. [High] Multi-select filters across the module start with every option pre-selected, so clicking one to isolate it actually DESELECTS it instead -- confirmed on Alert Configuration's Vehicle filter AND the Report page's Vehicle and Alert Type filters
- **Test**: `test_vt_040_filter_one_vehicle`
  (`Tests/functional/test_vt_alert_functional.py`); confirmed live via a
  read-only probe to also affect the Report page's Vehicle and Alert
  Type filters (`Tests/functional/test_vt_report_functional.py`),
  same symptom, same root cause -- not a one-off, a shared component
  pattern.
- **Symptom**: The Alert Configuration page's Vehicle filter is a
  multi-select (`<mat-select multiple>`, confirmed live via its own
  `class="mat-mdc-select-multiple"`) that displays "All vehicles" by
  default. Confirmed live via `aria-selected`: in that default state,
  **every real vehicle option is already individually marked
  `aria-selected="true"`** -- "All vehicles" isn't a separate, distinct
  filter state, it's just the display label for "every vehicle
  currently selected." Consequently, clicking a single vehicle (e.g.
  B123456) to isolate the alerts for just that vehicle does the
  opposite of what a user would expect: since it was already selected,
  the click **toggles it OFF** (`aria-selected` flips to `"false"`),
  leaving every *other* vehicle still selected. The filter then shows
  every vehicle's alerts **except** the one just clicked (confirmed
  live: clicking "B123456" left the list showing only "B123459"'s 50
  alerts, zero for B123456) -- filtering to one vehicle requires
  instead deselecting every *other* vehicle individually, which doesn't
  scale and isn't what "click a vehicle to filter to it" implies.
  Confirmed live the same way (all options `aria-selected="true"` by
  default) on the **Report page's Vehicle filter** (both B123456 and
  B123459 pre-selected) and its **Alert Type filter** (all 53 real
  alert-type options pre-selected) -- the identical shared multi-select
  component/pattern, not a coincidence.
- **Impact**: High for a fleet-monitoring tool -- an operator trying to
  isolate one vehicle's (or alert type's) records by clicking it gets a
  filtered view of every *other* option instead, with no error or
  indication that the opposite of the intended filter was applied. With
  a larger fleet/alert catalog this could easily be misread as "vehicle
  X has no data" when the reverse is being shown. Since this recurs
  across at least two independent pages (Alert Configuration list,
  Report), it looks like a shared underlying filter component -- fixing
  it once there would likely resolve every instance. Recommend either
  making a single option click clear all other selections and select
  only that one (the conventional single-filter-click UX), or visually
  distinguishing "all selected" from a real "All"/reset state so the
  toggle behavior is at least discoverable.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 across all 3 tested locations (Alert Configuration's Vehicle filter, Report page's Vehicle filter, Report page's Alert Type filter).
### 41. [Medium] Update Video Alert dialog: Vehicle, Alert Type, Priority, Delivery Channels, and Delivery Mode are all pre-filled correctly but cannot actually be changed -- only Cooldown and Status are genuinely editable
- **Test**: `test_vt_081_082_083_084_085_086_087_edit_alert_full_flow`
  (`Tests/functional/test_vt_alert_create_functional.py`).
- **Symptom**: Confirmed live via a read-only probe across multiple
  real alert configurations (different vehicles and alert types): in
  the "Update Video Alert" edit dialog, the Vehicle selector, Priority
  selector, all three delivery-channel checkboxes (Application/Email/
  WhatsApp), and both delivery-mode radios (Real time/Interval) are all
  disabled (`aria-disabled="true"` on the two mat-selects,
  `is_enabled() == False` on the checkboxes/radios via their Angular
  Material `-disabled` classes). Only the Cooldown Minutes input and
  the Enabled/Disabled Status checkbox remain interactive. The values
  shown for the locked fields are correct (matches the design doc's
  own "Edit Alert" requirement to load with the correct existing
  values), so this isn't a data bug -- it's that five of the seven
  fields the edit form displays are read-only, not editable, despite
  looking like normal, non-greyed form controls at a glance.
- **Impact**: Medium -- the test suite's own test cases (VT-082
  "Change vehicle; save", VT-083 "Change priority; save", VT-084
  "Change Email/WhatsApp", VT-085 "Change Real time/Interval") all
  describe editing these fields as expected, working functionality;
  live behavior contradicts that for all four. If this lock is
  intentional (e.g. vehicle+alert-type+priority forming a fixed
  identity key once created), it should be communicated to the user --
  e.g. by visually disabling/greying those controls distinctly, or by
  a tooltip/note explaining why -- rather than presenting a form that
  looks fully editable but silently rejects interaction on 5 of 7
  fields. If unintentional, it's a functional regression against the
  documented Edit Alert capability.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 42. [Medium] Report page's Notification filter has no "Skipped" option, even though "SKIPPED" is a real, commonly-displayed notification value in the report table
- **Test**: `test_vt_130_131_notification_filter_sent_and_skipped`
  (`Tests/functional/test_vt_report_functional.py`).
- **Symptom**: Confirmed live: the Report page's Notification filter
  dropdown offers exactly four options -- "All Status", "Sent",
  "Pending", "Failed" -- with no "Skipped" option. But the report
  table's own Notification column routinely displays **"SKIPPED"** as
  a real value on real rows (confirmed live: most rows in the default
  89-record report are SKIPPED, only a handful are SENT). So a
  notification state that's common in the actual data has no
  corresponding filter to isolate it.
- **Impact**: Medium -- a user trying to filter the report down to
  "just the alerts that were skipped" (arguably the more actionable
  case, since it likely means a delivery/config problem) has no way to
  do so; "Sent"/"Pending"/"Failed" are all available but the one status
  most rows actually have is not. Either the filter option list is
  missing "Skipped", or the table is displaying "SKIPPED" for what
  should map to one of the existing filter values (e.g. "Failed") --
  either way, filter options and real displayed data are out of sync.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 43. [High] Report page's Export to Excel, Export to CSV, Export to PDF, Print, and Copy are all unimplemented stubs -- none of them produce any output
- **Test**: `test_vt_166_export_report`, `test_vt_167_export_filtered_report`,
  `test_vt_168_export_empty_report` (`Tests/functional/test_vt_report_functional.py`).
- **Symptom**: Confirmed live via console-message and network-request
  monitoring: clicking any of the 5 export-area buttons on the Report
  page ("Export report to Excel", "Export report to CSV", "Export
  report to PDF", "Print report", "Copy report") does exactly one
  thing -- a `console.log(...)` of the label and the current report's
  row data (e.g. `console.log("Export report to Excel", [...50 row
  objects...])`) -- and nothing else. No file download event fires, no
  new tab opens, no network request is made (confirmed: none of the
  five clicks produced any request beyond an unrelated Google Translate
  widget ping), no browser print dialog opens, no clipboard write
  occurs, and no visible feedback (toast/snackbar) is shown to the
  user. Every one of the 5 actions is a leftover developer placeholder,
  not a working feature.
- **Impact**: High -- the entire Export/Print/Copy capability the
  Report page visibly advertises (5 distinct, clearly-labeled buttons)
  does nothing at all when used, with zero indication to the user that
  nothing happened. A user trying to export ADAS/DMS alert history for
  compliance, incident review, or sharing has no way to actually get
  the data out of the report view. This affects every one of the 5
  actions, not just one -- likely all still wired to placeholder
  `console.log` calls from early development rather than real
  export/print/clipboard implementations.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 for all 5 export/print/copy actions.
### 44. [High] Report page's Alert Type filter is sent to the backend correctly but has no effect on the returned results
- **Test**: `test_vt_129_alert_type_specific`, `test_vt_135_generate_filtered_report`
  (`Tests/functional/test_vt_report_functional.py`).
- **Symptom**: Confirmed live via request-payload inspection: selecting
  a single real alert type ("Speeding") in the Alert Type filter and
  clicking Generate Report sends a correctly-formed request --
  `POST .../adas_api.php` with body `{"method":"get_adas_alert_history",
  "page":1,"limit":50,"from":"2026-09-01","to":"2026-09-05",
  "alarm_code":[11]}` -- so the frontend selection state and its
  translation into the API call are both correct (the UI's own
  aria-selected state was independently verified to show only
  "Speeding" selected before Generate was clicked, ruling out a
  frontend selection bug). Despite `alarm_code:[11]` being sent, the
  returned 50 rows are NOT filtered by it -- the first row returned was
  "Main Power Disconnected", an unrelated alert type, and the result
  set size (a full 50-row page) matches the unfiltered/default report's
  own page size, indicating the backend is silently ignoring the
  `alarm_code` filter parameter entirely rather than applying it.
- **Impact**: High -- a user filtering the report to one specific alert
  type (e.g. to review only Speeding events, or only a specific ADAS/
  DMS category relevant to an incident) gets back the full, unfiltered
  report instead, with no indication the filter wasn't applied. This
  directly undermines the Report page's core "narrow down to what you
  need" purpose and could lead to a reviewer missing or misattributing
  events, or wrongly concluding a filtered search "has no matching
  events" only because they can't spot their target among unrelated
  rows.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 45. [CRITICAL] Evidence snapshot and video files are fully downloadable with zero authentication -- no login, session, or token required
- **Test**: `test_vt_197_evidence_url_authorization`
  (`Tests/functional/test_vt_security_functional.py`).
- **Symptom**: Confirmed live: every evidence snapshot image and
  evidence video referenced in the Report page's evidence panel is
  served directly from a separate host (`https://new.trackofy.com:16611/...`)
  via URLs like
  `.../3/5?Type=3&FLENGTH=97240&FOFFSET=95525338&FILELOC=2&FPATH=...&MTYPE=1`
  (snapshot) and
  `.../3/5?DownType=3&FLENGTH=4666923&FOFFSET=0&FILELOC=2&MTYPE=1&FPATH=...`
  (video) -- these query parameters are pure file-location metadata
  (byte offset/length, storage path built from vehicle IMEI + date +
  timestamp), with **no session cookie, auth header, or token of any
  kind** in the URL. Verified by capturing one real snapshot URL and
  one real video URL while logged in, then fetching BOTH directly from
  a completely fresh, cookie-less, never-authenticated browser context:
  both returned `200 OK` with the correct `content-type`
  (`image/jpeg`/`video/mp4`) and the full, correct byte size matching
  their own `FLENGTH` parameter (97,240 bytes for the snapshot,
  4,666,923 bytes for the video) -- i.e. the real file, in full,
  served to a party that never logged in at all.
- **Impact**: CRITICAL. Anyone who obtains one of these URLs -- via a
  shared link, browser history, a proxy/network log, a referrer leak,
  or simply by noticing the predictable structure (sequential/
  guessable byte offsets, a file path built from a real, often-public
  vehicle IMEI and a date) -- can retrieve any driver/vehicle's ADAS/
  DMS evidence video or snapshot without ever authenticating, with no
  rate limiting or authorization check evident from this test alone.
  For a fleet-safety product whose evidence footage can include
  driver-facing DMS camera video (fatigue, distraction, identity),
  this is a serious privacy and safety-data exposure, and defeats the
  entire point of an access-controlled Evidence feature (VT-197's own
  CSV expectation is "Access is denied" for exactly this scenario).
  Recommend the evidence file server require a valid, short-lived,
  per-request signed token or session check before serving any file,
  not just location/offset parameters.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 for both snapshot and video URLs, byte-exact content match against a completely fresh, cookie-less request context each time.
### 46. [Low] Video Telematics' custom-styled combobox controls (vehicle/channel selectors) show no visible focus indicator
- **Test**: `test_vt_visible_focus_indicator`
  (`Tests/functional/test_vt_accessibility_responsive_functional.py`).
- **Symptom**: Confirmed live: focusing the Dashboard's vehicle
  selector (a custom-styled `<mat-select>`, not the browser's native
  control) via keyboard leaves `outline: none` and `box-shadow: none`
  on the focused element, and none of its ancestor wrapper elements
  gain a focus-indicating class either -- there is no visible change
  at all to mark that the control now has keyboard focus.
- **Impact**: Low -- a keyboard-only user tabbing through the Video
  Telematics module's vehicle/channel selectors (Dashboard, Playback,
  Report all use the same styled combobox pattern) has no way to see
  which control is currently focused, making keyboard navigation
  difficult to use reliably (WCAG 2.4.7 Focus Visible). Recommend
  adding a visible focus style (outline or box-shadow) to this shared
  combobox component.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3, plus a supplementary real-keyboard-Tab check that also confirmed no visible focus indicator.
### 47. [Medium] At mobile viewport widths, Video Telematics' navigation drawer auto-opens over the page content, and its own Close button renders outside the viewport
- **Test**: `test_vt_219_dashboard_responsive`, `test_vt_221_playback_responsive`
  (`Tests/functional/test_vt_accessibility_responsive_functional.py`).
- **Symptom**: Confirmed live at a 390x844 mobile viewport: opening any
  Video Telematics sub-page renders the module's own left-nav
  ("MODULES: Dashboard/Alert/Playback/Report") as an open overlay
  drawer by default, pushing/hiding the actual page heading and
  content underneath it (confirmed: the Dashboard's own heading exists
  in the DOM but has a `width: 0` bounding box and `is_visible() ==
  False`). The drawer's own dismiss control (`aria-label="Close
  navigation menu"`) is present but Playwright reports it "outside of
  the viewport" and un-clickable -- so the drawer cannot even be
  dismissed through normal interaction at this width, trapping the
  user on an empty-looking page. This is a different, more severe
  variant of the mobile-navigation issue already logged as Bug #34 in
  the Miscellaneous Pages module (there, the Account menu was simply
  unreachable at mobile width; here, an entire module's main content
  is hidden behind an auto-opened, undismissable drawer).
- **Impact**: Medium -- Video Telematics is effectively unusable at
  mobile viewport widths: every sub-page's real content is hidden
  behind a navigation drawer that opens automatically and can't be
  closed via its own visible-but-unreachable Close button. Recommend
  either not auto-opening the drawer on these routes at narrow
  viewports, or ensuring its Close control is always within the
  viewport bounds.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
---

## Login Page Module

### 48. [Minor] Login heading has a typo -- "Sign in to you account" instead of "your account"
- **Test**: `test_login_00X_heading_text` (`Tests/functional/test_login_functional.py`).
- **Symptom**: Confirmed live: the login page's main heading reads
  "Sign in to you account" -- missing the "r" in "your".
- **Impact**: Minor -- purely cosmetic, doesn't affect functionality,
  but it's the first thing every user sees on the primary entry point
  of the application. Confirmed with the user as a real, intended
  finding (not a rendering/probe artifact) and logged as Minor
  priority per their direction.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 49. [Medium] Password visibility toggle is unreachable via Tab (tabindex="-1")
- **Test**: `test_login_keyboard_password_toggle_reachable` (`Tests/functional/test_login_functional.py`).
- **Symptom**: Confirmed live: the eye icon that toggles password
  visibility has a real, correct `aria-label="Toggle password
  visibility"` and works correctly when clicked (masks/unmasks without
  changing the value) -- but its underlying `<button>` carries
  `tabindex="-1"`, which explicitly removes it from the natural Tab
  order. A keyboard-only user tabbing through Username -> Password ->
  ... never reaches it at all.
- **Impact**: Medium -- directly contradicts the design doc's own
  stated requirement ("Control is keyboard accessible") and its
  Keyboard & Accessibility checklist, which explicitly lists the
  password visibility control as one of the controls that must be
  Tab-reachable. A keyboard-only user who mistypes their password has
  no way to reveal and check it without a mouse. Recommend removing
  the `tabindex="-1"` (or setting `tabindex="0"`) so it participates
  in the normal tab order between Password and Terms & Privacy.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 50. [High] Every failed login shows a raw technical error instead of a safe, user-friendly message -- leaks the internal API hostname and endpoint
- **Test**: `test_login_007_invalid_username_safe_error`,
  `test_login_009_incorrect_password_safe_error`
  (`Tests/functional/test_login_functional.py`).
- **Symptom**: Confirmed live across every failed-login scenario tried
  (nonexistent username, and a real username with the wrong password):
  the error toast shown to the user is the literal, unmodified HTTP
  client error --
  `"Http failure response for https://beta2.trackofy.com/trackofy_api_new/token.php: 401 Unauthorized"`
  -- not a safe message like "Invalid username or password". The same
  raw-error pattern was also seen when replaying a tampered auth token
  (a separate live check, not itself a CSV scenario), suggesting this
  is the app's general-purpose failure handler rather than a one-off.
  On the positive side: nonexistent-username and wrong-password-for-a-
  real-account produce the *identical* message, so this specific
  defect does not by itself enable username enumeration.
- **Impact**: High -- this is the default, everyday experience for
  the single most common negative path (a mistyped password), and it
  directly violates the design doc's own "Authentication Error
  Handling" (§7: "appropriate error is displayed") and "Error Message
  Security" (§21: must not reveal "internal API details") sections.
  Every user who mistypes a password sees raw HTTP client internals
  naming the actual backend host and endpoint
  (`beta2.trackofy.com/trackofy_api_new/token.php`), which is both a
  poor user experience and unnecessary information disclosure about
  the backend architecture. Recommend catching this failure class and
  rendering a generic, friendly "Invalid username or password" message
  instead of surfacing the raw HTTP client error text.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 51. [Low] Auth token is stored in localStorage, not an HttpOnly cookie -- no defense-in-depth against token theft via XSS
- **Test**: `test_login_token_not_httponly_cookie` (`Tests/functional/test_login_security_functional.py`).
- **Symptom**: Confirmed live: after login, the JWT session token
  lives in `localStorage['token']` (alongside a separate
  `adas_token`, `device_id`, `role`, `username`, etc.) -- the only
  cookie present is Google's own `g_state`. No auth-relevant cookie
  exists at all, so none of it can carry `HttpOnly`/`Secure`/
  `SameSite` attributes -- those are cookie-only protections and
  simply don't apply to localStorage. Any JavaScript that runs on the
  page (including via a future XSS bug) can read the token directly
  with `localStorage.getItem('token')` and exfiltrate it.
- **Impact**: Low, given this session's own XSS testing (LOGIN-069,
  and the equivalent tests across every other module tested this
  session) found no actual script-injection vulnerability to exploit
  this through today. But it is a real, standing architectural gap
  against the design doc's own §20 requirement ("Authentication
  cookies/tokens have appropriate security attributes") -- a
  defense-in-depth layer that would contain a future XSS bug (by
  keeping the token unreadable to injected scripts) is entirely
  absent. Recommend moving the session token to an HttpOnly, Secure,
  SameSite cookie set by the server, rather than JS-readable
  localStorage, if the login flow can be adapted to a cookie-based
  session model.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
---

## Admin Panel Module

### 52. [Minor] Inconsistent nav-item labeling -- "UnassignDevice" has no space, every other nav item does
- **Test**: `Pages/admin_dashboard_page.py::NAV_PARENT` (documented inline),
  exercised via `test_admin_003_nav_reaches_all_in_scope_pages`
  (`Tests/Admin Panel/functional/test_admin_auth_functional.py`).
- **Symptom**: Confirmed live: every Device-submenu nav link uses a
  spaced, title-cased label ("Add Device", "Manage Device", "Bulk Upload
  Device", "Migrate Device", "Device Distribution", "Device Expiry",
  "Search Device") except one -- its real accessible link text is
  literally `"UnassignDevice"`, no space.
- **Impact**: Cosmetic/consistency only, but visible to every admin user
  in the same menu as its correctly-formatted siblings.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 53. [Minor] Create Plan form: "Currency*" label's `for` attribute points to the same id as "BillType*", not its own field
- **Test**: `Pages/admin_plan_page.py` (documented inline).
- **Symptom**: Confirmed live via DOM inspection of `/admin/plan/create-plan`:
  both the "BillType*" and "Currency*" `<label>` elements have
  `for="billType"` -- there is no independent, correctly-associated label
  for the Currency field. A screen-reader user tabbing to the Currency
  control would hear "BillType" announced, not "Currency".
- **Impact**: Accessibility gap; automation had to fall back to
  positional (`get_by_role("combobox").nth(1)`) selection for Currency
  since `get_by_label("Currency")` cannot reach it.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
### 54. [Minor] Manage User/Manage Dealer row-action icons and Tax List's Edit/Delete icons have no accessible name at all
- **Test**: `Pages/admin_user_page.py::edit_icon/delete_icon/view_subusers_icon`,
  `Pages/admin_tax_page.py::edit_icon/delete_icon` (documented inline).
- **Symptom**: Confirmed live: Manage User/Manage Dealer's row-level
  Update/Delete/View-Subusers actions are bare `<i>` icons using
  PrimeNG's `ptooltip` attribute for their hover text, with no
  `aria-label` or `role="button"`. Tax List's Edit/Delete icons are even
  less accessible -- plain `<i class="pi pi-pencil/pi-trash">` with
  neither `ptooltip` nor any ARIA attribute. None of these are reachable
  via `get_by_role`, and a screen-reader/keyboard-only admin user has no
  way to know what these icon-only controls do.
- **Impact**: Real accessibility gap across the panel's most-used CRUD
  actions (every user, dealer, and tax record's Edit/Delete goes through
  one of these unlabeled icons).

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 on Manage Dealer and Tax; Manage User came back 2/3 clean (1 attempt hit a table-not-yet-loaded timing miss, not a contradicting result).
### 55. Intermittent 500 from `get-tax-master` under rapid successive admin-panel API calls
- **Test**: `test_admin_tax_002_create_and_delete_tax_profile`
  (`Tests/Admin Panel/functional/test_admin_tax_functional.py`), caught
  at fixture teardown by the global `_track_server_errors` check.
- **Symptom**: A full serial run of the Tax test file (9 tests, several
  doing real create/delete cycles against `/admin/tax` in quick
  succession) produced one real `POST .../api/get-tax-master -> 500
  {"message": "Server Error"}`. Re-running the same test in isolation
  passed cleanly with no error. This is the same shape as the already-
  documented Unit Module Bug #5 (intermittent 500 from `unit_general/get`
  under concurrent/rapid load) -- backend contention triggered by rapid
  successive real API calls against the same account, not a defect in
  the test itself.
- **Impact**: Low/informational on its own (didn't corrupt data or block
  the create/delete flow itself), but worth the same "known, load-
  sensitive backend" note as Bug #5 -- avoid running Admin Panel Tax
  tests concurrently with other heavy suites against the same account.

- **Reverification (2026-09-07, live 3x pass):** NOT REPRODUCED this pass (0/9 rapid create/delete cycles across 3 runs) -- consistent with the bug's own documented intermittent nature; kept as documented, not withdrawn, pending a repro under genuine concurrent load.
### 56. [High] Manage User's search box does not filter at all
- **Test**: `Pages/admin_user_page.py::search` (documented inline);
  discovered while trying to locate leftover test data.
- **Symptom**: Confirmed live on `/admin/user/manage-user`: entering any
  query (a known-present first name, a full email, mixed case) and
  pressing Enter always re-renders the exact same full, unfiltered
  15,900+-row list ("Showing 1 to 10 of 15942 users" regardless of the
  query). Contrast with `/admin/tax`'s search box, which filters
  correctly. The only way to find a specific record is to page through
  the entire list manually (or know it sorts to the last page for
  newest-first lookups).
- **Impact**: High -- this is the primary way an admin would locate any
  one of 15,942 real customers, and it is completely non-functional. No
  workaround exists inside the UI itself.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3, with a working Tax-search control (correctly narrowed 8->1 row) confirming the search mechanism itself functions and Manage User's is specifically the broken one.
### 57. [Medium] Create User: colliding Mobile number is only rejected server-side after the entire 3-step wizard is submitted
- **Test**: `Pages/admin_user_page.py::create_dummy_user` (documented
  inline); discovered live -- a randomly-picked test mobile number
  happened to collide with a real existing customer's number.
- **Symptom**: Confirmed live: filling Mobile with an already-registered
  number passes client-side validation on every step (Personal
  Information, Billing Information, Service) and only fails after the
  final Submit, with the message "Mobile number already exists" -- all
  entered data across all 3 steps is lost, with no indication of which
  field caused the failure.
- **Impact**: A real, uncommon-but-plausible admin workflow failure --
  filling a long multi-step form only to lose everything on a late,
  unexplained rejection. Recommend either an inline uniqueness check on
  the Mobile field itself (Personal Information step) or preserving
  entered data on submit failure so the admin can just fix the one field.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 2/3 clean (1 attempt inconclusive due to unrelated wizard-flakiness already documented elsewhere in this module, not a contradicting outcome) -- the colliding mobile number was accepted through all 3 wizard steps and rejected only at final submit, losing all entered data.
### 58. [High] Create Dealer: a non-numeric value in a PIN-Code field triggers a raw SQL Server error that leaks the database host, port, and database name
- **Test**: `Pages/admin_user_page.py::fill_billing_info_minimal`
  (documented inline); discovered live while filling Create Dealer's
  Billing step with generic placeholder text.
- **Symptom**: Confirmed live via network trace: `POST
  https://beta2.trackofy.com/api/create-dealer` returned `200` with body
  `{"status":false,"message":"Dealer creation failed","error":"SQLSTATE
  [22018]: [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
  Conversion failed when converting the nvarchar value 'AutoQA123' to
  data type int. (Connection: sqlsrv_second, Host: 192.168.23.131, Port:
  15433, Database: atl_testing, ...)"}` when a PIN-Code-shaped field
  received an alphanumeric value instead of digits.
- **Impact**: High -- this is a genuine information-disclosure bug, not
  just a rough error message: the raw error string exposes the internal
  database server's IP address, port, and database name to the client.
  Combined with the 200 status code (a real error masquerading as a
  successful response), any consumer checking only HTTP status would
  also miss the failure entirely. Recommend catching this class of DB
  exception server-side and returning a generic validation message with
  no connection details, plus real client-side type validation on
  PIN-Code-shaped fields (numeric-only) so this path isn't reachable from
  the UI at all.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- identical raw SQLSTATE error leaking the DB host/port/database name and the full INSERT statement every time.
### 59. Manage Dealer has no Delete action -- dealers created via this panel are permanent
- **Test**: `test_admin_dealer_003_no_delete_action_present`
  (`Tests/Admin Panel/functional/test_admin_dealer_functional.py`).
- **Symptom**: Confirmed live on every dealer row inspected, both a
  freshly created dummy dealer and multiple pre-existing real ones: the
  row-action column has only an "Update dealer" (`pi-user-edit`) icon and
  a disabled "White Labeling Details" (`pi-tag`) icon -- no delete icon,
  no `ptooltip="Delete dealer"` element anywhere, unlike Manage User
  which has a real (request-based) delete flow for the same page shape.
- **Impact**: Not necessarily a defect (may be an intentional business
  rule -- dealers likely have downstream sub-users/devices that make
  deletion unsafe), but it is a real, confirmed asymmetry with Manage
  User worth the product team's awareness, and it directly shaped this
  suite's design: only status-toggle (disable), never delete, is used
  for dealer cleanup.

- **Reverification (2026-09-07, live 3x pass):** Re-confirmed live alongside this pass's Bug 58/63 dealer-creation attempts -- every dealer row inspected still has no delete action.
### 60. Device assignment is genuinely eventually-consistent -- a device can be missing from its new owner's device list well after the "assigned successfully" confirmation
- **Test**: `test_admin_device_008_full_assign_and_unassign_cycle`
  (`Tests/Admin Panel/functional/test_admin_device_functional.py`,
  currently `@pytest.mark.skip` -- see the skip reason for full detail).
- **Symptom**: Confirmed live, reproduced across 3 separate automated
  runs: after Add Device returns `{"status":true,"message":"Device
  assigned successfully"}` and the owner's own row-level device COUNT
  correctly increments, the SAME owner's "View Devices" dialog can still
  omit the newly assigned device for an extended period -- reproduced
  even after a 3.5s post-submit wait plus 6 retry attempts (each a full
  page reload, ~2s apart, so at least ~15-20s of real wall-clock time).
  Manually, with longer, less structured pauses between checks, the
  device did eventually appear and unassign correctly every time.
- **Impact**: The row-count and the per-owner device-list appear to be
  backed by different data paths with materially different consistency
  windows. An admin who assigns a device and immediately opens "View
  Devices" to confirm it could see a device list that doesn't yet
  include what they just assigned, which could read as "did the
  assignment even work" even though it did. Recommend the product team
  confirm the real propagation delay between these two read paths, and
  consider making the device-list dialog reflect the same immediately-
  consistent count the summary row already shows.

- **Reverification (2026-09-07, live 3x pass):** COULD NOT VERIFY this pass -- no never-assigned device IMEI was found on the first page of Unassign Device's inventory to drive a real Add Device flow through. The original finding (reproduced across 3 runs in a prior session) stands undisturbed; simply not independently re-run here.
### 61. [WITHDRAWN -- not reproducible] Create Plan Submit-enablement gating
- **Original claim**: Submit only enables once EVERY Payment Type row AND
  EVERY Menu List item is checked, with no indication this is required.
- **Reverification (this pass)**: Live-retested at the user's request.
  Filling Plan Name/BillType/Selling Amount and checking only ONE
  Payment Type row and ONE Menu List item now reliably enables Submit --
  confirmed across 3 clean back-to-back trials (`disabled` attribute
  absent, `is_enabled()` True, computed CSS `opacity:1`/`cursor:pointer`
  every time). **The original claim does not reproduce and is
  withdrawn.**
- **Real root cause of the original false positive**: this page's
  Submit button, on click, opens a **second confirmation dialog**
  ("Please check your selling amount before submitting. Do you want to
  continue?", Cancel/Submit) with its own, separately-scoped "Submit"
  button. The original investigation's automation clicked only the
  first (form-level) Submit and never the confirmation dialog's own
  Submit, then observed no `POST /api/create-plan` call and concluded
  the button didn't work / required more fields -- when in fact the
  first click was working correctly (it opens the confirmation step)
  and the miss was a missing second click, not a validation gate. With
  both clicks performed, `POST /api/create-plan` returns
  `200 {"status":true,"message":"Plan created successfully","plan_id":
  <real id>}` -- a genuinely successful creation -- for BOTH a minimal
  (1 row + 1 item) selection and a full (all rows + all items)
  selection alike, confirming the earlier "must check everything"
  theory was never the real mechanism.
- **New, confirmed-live finding from this reverification: Manage Plan
  has no Edit/Delete action of any kind.** The two real plans created
  while confirming the above (`ReverifyConfirm_...`, `ReverifyBody_...`,
  real `plan_id`s returned by the API) could not be removed -- their
  table rows have no action-icon column at all (confirmed via direct
  DOM inspection: only S.No/Plan Name/Payments/Menu/Description
  columns), and the row's own "Menu" tag opens only a read-only cost
  breakdown, not an edit/delete surface. This is the same shape as Bug
  #59 (Manage Dealer has no Delete action) extended to Manage Plan --
  **both real plans created during this reverification remain
  permanently in the account's real plan list with no way to remove
  them through the UI.**
- **Impact**: Re-scoped from Medium (a confusing-but-recoverable
  validation gate) to a documentation correction plus a new, separate
  finding: (1) the original Bug #61 should be removed from any tracker
  it was filed in, since it doesn't reproduce and its root cause was a
  test-automation gap, not a product defect; (2) Manage Plan's complete
  absence of a delete/edit-removal action is a real, standalone gap
  (see the CSV export's replacement row) worth the product team's
  awareness on its own, independent of the withdrawn claim.
- **Still true, unaffected by this correction**: checking a Payment Type
  row's checkbox correctly auto-derives its Amount from Selling Amount
  (e.g. 99 -> Monthly 99, Quarterly 297, Half Yearly 594, Yearly 1188).

- **Reverification (2026-09-07, live 3x pass):** [WITHDRAWN, unaffected by this pass] One confirmation pass performed per scope, not the full 3x (already conclusively root-caused and corrected earlier this session -- see the full withdrawal writeup below): minimal 1-row/1-item selection still enables Submit and opens the real confirmation dialog as documented.
### 62. [Low] Configuration's Manage Brand/Manage Model/Documentation and the top-level Menu page silently redirect to Dashboard
- **Test**: `test_admin_smoke_004_configuration_and_menu_pages_redirect_to_dashboard`
  (`Tests/Admin Panel/functional/test_admin_smoke_functional.py`).
- **Symptom**: Confirmed live: `/admin/configuration/manage-brand`,
  `/admin/configuration/manage-model`, `/admin/configuration/documentation`,
  and `/admin/menu` all silently redirect to `/admin/dashboard` when
  navigated to directly -- no error message, no "not implemented" notice,
  no permission-denied indication. All 4 have real, clickable links in
  the top nav menubar (confirmed via the full `a[href*="/admin/"]`
  extraction done during initial exploration) that lead nowhere useful.
- **Impact**: Low -- these are secondary configuration/reference pages,
  not core to the panel's stated purpose, but a real admin clicking any
  of these 4 nav items gets silently bounced to the dashboard with no
  explanation, which reads as the link being broken rather than the
  feature being intentionally unavailable.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 across all 4 URLs.
### 63. [CRITICAL] Users and Dealers created via the Admin Panel cannot log in, and the standalone Forgot Password flow doesn't recognize them either -- a separate, real activation-email flow exists and is broken (see Bugs #64 and #65)
- **Test**: none automated yet; a regression test should be added to
  `Tests/Admin Panel/` once #64/#65 are fixed and the real activation
  flow can be driven end-to-end with a real inbox.
- **Symptom**: Confirmed live, for both a Create User and a Create
  Dealer record created through the Admin Panel with a fake
  (`@example.com`) email:
  1. Logging in with the record's mobile number as username fails with
     `401 Unauthorized` (no password is ever set anywhere in the Create
     User/Dealer wizard -- there is no password field at any step).
  2. The main login page's Forgot Password flow does not recognize
     these accounts by phone or email ("Please enter valid mobile/
     email"), while the identical flow correctly proceeds to "OTP sent"
     for a real, pre-existing end user's mobile number (Madhup Dwisedi,
     8527736688) used as a control -- confirming the mechanism itself
     works and specifically doesn't recognize Admin-Panel-created
     records.
  3. **Correction, confirmed by the user with a real inbox**: a
     genuinely separate credentials/activation EMAIL *is* sent after
     Create User, containing its own link to a dedicated verification-
     code form (choice of email or phone) -- this is not the same flow
     as the main login page's Forgot Password. That dedicated form is
     where the account activation actually happens, and it's the one
     that's broken -- see Bugs #64 and #65 for the real root cause.
- **Impact**: CRITICAL. Regardless of which flow is the "correct" one,
  the end result stands: as of this investigation, there is no working
  path for a user or dealer created through the Admin Panel to ever
  gain access to their account, which is the core purpose of the "admin
  can... create a new user, assign them plan" workflow this module
  exists for.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED (User side) -- re-confirmed live with a fresh Admin-Panel-created user: login fails 401, Forgot Password doesn't recognize the record, and a control test against a real pre-existing user succeeds normally, isolating the gap to Admin-Panel-created records specifically. Dealer side inconclusive this pass -- both dealer-creation attempts failed before completion (verified via the full Manage Dealer list afterward), so the dealer-side login/forgot-password claim was not independently re-run.
### 64. [CRITICAL] Account-activation "verification code" request fails with a raw SQL fragment leaking through a broken JSON response -- Email channel
- **Test**: none automated yet (found via the user's manual test with a
  real inbox after Create User); needs a dedicated Admin Panel ->
  real-activation-email E2E test once this is fixed.
- **Symptom**: Confirmed live: after creating a user via the Admin
  Panel, a real credentials/activation email is sent to the user's real
  email address, containing a link to a verification-code request page
  (choice of "email" or "phone"). Choosing **email** and submitting the
  account's own real email address (e.g. `systemsatlanta0@gmail.com`)
  returns the client-side error `Error: Unexpected token 'S',
  "SELECT ema"... is not valid JSON`.
- **Root cause (from the error text itself)**: the backend endpoint
  behind "Send Code" is returning a raw, unexecuted SQL query fragment
  (beginning `SELECT ema...`, almost certainly `SELECT email FROM
  ...`) as its HTTP response body instead of a JSON payload -- the
  frontend's `response.json()` call then fails to parse it, surfacing
  the raw SQL text directly in the UI's error toast.
- **Impact**: CRITICAL, two compounding problems: (1) this is a genuine
  information-disclosure bug -- raw SQL query text belongs nowhere
  near a client response; (2) functionally, this completely blocks the
  email-based path of account activation for every newly created user,
  with no visible workaround.

- **Reverification (2026-09-07, live 3x pass):** COULD NOT INDEPENDENTLY VERIFY this pass -- no IMAP/inbox credentials exist in this environment to receive the real activation email and reach the verification-code page. The original finding (confirmed live by the user with a real inbox) stands undisturbed.
### 65. [CRITICAL] Account-activation "verification code" request fails with a raw SQL fragment leaking through a broken JSON response -- Phone channel
- **Test**: none automated yet; same follow-up as Bug #64.
- **Symptom**: Confirmed live: the same verification-code request page
  from Bug #64, choosing **phone** instead and submitting a phone
  number (e.g. `2112112212`), returns the client-side error `Error:
  Unexpected token 'S', "SELECT mob"... is not valid JSON`.
- **Root cause (from the error text itself)**: identical shape to Bug
  #64 but for the phone/mobile lookup query -- the backend returns a
  raw, unexecuted SQL fragment beginning `SELECT mob...` (almost
  certainly `SELECT mobile FROM ...`) instead of a JSON response.
- **Impact**: CRITICAL, same two compounding problems as Bug #64
  (information disclosure + complete functional block), this time for
  the phone-based activation path -- meaning BOTH channels offered on
  this page are broken, leaving no working way to complete account
  activation via this flow at all.

- **Reverification (2026-09-07, live 3x pass):** COULD NOT INDEPENDENTLY VERIFY this pass -- same reason as Bug 64 (no inbox access).
### 66. [CRITICAL] Create Dealer sends NO credentials/confirmation email at all -- not even the broken one Create User sends
- **Test**: none automated yet; needs a real-inbox E2E test alongside
  #64/#65's fix verification once available.
- **Symptom**: Confirmed by the user with a real inbox: creating a
  dealer through the Admin Panel's Create Dealer wizard sends no email
  whatsoever -- no credentials email, no confirmation, no activation
  link of any kind. This is a step below Create User's own broken flow
  (Bug #63/#64/#65): User at least attempts to email real activation
  steps to the new record (even though both the email and phone
  verification-code endpoints behind that link are themselves broken);
  Dealer doesn't attempt anything at all.
- **Impact**: CRITICAL, and compounds Bug #63's core finding: combined
  with Manage Dealer having no Delete action (Bug #59) and no working
  password-reset recognition (Bug #63), a dealer created through this
  panel is not only unable to log in today, there is no
  automatically-triggered channel through which they'd ever even be
  told the account exists or given a path to obtain access. Recommend
  the product team confirm whether dealer onboarding is meant to route
  through a manual/offline process (e.g. a human sending credentials)
  or whether an equivalent automated email is simply missing and should
  mirror whatever Create User's flow does once that flow itself is
  fixed.

**Note on likely cause of this cluster going unnoticed** (#59, #63-#66):
per the user's own assessment, this pattern -- broken automated
activation across both channels for User, no attempt at all for Dealer
-- is consistent with new accounts actually being activated by the dev
team directly through the database rather than through either of these
UI-driven flows. That would explain why none of this has surfaced
before: nobody exercising real account creation day-to-day is actually
walking through the flows this cluster of bugs breaks. Worth surfacing
to the team not just as "these 4 endpoints are broken" but as "the
self-service activation path may not be exercised in practice at all,"
since that's a process/practice risk on its own, independent of any one
endpoint's fix.

- **Reverification (2026-09-07, live 3x pass):** COULD NOT INDEPENDENTLY VERIFY this pass -- same reason as Bug 64 (no inbox access to confirm the absence of an email).
### 67. [HIGH, Login Page Module] No rate limiting or account lockout on the login endpoint -- 25 consecutive failed attempts all behaved identically
- **Module**: this is a Login Page Module finding, not Admin Panel-
  specific (the shared `/trackofy_api_new/token.php` endpoint behind
  the one login form used by every account type tested this session) --
  numbered in sequence here rather than back in the Login Page Module
  section (#48-#51) to avoid renumbering the whole document.
- **Test**: none automated yet; a dedicated
  `test_login_XXX_no_rate_limit_on_repeated_failed_attempts` (or
  similar honestly-named "confirmed absent" regression pin) should be
  added to `Tests/functional/test_login_security_functional.py`.
- **Symptom**: Confirmed live: 25 consecutive login attempts against a
  single non-existent username (`bruteforce_probe_nonexistent_user`,
  chosen specifically so no real account's lockout state could be
  affected by this test) with a different wrong password each time
  produced 25 IDENTICAL results -- `401 {"message":"Login failed"}`,
  response time consistently ~1.28-1.36s with no growth (no
  exponential backoff), no CAPTCHA element ever appeared in the DOM, no
  "too many attempts"/"try again later"/"locked" message ever appeared,
  and no `429 Too Many Requests` status was ever returned. All 25
  requests were sent back-to-back (only a 0.3s polite delay between
  attempts on the test's side, not enforced by the server).
- **Impact**: HIGH. This is a real, unmitigated brute-force/credential-
  stuffing exposure -- an attacker can attempt unlimited password
  guesses per second against any known username (or enumerate valid
  usernames the same way) with no server-side friction at all.
  Recommend adding IP-based and/or account-based rate limiting
  (progressive backoff and/or temporary lockout after N failures) and,
  ideally, CAPTCHA after a handful of failed attempts.
- **Also confirmed against a REAL account** (`tarun_01`, the main test
  account): 25 consecutive wrong-password attempts produced the exact
  same result -- no lockout, no CAPTCHA, no message, no 429, no growth
  in response time. Immediately afterward, logging in with the correct
  password succeeded normally ("Login successful", redirected to
  `/home`), confirming the account itself was undamaged by this test.
  This rules out account-specific lockout as well as IP-level
  throttling -- there is no rate-limiting or lockout mechanism of any
  kind on this endpoint, for a nonexistent username or a real one.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- 3 separate runs of 10 consecutive failed attempts each (30 total) against a nonexistent username: identical 401s, no growth in response time, no CAPTCHA, no 429, no lockout message in any run.
### 68. [HIGH] Manage User's "rows per page" offers an unbounded "show all 15,959 rows" option that freezes and eventually crashes the browser tab
- **Test**: none automated yet (a real crash makes this unsafe to run as
  a normal CI-gated regression test as-is; if automated, it should run
  isolated, with a hard timeout, and assert the page recovers/doesn't
  hang rather than actually completing the render).
- **Symptom**: Confirmed live: the Rows-per-page control on
  `/admin/user/manage-user` offers `10 / 25 / 50 / 100 / 500 / 15959` --
  the last option is not a fixed "large page size," it's literally the
  account's live total row count (15,959 at time of testing), i.e. an
  unbounded "render the entire table" option that grows as the account
  grows. Selecting it does not paginate at all -- it attempts to render
  every row into the DOM in one table. Measured live: the render is
  genuinely progressive but rapidly decelerating, and the page's own
  main-thread responsiveness degrades in lockstep, not just the visible
  row count:
  | elapsed | rows rendered | main-thread response time for a trivial `1+1` JS eval |
  |---|---|---|
  | 10s | 700 | 4ms |
  | 20s | 1,500 | 35ms |
  | 31s | 2,100 | 1,748ms |
  | 44s | 2,600 | 3,724ms |
  | 60s | 3,000 | 5,803ms |
  | 81s | 3,400 | 7,170ms |
  This is a classic unvirtualized-list collapse: every additional row
  makes the next reflow/layout pass more expensive, so cost grows much
  faster than linearly with row count. **Confirmed by the user with a
  real browser session**: continuing past this point (this automated
  probe was stopped for safety around 3,400 rows/81s), the real page
  reached roughly 8,000 rendered rows before the tab stopped responding
  entirely and crashed.
- **Impact**: HIGH. Any admin who selects the "show all" pagination
  option on a table of this size (15,959 rows today, and growing) will
  reliably freeze their browser tab and, per direct user confirmation,
  can crash it outright before it ever finishes rendering -- there is no
  way to select this option safely at the account's current size. The
  fix suggested directly by the user, and the one this report
  recommends: cap the maximum selectable rows-per-page at a bounded
  value (e.g. 100, already one of the existing options) and remove the
  "render the entire live table" option entirely, or if a bulk/full-
  export use case genuinely needs all rows, serve that through a
  dedicated export/download flow (server-side, streamed to a file)
  rather than a client-side "page size" that scales with total table
  size.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- the same unvirtualized-list collapse pattern in all 3 fresh-context attempts (main-thread eval latency growing from roughly 10-120ms to multi-second, up to 10-second, stalls within 90s). No hard crash within the 90s headless safety cap (a real browser's actual crash point, per prior direct user confirmation, is later, around ~8,000 rendered rows), but every attempt reached severe, user-visible freezing well before that cap.

### 69. [Medium] Manage Plan's search box returns unrelated plans that don't match the query
- **Test**: none automated yet -- should be added to `Tests/Admin Panel/functional/test_admin_plan_functional.py` alongside `test_admin_plan_007_manage_plan_search_box_present` (which had previously only smoke-tested the search box's presence with "no confirmed evidence either way" on filtering correctness -- this closes that gap).
- **Symptom**: Confirmed live on `/admin/plan/manage-plan`, reproduced across 3 independent fresh sessions: searching for a real, exact plan name ("Platinum", read directly from row 1 of the unfiltered list) does narrow the result count (10 -> 5 rows in every attempt) -- so the search isn't completely inert like Bug #56 (Manage User's search) -- but the returned 5 rows every time were `["Platinum", "Gold", "Platinum_bms", "Platinum 4", "Platinum (4)"]`. Four of the five genuinely contain "Platinum"; **"Gold" does not match the query in any way** (no substring, prefix, or fuzzy relation) and still appears in the filtered results, identically in all 3 attempts.
- **Impact**: Medium -- an admin searching Manage Plan's ~35 real plans for a specific one gets a result set that looks correctly filtered (row count drops, matching plans are present) but silently includes at least one unrelated plan mixed in, with no visual distinction marking it as a non-match. This is more subtle and easier to miss than a search that visibly does nothing (like Bug #56) -- a user could reasonably not notice the one wrong row in a short filtered list, or worse, act on it believing it matched their search term.
- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- identical filtered result set, including the same unrelated "Gold" row, in all 3 independent fresh-session attempts.
---

## Test Suite Notes (not application bugs, for context)

- **Correction**: General Permission (Step 3) and Unit Permission (Step 4)
  category/item checkboxes were earlier believed to start CHECKED by
  default (an opt-out model). Re-verified live with an isolated probe (zero
  prior clicks anywhere on the step) and confirmed they actually start
  UNCHECKED (an opt-in model). The original false positive came from a bug
  in `AdministratorPage.expand_permission_category()`: the category name
  text is the *label of the category's own checkbox*, so clicking it (the
  method's old "expand" implementation) was actually toggling that checkbox
  on -- which, per Material's parent/child checkbox pattern, cascades to
  check its children too, making a freshly-touched category look
  checked-by-default. Fixed to click the accordion's chevron
  (`.mat-expansion-indicator`) instead, which genuinely expands without
  touching any checkbox. All dependent tests (Phase 3 back-chain, Phase 5
  General Permission, Phase 6 Unit Permission) and `create_user()`'s
  docstring have been corrected to match the real (unchecked-by-default)
  behavior.
- Unit module tests run against a single shared "first unit" in the account.
  Running them with `pytest-xdist` (`-n > 1`) causes multiple workers to
  operate on that same unit concurrently, which produces both UI-timing
  false failures and *triggers* real backend contention issues (see #5
  above). **Run the Unit suite serially** (no `-n` flag) for trustworthy
  results; the intermittent-500 backend issue itself is real and worth
  the product team's attention independent of how the tests are run.
- A global check (`conftest.py::_track_server_errors`) now fails any test
  where the application API returns a 5xx during that test, with the
  response logged — this is what caught findings #4 and #5 above. Tests
  that intentionally mock a 5xx to test error handling are marked
  `@pytest.mark.allow_server_error` and are exempt from this check.
- A full serial run of the entire Reports module (`pytest Tests/ -m reports`,
  ~270 tests) took just over 2 hours and hit a sustained ~30-60 minute window
  of basic page-load/navigation timeouts (`Page.goto` and `wait_for` timing
  out reaching `/reports/standard` itself, not any report-specific logic) —
  ~35 of ~40 failures in that run trace back to this one window and did not
  reproduce when the same tests were re-run individually right afterward.
  This looks like transient staging-environment/session degradation under
  a very long continuous automated session, not a product defect — but it
  means a single marathon run is not a reliable signal on its own; a failure
  is only worth chasing once it's confirmed to reproduce in a short, isolated
  re-run (as was done for findings #18 and #20 above, and as this note itself
  is scoped to exclude).
- Several tests that use the `network_monitor` fixture and assert on captured
  successful backend calls (`test_reports_generation_smoke.py`,
  `test_reports_crud.py`, `test_reports_custom_schedule.py`,
  `test_reports_functionality.py`) failed with "0 successful calls captured"
  even for reports confirmed to have loaded correctly and quickly (e.g.
  Fleet Summary loading in ~2s). This looks like a timing/race issue in the
  `network_monitor` fixture's own capture window (the fixture's `start()`
  vs. the click firing the request) rather than a product bug — the
  underlying report generation itself worked. Not fixed in this pass since
  it's pre-existing test infrastructure outside the Reports-module page
  object/dataset work; worth a follow-up if `network_monitor`-based
  assertions are relied on going forward.
