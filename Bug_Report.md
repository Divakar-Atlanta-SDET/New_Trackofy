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

## Unit Module — Custom Sensors

### 2. No validation on Configuration Expression (TC-120)
- **Test**: `Tests/negative/test_unit_sensors_negative.py::test_tc120_invalid_configuration_expression`
- **Symptom**: Entering a malformed Configuration Expression (e.g. missing
  operand/garbled syntax) does not disable **Save Config** and shows no
  inline validation error. The form accepts and submits invalid expressions.
- **Impact**: A user can save a sensor with a broken calculation expression
  with no warning; downstream sensor readings for that config will be wrong
  or fail silently.

### 3. No maxlength or validation on Sensor Configuration Name (TC-106)
- **Test**: `Tests/edgecase/test_unit_sensors_edgecase.py::test_tc106_exceed_sensor_name_length`
- **Symptom**: The Sensor Configuration Name field has no `maxlength`
  attribute and accepts an unbounded string (tested with 300 characters) with
  no validation error.
- **Impact**: Unbounded input can be submitted to the backend; combined with
  the JS-side table rendering that silently truncates long names with `...`,
  this also produces confusing/unreadable rows in the Custom Sensors list.

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

### 14. Driver create form: Address field is silently required
- **Test**: found while building `Tests/positive/test_settings_driver_positive.py`
- **Symptom**: The **Create Driver** button stays disabled until the Address
  field is filled, but Address carries no visible required-field indicator
  (no asterisk), unlike Name/Mobile/Email/DOB/DL fields which do.
- **Impact**: A user filling only the visibly-marked required fields will
  be stuck with a disabled Create button and no explanation why.

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
