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
- **Reverification (2026-09-16, production):** Still ❌ **STILL BROKEN** -- `test_tc120_invalid_configuration_expression` reproduced again: Save Config remained enabled and no validation error appeared for `"not a valid expression @@@"`.
### 3. No maxlength or validation on Sensor Configuration Name (TC-106)
- **Test**: `Tests/edgecase/test_unit_sensors_edgecase.py::test_tc106_exceed_sensor_name_length`
- **Symptom**: The Sensor Configuration Name field has no `maxlength`
  attribute and accepts an unbounded string (tested with 300 characters) with
  no validation error.
- **Impact**: Unbounded input can be submitted to the backend; combined with
  the JS-side table rendering that silently truncates long names with `...`,
  this also produces confusing/unreadable rows in the Custom Sensors list.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3 -- no maxlength attribute, full 300-char value accepted with no validation error, 3 fresh sessions.
- **Reverification (2026-09-16, production):** Still ❌ **STILL BROKEN**, unchanged -- `test_tc106_exceed_sensor_name_length` reproduced again: no `maxlength` attribute, full 300-char value accepted, no validation error shown. Regression-pin test left unmodified (application defect, not a script issue).
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
- **Reverification (2026-09-16, production):** ❌ **STILL PRESENT**, and the predicted "day > 12" failure mode confirmed directly: typing today's date (day 16) in DD/MM format for Playback's From/To Date gets parsed as month=16 (invalid), which correctly shows `aria-invalid="true"` and "This field is required." errors, blocking Load Playback entirely -- exactly the "parse/validation failure instead" case anticipated above, not a new symptom. `test_trk_play_013_todays_date` was itself tripping over this via the wrong input format; fixed to type MM/DD/YYYY (matching `test_tracking_playback_positive.py`'s established `_fmt_input`/`_fmt_display` workaround) so it now correctly lands on today's date instead of an invalid one.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED** on both Location Control and Vehicle Group. Creating a second Location (or Vehicle Group) with a name identical to an existing one is now rejected client-side with an "already exist"-style validation message, and the entity count stays at 1 -- no duplicate row is created. `test_set_085_duplicate_location_name_not_prevented` and `test_set_196_duplicate_vehicle_group_name_not_prevented` flipped to assert the fixed behavior and now pass.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** Picking a vehicle from the Assign Units dialog's "Select Vehicles" multi-select now correctly updates the "X selected" counter, and the Assign Units button enables and submits the assignment successfully. `test_set_086_assign_unit_button_stays_disabled` flipped to assert the fixed behavior and now passes.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** A fully filled-out POI Alert form (unit, POI, notification channel) now submits successfully -- the dialog closes with no "Missing required fields" rejection, and the new alert appears in the list. `test_poi_alert_create_valid_configuration` (renamed from the rejection-expecting version) flipped to assert the fixed behavior and now passes.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED** for both BMS Alert and Vehicle Odometer Alert. Creating a configuration for a vehicle now genuinely persists and shows up in the list after a full page reload -- confirmed via the reloaded table containing the configured vehicle's name. One caveat worth noting for anyone re-testing this: the app enforces one configuration per vehicle per alert type, so re-running this check against a vehicle that *already* has a configuration updates its existing row instead of adding a new one -- that's a business rule, not a regression of this bug, and one earlier check in this pass briefly mistook it for one before re-running against a vehicle with no prior configuration confirmed the real (fixed) behavior. `test_alert_created_and_listed_after_reload` (parametrized over both alert types) flipped to assert the fixed behavior and now passes.
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
- **Reverification (2026-09-13, live, confirmed via automated suite):** ❌ **STILL BROKEN.** Both `test_set_156_create_valid_route` (Save) and the Custom Route tab's Cancel path still land on `/home` after the action, requiring the test's own `_recover_to_route_list()` workaround (re-entering Settings via the nav bar) to get back to Route Management. Unchanged from the 2026-09-07 finding.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** The Email field on the Create Driver form now carries a hard `maxlength="30"` attribute matching the DB column's real limit, and Angular's own validator marks the field invalid (visible "Invalid email" error, Create Driver button stays disabled) the instant the value would exceed it -- confirmed the browser truncates keystrokes at exactly 30 characters as they're typed, so an over-length email can never reach the submit handler through the form. Also tried bypassing the client-side `maxlength` directly via a DOM `value` set + dispatched `input` event (to check whether this is enforced anywhere besides the `maxlength` attribute) -- Angular's own reactive-form validator re-ran on the injected value and re-disabled the Create Driver button anyway, so there is no way to get an over-length email submitted through the actual UI attack surface. No raw SQL error or HTTP 500 could be triggered in 3 independent attempts. Backend-level defense-in-depth (does `POST /api/add-driver` itself reject an over-length value if called directly, bypassing the UI entirely) was not separately tested -- out of scope for this pass, which targets the form flow a real user goes through.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** Leaving Route Name blank now keeps the Save Route button disabled (confirmed for missing name, missing origin, and missing destination alike -- the form validates via a disabled button rather than submit-then-reject now) -- no more silent "My Route" default-and-save. `test_set_157_route_name_not_actually_enforced` (renamed) flipped to assert the fixed behavior and now passes.
### 14. Driver create form: Address field is silently required
- **Test**: found while building `Tests/positive/test_settings_driver_positive.py`
- **Symptom**: The **Create Driver** button stays disabled until the Address
  field is filled, but Address carries no visible required-field indicator
  (no asterisk), unlike Name/Mobile/Email/DOB/DL fields which do.
- **Impact**: A user filling only the visibly-marked required fields will
  be stuck with a disabled Create button and no explanation why.

- **Reverification (2026-09-07, live 3x pass):** REPRODUCED 3/3.
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** The Address field now displays a required-field asterisk ("Address *") matching the other mandatory fields on the form. As a side effect of this UI change, the visible label text is no longer programmatically associated with the input (no `<label for>`/`aria-labelledby`), so its accessible name falls back to its placeholder ("Enter complete address") -- `Pages/driver_page.py`'s `address_input` locator was updated to match on the placeholder instead of `name="Address"`, which had started matching zero elements.
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
- **Reverification (2026-09-13, live, 3x pass, screenshot-confirmed):** ✅ **FIXED.** Typing an address into the field now shows the entered text immediately and correctly in the visible viewport -- confirmed via a screenshot of the field after typing, no scroll/visibility gap.

### 75. [High] BMS Alert list rows have no Edit or Delete action buttons at all -- a BMS Alert configuration, once created, can never be managed or removed through the UI
- **Found**: 2026-09-13, while regression-testing the fix for Bug #11 (BMS/Odometer Alert list not refreshing)
- **Test**: `Tests/negative/test_settings_alerts_negative.py::test_alert_created_and_listed_after_reload[BMS Alert]`
  (surfaced as a cleanup failure -- `delete_alert()` timed out finding a Delete
  button on a real BMS Alert row -- then confirmed directly)
- **Symptom**: Every other alert type checked -- AC, Ignition, Main Power,
  Panic, Speed, Idle, Temperature, POI, and Vehicle Odometer Alert -- renders
  at least one action button (Edit and/or Delete) per row. BMS Alert is the
  sole exception: inspecting the row HTML directly across all 10 existing
  BMS Alert rows (and the first 5 rows specifically checked for button
  count) shows **zero `<button>` elements of any kind** in every row, in 3
  independent live checks. The row itself renders correctly (Unit, Mode,
  Alert Type, Battery, Email, WhatsApp No, Created Date columns all populate
  with real data) -- only the action-button column is missing.
- **Impact**: A user (or this automated suite) can create a BMS Alert
  configuration, but can never edit or delete it again through the UI --
  every BMS Alert this account creates is permanent. This is a more severe,
  distinct issue from the now-fixed Bug #11 (which was about the list not
  refreshing to show a new row at all): here the row does appear correctly,
  it simply cannot be acted on afterward. The Settings-module regression
  test that creates one of these on every suite run had to add a
  best-effort-only cleanup guard (skip cleanup entirely for BMS Alert,
  since there's no button to click) to avoid asserting on the cleanup step
  itself, which would otherwise fail for reasons unrelated to what the test
  is actually checking.
- **Reverification (2026-09-13, live, 3x pass):** REPRODUCED 3/3 -- identical zero-button result across all three independent checks (two full-module surveys across every other alert type for contrast, plus the original cleanup-step timeout).

### 76. [High] A fixed-position "FEEDBACK" widget can intercept clicks on real row controls beneath it, app-wide
- **Found**: 2026-09-13, while cleaning up test data left in Location Control
- **Test**: surfaced as a real click failure during Settings test-data cleanup
  (a `Locator.click` on a Location's Delete button timed out with Playwright
  reporting `<div class="fixed top-[40vh] right-0 ...">` intercepting pointer
  events), then confirmed directly and surveyed across modules.
- **Symptom**: A "FEEDBACK" button (`<div class="fixed top-[40vh] right-0
  z-[90] ...">`, rotated -90deg, fixed at 40% viewport height on the right
  edge) is rendered on top of the normal page content on at least Dashboard,
  Unit, and Settings (confirmed absent on Home, Tracking, and Reports in the
  same pass -- inconsistent across modules, not universal). Because its
  position is fixed relative to the viewport, not the page content, any real
  interactive control that happens to scroll to around that screen height --
  which row that is depends entirely on how much content/how many rows
  render above it -- becomes genuinely unclickable through a normal click; a
  real Delete button in Location Control was blocked this way in live
  testing (`force=True` did not help; only hiding the widget via a
  JS override let the click land). Same class of defect as Bug #74 (CAN
  module's map overlay intercepting clicks), but this widget is a shared,
  app-level component rather than one module's own overlay, and its
  interception is data/scroll-position-dependent rather than constant.
- **Impact**: Any user whose data happens to place a real action button
  (Edit/Delete/Assign/etc., not specific to Location Control -- any row
  control rendering near 40% viewport height on an affected module) behind
  this widget cannot click it at all through normal interaction, with no
  visual indication anything is blocking the click.
- **Reverification (2026-09-13, live, 3x pass):** REPRODUCED 3/3 -- the direct click-interception (1x, during real cleanup work) plus 2 independent module surveys confirming the widget's presence, fixed position, and visibility on Dashboard/Unit/Settings.

## Administrator Module (continued)

### 77. [WITHDRAWN -- test automation bug, not a product bug] Driver reassignment/unassign
- **Status: RETRACTED 2026-09-13.** Not a real bug -- a bug in this
  session's own test automation helper produced a false positive.
- **What happened**: Two rounds of live diagnostics both concluded
  something was broken in the driver Assign/Unassign dialog -- first that
  a direct vehicle swap via "Update Assignment" was rejected as "already
  assigned," then, after correctly being told the real flow is
  unassign-then-reassign, that Unassign's own success toast was lying
  about clearing the assignment. The user directly verified Unassign
  manually and reported it works correctly, and flagged the diagnostic
  script as the likely problem rather than the app.
- **Root cause, confirmed**: `Pages/driver_page.py`'s `unassign_vehicle()`
  helper clicked the "Unassign current vehicle" icon (which -- confirmed
  live via network capture -- immediately fires `POST /api/unassign-driver`
  and genuinely commits, 200 OK, independent of anything else) and then
  **also** clicked "Update Assignment" right after. At that point the
  Select Vehicle dropdown still visually showed the just-unassigned
  vehicle (a stale UI artifact, not yet re-rendered) -- clicking
  "Update Assignment" against that stale, still-populated dropdown
  silently re-submitted and re-assigned the same vehicle, undoing the
  unassignment the icon click had already correctly performed. This
  extra click is what produced every downstream symptom: the
  driver ending up still assigned to the "unassigned" vehicle, and every
  later reassignment attempt correctly being rejected as already-assigned
  (because the driver genuinely still was).
- **Confirmed via a corrected script** using the real intended flow
  (click the Unassign icon, close the dialog via Cancel -- no further
  confirm click) end-to-end: assign driver to Vehicle A (succeeds) ->
  unassign (icon click only, "Unit Unassigned Successfully", driver's row
  genuinely shows no vehicle after reload) -> assign to a different
  Vehicle B (button correctly reads "Assign Vehicle," not "Update
  Assignment," confirming the clean unassigned state; succeeds; row shows
  Vehicle B after reload). The full assign/unassign/reassign cycle works
  correctly end-to-end.
- **Fix applied**: `Pages/driver_page.py`'s `unassign_vehicle()` no longer
  clicks "Update Assignment" after the unassign icon -- it closes the
  dialog via Cancel instead, matching the real, correct flow.
  `test_set_053_change_driver_assigned_unit` rewritten to exercise and
  assert the genuine, correct assign -> unassign -> reassign cycle.

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
### 70. Distance Chart, Stoppage Summary and Engine Hour report three mutually contradictory total-distance figures for the identical vehicle and date range
- **Test**: Manual data-validation pass over the Standard Reports catalog (staging,
  vehicle `GCBL10536MHG14AG04459`, date range 03/01/2026-03/10/2026)
- **Symptom**: Generating Distance Chart, Stoppage Summary, and Engine Hour back-to-back for
  the exact same vehicle and date range returns three different answers to "how far did this
  vehicle travel":
  - Distance Chart: **Total(km) = 180.55** (daily breakdown 0 + 65.28 + 80.37 + 34.9 = 180.55,
    internally consistent with itself)
  - Stoppage Summary: **Distance = 1,114.32 km** -- roughly 6x Distance Chart's figure
  - Engine Hour: **Total Distance = 0**, with Status shown as "Inactive" for the same vehicle
    and range
- **Impact**: A report is only useful if its numbers are trustworthy; here three different
  Standard reports give three incompatible answers for the same query, so at least two of
  the three (and possibly all three) are computing distance incorrectly. A user cross-checking
  fleet mileage across reports (a normal use case) gets contradictory numbers with no
  indication which, if any, is correct.
- **Reverification (2026-09-10, live 3x pass):** REPRODUCED 3/3 -- identical 180.55 / 1,114.32 / 0 figures across 3 independent fresh sessions.
- **Reverification #2 (2026-09-10, corrected date range, live):** The original 03/01/2026-03/10/2026 range predates this account's real telemetry window (confirmed separately: any report using that range returns a raw SQL error for a missing monthly partition, Bug #17), so it was re-tested with a genuinely in-range last-2-months window. Two sub-findings:
  - A **short, real-data range (15 days, 2026-08-25 to 2026-09-09)** shows Distance Chart (281.68 km) and Stoppage Summary/Engine Hour (282.13 km, identical to each other) agreeing within 0.16% -- effectively consistent, not a meaningful mismatch.
  - A **longer, real-data range (~2 months, 2026-07-11 to 2026-09-09)** reproduces a large mismatch again, **3/3 identical across independent fresh sessions**: Distance Chart = **900.62 km** vs Stoppage Summary/Engine Hour = **2634.16 km** (both identical to each other) -- a ~2.9x disagreement.
  - **Revised conclusion: CONFIRMED, still a real bug** -- but the discrepancy is range-length-dependent, not a fixed ratio, and does not manifest (or is negligible) over short windows. Distance Chart's per-day-bucketed total and Stoppage Summary/Engine Hour's trip-based total diverge increasingly as the requested date range grows, suggesting Distance Chart under-counts (missing/dropped days beyond a certain range) or Stoppage Summary/Engine Hour over-counts (e.g. double-counting overlapping trip segments) for longer queries. Root cause not isolated further; flagging the range-dependence for whoever investigates the calculation.
### 71. Stoppage Summary shows a non-zero Distance with 0m Total Running and 0m Total Idle -- an internally impossible combination
- **Test**: Manual data-validation pass over the Standard Reports catalog (staging,
  vehicle `GCBL10536MHG14AG04459`, date range 03/01/2026-03/10/2026)
- **Symptom**: The Stoppage Summary row for the vehicle shows **Total Running = 0m**,
  **Total Idle = 0m**, and **Distance = 1,114.32 km** in the same row. A vehicle cannot cover
  over a thousand kilometers while its own report records zero minutes of running time for
  the period -- the three columns are self-contradictory regardless of what the "correct"
  distance value should be (see also Bug #70).
- **Impact**: The report's own columns don't agree with each other, which is a stronger signal
  of a broken duration/distance calculation than a bad number alone -- the underlying
  aggregation is not deriving Distance from the same trip/running data it uses for
  Total Running/Total Idle.
- **Reverification (2026-09-10, live 3x pass):** REPRODUCED 3/3 -- identical 0m / 0m / 1,114.32 km row across 3 independent fresh sessions.
- **Reverification #2 (2026-09-10, corrected date range, live 3x pass):** NOT REPRODUCED with a genuinely in-range date (2026-07-11 to 2026-09-09, avoiding the missing-partition range from Bug #17) -- Total Running showed a real, non-zero value (**90h**, identical across 3 independent fresh sessions) alongside the (still mismatched, per Bug #70) Distance figure. **Withdrawn as a standalone finding**: the original 0m-Total-Running symptom was an artifact of querying a date range with no real underlying telemetry (see Bug #17), not a genuine calculation defect independent of Bug #70. The Distance-figure disagreement itself remains open under Bug #70.
### 72. Driver Performance returns all-zero metrics for every driver, including one assigned to a vehicle with confirmed real activity in the same range
- **Test**: Manual data-validation pass over the Standard Reports catalog (staging,
  date range 03/01/2026-03/10/2026, drivers: syam, Test Driver Alpha/Bravo/Charlie)
- **Symptom**: Generating Driver Performance for the full driver list returns 4 rows where
  every numeric column -- Max Speed, Avg Speed, Total Distance, Harsh Breaking, Harsh
  Acceleration, Fuel Consumption, Mileage, No Of Trips -- is exactly `0` for all 4 drivers,
  and Rating is `NA` for all 4. Driver "syam" is associated with vehicle
  `GCBL10536MHG14AG04459`, which independently shows real distance (180.55 km, per Bug #70)
  and real speed data (up to 41 km/h, per the Maxspeed Chart report) for this exact date
  range -- so driver-level metrics should not be zero across the board.
- **Impact**: Driver Performance is non-functional as a data source -- it cannot currently be
  used to evaluate or compare any driver's behaviour, since it returns identical, uninformative
  all-zero rows regardless of a driver's actual underlying vehicle activity.
- **Reverification (2026-09-10, live 3x pass):** REPRODUCED 3/3 -- identical all-zero rows for all 4 drivers across 3 independent fresh sessions.
- **Reverification #2 (2026-09-10, corrected date range, live):** NOT REPRODUCED with a genuinely in-range date (2026-07-11 to 2026-09-09, avoiding the missing-partition range from Bug #17). Driver "syam" (assigned to the same test vehicle) now returns real, differentiated data: Max Speed 40.74, Avg Speed 19.09, Total Distance 2664.38, Rating "Good", 9 trips -- not all-zero. **Withdrawn as a standalone finding**: the original all-zero symptom was an artifact of querying a date range with no real underlying telemetry (see Bug #17), not a genuine defect in Driver Performance's calculation. Note in passing (not separately filed, needs its own investigation before treating as a bug): one other driver in the same result set ("Test Driver Alpha") showed Avg Speed 178.2 km/h against a Total Distance of only 1.17 km for the period -- an implausible speed/distance combination worth a closer look in a future pass.

### 95. [Medium] Distance Chart, Cumulative Distance and Maxspeed Chart show validation error banners the instant the Start Date field is clicked -- before any date is picked and before Generate report is ever pressed

- **Test**: none automated yet; found by the user's own manual testing, independently reproduced live on **production** (v6.trackofy.com) across 3 separate reports.
- **Symptom**: Confirmed live, screenshot evidence both before and after: opening the Distance Chart standard report form shows a clean, error-free state (Start Date and End Date both default to the same day, "Yesterday" quick-filter active, Min/Max Distance blank, Select Vehicles blank). Simply **clicking into the Start Date field to open its calendar picker** -- not selecting a different date, not touching Min/Max Distance or Select Vehicles, and not clicking "Generate report" -- immediately causes the same red banner ("Start Date and End Date cannot be the same when time selection is not available.") to appear **three separate times** in the form (above Select Vehicles, below Select Vehicles, and again near the bottom above the Generate button). The underlying condition it's complaining about (Start Date == End Date) was already true in the clean "before" state and did not change from clicking the field -- only the *visibility* of the error changed, meaning the form is (likely) calling something equivalent to Angular's `markAllAsTouched()` on any field interaction instead of only on submit/blur of the specific control.
- **Blast radius (confirmed via a live pass across every Standard report with an End Date field)**: reproduces identically on **Cumulative Distance** and **Maxspeed Chart** (4 banners each, same trigger). Does **not** reproduce on Work Hour, Stoppage Summary, Running Summary, or Engine Hour, despite all four also having a Start Date + End Date pair -- narrowing this to whichever shared sub-component Distance Chart/Cumulative Distance/Maxspeed Chart use for their date range (likely a distance/speed-report-specific date-range control, not the generic one).
- **Secondary observation**: the affected reports' own *default* state (same-day range via the "Yesterday" quick-filter) already violates the rule the error message describes -- meaning the form ships pre-invalidated by default, and merely touching any field is enough to surface that latent invalid state. Even setting aside the premature-display bug, the "same day requires time selection" rule itself deserves a second look: it's unclear why a same-day range should require an explicit time selection at all for these reports.
- **Impact**: Medium -- doesn't block report generation (the banners disappear once a valid, non-same-day range is actually selected, and Generate still works), but it's a broken, unprofessional first impression: a user who has done nothing wrong yet sees the form yelling three validation errors at them for simply looking at the date picker, on 3 of the app's most commonly used reports.
- **Reproduction (2026-09-15, live, production)**: REPRODUCED 3/3 reports (Distance Chart, Cumulative Distance, Maxspeed Chart), confirmed via before/after screenshots showing the clean-vs-errored states.

### 97. [High] AS-219, reconfirmed on PRODUCTION: a scheduled report ("Daily" delivery) never arrives at the configured email address at all -- checked both Inbox and Spam

- **Test**: `Tests/functional/test_reports_schedule_functional.py::test_rep_sch_030b_scheduled_report_actually_delivered_to_email`.
- **Symptom**: Created a genuine "Fleet Summary" schedule (Daily, fire time ~2 minutes in the future, Schedule Till = today) targeting a real, checkable inbox. Polled that real inbox via IMAP for 6 minutes, checking **both the Inbox and the Spam folder** (the Spam check was added specifically to rule out "delivered but filtered" as a false-negative cause) -- no email containing "Fleet Summary" arrived in either folder. This is the same AS-219 symptom already documented in `retest_bug_report.md` from staging testing, now confirmed to reproduce on **production** (`v6.trackofy.com`) as well, not just staging.
- **Impact**: High -- the Schedule feature's entire purpose is unattended, recurring report delivery; if the email never arrives (and isn't even landing in Spam), the feature is silently non-functional end to end for anyone relying on it, on the real production environment customers use.
- **Caveat**: only same-day "Daily" delivery was tested (fire time ~2 minutes after creation). If the scheduler is actually designed to only start firing the day *after* creation, that would produce this exact symptom without being a bug -- worth one follow-up confirming next-day delivery before treating this as fully conclusive. The original AS-219 report itself describes the same "configured a schedule, never arrived" symptom without a same-day/next-day distinction either.
- **Cleanup**: the test's own `finally` block deletes the schedule it created regardless of outcome -- confirmed this ran (no orphaned schedule should remain from this specific test run, but see the final report's data-cleanup section for a full sweep).
- **Reproduction (2026-09-15, live, production)**: REPRODUCED -- 3rd confirmed occurrence of this exact symptom overall (previously confirmed on staging per `retest_bug_report.md`), 1st confirmed occurrence specifically on production.
- **Reproduction (2026-09-16, live, staging, full run -- 8/9 other schedule tests passed cleanly)**: REPRODUCED again -- no "Fleet Summary" email arrived in Inbox or Spam within 6 minutes of the scheduled 10:35 delivery time. 4th confirmed occurrence overall, 2nd on staging specifically. Schedule cleanup in the test's `finally` block ran normally.
- **Reproduction (2026-09-16, live, staging, isolated rerun)**: REPRODUCED a 5th time -- independent run, new schedule fired for 11:56, still no "Fleet Summary" email in Inbox or Spam after the full 6-minute poll. Consistent, repeatable, not a one-off timing fluke.

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
- **Reverification (2026-09-13, live, 4x pass):** ✅ **FIXED.** The Step 1 -> Step 2 "Next Step" transition no longer fires a `POST /api/save_subuser` (or any other save-shaped) API call at all -- confirmed via full network-response logging across the whole wizard flow. Closing the wizard via the "X" icon, tested both right after Step 1->2 and again after progressing all the way through Step 4 (menu group, permissions, unit selection) without ever clicking Submit, leaves the user count unchanged and the attempted username absent from User Management on a fresh reload -- confirmed 4x total (1 automated pytest run via the existing regression pin, 3 independent manual diagnostic runs, one of which exercised the full Step-1-through-4 path). The save now appears to genuinely wait for final Submit, matching the app's own stated design intent. `test_adm_053_close_wizard_without_submit_still_creates_user` needs flipping to assert no user is created (not done automatically here since it's a meaningful behavior-assertion change worth a deliberate pass, not a locator fix).
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED (the stacking defect).** The "Add Group" button now disables itself immediately on click and stays disabled until its dialog opens -- confirmed live a second/third rapid click during that window is simply blocked (Playwright's own actionability check reports the button `disabled` and cannot click it), so multiple dialogs can no longer stack. Also confirmed exactly one `GET /api/v1/user/menus`-shaped request fires per open, not one per click. The disabled state during the fetch also doubles as a (minimal) busy indicator, partially addressing the original "looks broken, no feedback" complaint too. `test_adm_065b_rapid_add_group_clicks_stack_duplicate_dialogs` needs flipping to assert the button blocks rapid clicks / exactly one dialog opens (not done automatically here since it's a meaningful behavior-assertion change).
- **Reverification (2026-09-16, production, via regression-pin test failure):** ⚠️ **POSSIBLE REGRESSION -- the Sep 13 fix no longer holds.** The flipped regression pin `test_adm_065b_rapid_add_group_clicks_no_longer_stack_dialogs` (which asserts the *fixed* behavior -- button disables on click) failed: `btn.is_enabled()` returned `True` immediately after clicking, i.e. the button is clickable again, same as before the Sep 13 fix. This was caught by an automated regression run against production, not a fresh manual dive -- worth a direct manual reverification (click Add Group, immediately check whether a second click opens a second dialog) before treating this as confirmed, but if it holds, the stacking-dialog defect is back.
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
- **Reverification (2026-09-13, live):** ✅ **FIXED (the UX gap itself).** Step 4's unit selector is no longer an unfiltered picker over the entire fleet -- confirmed live it now shows only the vehicle(s) selected in Step 1, with explicit UI copy ("Only vehicles selected in Step 1 are available", "1 in scope") confirming the scoping. With only `HP12G9691` selected in Step 1, Step 4's dropdown now offers no other vehicle at all -- the exact scenario this bug described (30+ unscoped vehicles listed) no longer reproduces, and the original regression test's setup (select a second, out-of-scope vehicle in Step 4) is no longer constructible, since the option simply isn't offered anymore. `test_authz_bug27_unit_permission_without_scope_is_inert` needs rewriting to assert the new scoped-dropdown behavior directly (not attempt the now-impossible unscoped-selection setup).

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
- **Reverification (2026-09-13, live) -- INCONCLUSIVE, NOT confirmed fixed:** direct `page.goto()` to both `/administrator` and `/settings/driver` as a freshly created, correctly-scoped-away sub-user now redirects to `/home` instead of rendering the page shell. On its own this looks like a fix -- but this app has a separate, independently confirmed, app-wide defect (NEW-1, `retest_bug_report.md`) where a raw `goto()`/reload to **any** module's direct URL bounces to `/home` for **every** account, including the fully-authorized owner account, regardless of permissions. That means this exact redirect is fully explained by NEW-1 alone and does **not** distinguish "real route-level authorization was added" from "nobody, authorized or not, can reach any module by direct URL anymore for an unrelated reason." Confirming this one way or the other would require reaching the route through a mechanism NEW-1 doesn't intercept (e.g. a client-side route change via the History API rather than a full navigation) -- not attempted this pass. Leaving this bug's status as unresolved/unverifiable under current conditions rather than claiming it fixed; `test_authz_bug29_direct_url_bypasses_menu_access` still fails (in the sense of no longer matching its original "loads real page" assertion) but for a confounded reason, not necessarily the fix it was written to catch -- left as-is rather than incorrectly flipped to "fixed."
- **Reverification (2026-09-16, production, via regression-pin test failure):** Same result as Sep 13, same unresolved confound -- `test_authz_bug29_direct_url_bypasses_menu_access` failed again with a fresh sub-user redirected to `/home` on direct nav to `/administrator`. Still haven't done the disambiguating work (a client-side route change instead of a full navigation) to tell "real authz fix" apart from "NEW-1 redirects everyone regardless of permission" -- status unchanged, still open/unverifiable, not claiming fixed.
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
- **Reverification (2026-09-13, live):** ✅ **FIXED.** Confirmed both surfaces now consistently label the category "User" -- the Create User wizard's Step 3, and an existing user's Permissions dialog's General Permission tab both show "User", not "Global".
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
- **Reverification (2026-09-13, live):** ❌ **STILL BROKEN**, unchanged -- "test", "admin", and "demo" all rejected again with the identical "User already exist" [sic] error toast, tested through the full wizard (Step 1 -> Submit) this time rather than just Step 1 -> 2, to account for Bug #25's fix moving the real save to final Submit.
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
- **Reverification (2026-09-13, live):** ✅ **FIXED.** Both fields now have a working, genuinely functional show/hide toggle -- "Show password" and "Show confirm password" (distinct, per-field aria-labels), confirmed live that clicking one flips its own field from `type="password"` to `type="text"` without affecting the other field. `test_adm_bug33_no_password_visibility_toggle_in_wizard` needs flipping to assert the toggles exist and work (not done automatically here since it's a meaningful behavior-assertion change).

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
- **Reverification (2026-09-13, live):** ✅ **FIXED.** At a 390x844 mobile viewport, My Profile, Support, Change Password, and Sign Out are all now genuinely reachable and functional -- confirmed live clicking each correctly navigates to its real page (`/profile`, `/profile/support`, `/profile/change-password`) or, for Sign Out, opens the confirmation. The mobile layout implements these as real `<a>` anchor links (not `role="button"` elements like the desktop layout), which is why `get_by_role("button", ...)` locators found nothing at this viewport -- not a product bug, just a locator that needed to account for the mobile markup using link semantics instead of button semantics. `test_misc_012_account_menu_responsive` needs updating to check for these via link/text locators instead of button role before it can be flipped to assert reachability (not done automatically here, since it's a genuine test-code update, not a one-line flip).
### 35. [RESOLVED 2026-09-13] Raise Support Ticket cannot be submitted -- originally: "X selected" counter stuck and Submit stayed disabled. Now confirmed FIXED end-to-end (an earlier same-day "Submit does nothing" reverification note was itself a false positive from an insufficient wait, corrected below).
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
- **Reverification (2026-09-13, live) -- ✅ FIXED. Earlier same-day reverification notes below (the "Submit is enabled but the click does nothing" finding) were themselves a false positive -- corrected after the user pushed back, having manually confirmed tickets genuinely do get created.** Root cause of my own false positive: my diagnostic script's wait after clicking Submit was too short for this page's real (and separately confirmed, see the new performance finding below) slow response time, so I was reading an in-flight state as a final "nothing happened" result. Re-tested properly with generous waits across 4 independent fresh-vehicle attempts: every one showed a "Ticket successfully created" toast, and a fresh reload + search confirmed the exact new ticket present in the list every time (e.g. `TCKT/130926/14551` for one run, matching its unique marker comment exactly). The "X selected" counter fix from earlier the same day still holds. `Tests/functional/test_misc_raise_ticket_functional.py`'s regression pins rewritten to assert genuine success (submission, toast, and list presence) instead of the retracted "inert click" finding.
- **New, related finding (not a bug in isolation, flagged for product awareness):** attempting a second ticket for a vehicle that already has ANY open ticket is rejected with "Complaint already exists for `<vehicle IMEI>`" -- confirmed this is **not** scoped to the same category as the existing ticket (tested same-category-repeat and different-category-repeat against the same vehicle, both rejected identically, across 3 independent vehicles). This means a vehicle with an open "Odometer is wrong" ticket cannot also have a separate "Invalid gps" ticket raised for an unrelated issue until the first is closed. May be an intentional one-active-complaint-per-vehicle business rule rather than a bug, but is worth product-team confirmation given it can block reporting a second, genuinely distinct issue on the same vehicle.
- **New finding (real, confirmed root cause of a user-reported point of confusion): the rejection message identifies the vehicle by its raw IMEI, not by the name/plate shown in the selector, making it look like an unrelated vehicle is being cited.** The user directly hit this confusion live ("I am selecting a different vehicle... why does it matter") after seeing "Complaint already exists for 865820071135078" despite having picked a vehicle by its plate-style name. Ran a full RCA across 9 vehicles spanning the account's entire fleet (first/middle/last of 36): the Select Vehicles combobox's displayed value matched the actually-selected vehicle name exactly in all 9/9 attempts (no selection-tracking bug); of those, 5 were rejected as already having an open ticket and 4 succeeded fresh; each of the 5 rejected vehicles was re-tested a second time and cited the exact same IMEI both times (5/5 consistent); and no two different vehicle names ever shared the same cited IMEI (zero cross-vehicle collisions). This rules out a real vehicle-selection or vehicle-mapping bug -- the block is always correctly tied to the vehicle actually selected. The genuine issue is purely a display/UX one: the selector uses plate-style names (e.g. "ptc400-demo", "GCBL10536MHG19CG06323") while the rejection message switches to a completely different-looking raw IMEI number (e.g. "864688053444367") with no visible link between the two, so a user has no way to recognize the cited vehicle as the one they just picked. Recommend the rejection message cite the same identifier the selector uses (or both), e.g. "Complaint already exists for ptc400-demo" instead of the bare IMEI.
- **New finding: intermittent slow loading, both for the ticket list and for ticket submission** -- confirmed live (and independently by the user manually) that the Support ticket list can take several seconds longer than expected to replace its "No support tickets found" placeholder with real data, and that Submit Ticket's own response can likewise take noticeably longer than a typical form submission. Confirmed this is intermittent/flaky rather than a constant fixed delay (varied between fast and slow across repeated checks). `Pages/support_page.py`'s `open()` and `open_ticket_history()` were hardened to wait for real content rather than a fixed timeout, which was masking this as apparent data-loss in this session's own test framework before being corrected.
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
- **Reverification (2026-09-13, live, 3x pass):** ✅ **FIXED.** With a short settle delay after opening the dialog (consistent with the 2026-09-07 nuance above -- this was always a timing race, not an absolute rejection), `fill()` now reliably sets the value, and the character counter updates correctly to match (e.g. a 43-character string shows "43/200"). No regression test currently exists for this bug (per its original "not yet automated" note) to flip.
### 37. [CRITICAL, SECURITY -- symptom evolved, see 2026-09-13 reverification] Change Password Stage 1 ("Verify" current password) provides no real authentication -- originally: always rejected the correct password; now: accepts ANY password, with zero server-side check
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
- **Reverification (2026-09-13, live) -- SYMPTOM CHANGED, now a more severe SECURITY vulnerability, not fixed:** The literal complaint ("Verify rejects the correct password") no longer reproduces -- entering the correct current password is now accepted. But re-testing properly (attempting the negative case, a **wrong** password) found something worse: Stage 1's "Verify" **unlocks Stage 2 for ANY input at all**, including a deliberately wrong password (`"CompletelyWrongPassword999XYZ!"`) -- confirmed 3x live. Network-capture during the Verify click shows **zero `/api/` calls fire at all**, for either a correct or an incorrect password -- the "Current password verified" success toast and Stage 2 unlock are not backed by any server-side check whatsoever; they appear to be a hardcoded/unconditional client-side success. Went one step further and confirmed the **Update Password button itself becomes genuinely enabled** once a new password is filled in, with Stage 1 "passed" on a wrong password -- i.e. the flow is fully prepared to submit a real password change with no current-password verification anywhere in the path. **Did not click Update Password** to avoid actually changing the shared staging test account's real credentials from a diagnostic script -- this is a deliberate stop-short, not evidence the final submit itself is safe; it may or may not have its own server-side check, which is unknown and should be verified by the product team directly, not by an automated script risking the shared account. **Impact**: this is now a broken-authentication / missing re-authentication-control vulnerability (relevant OWASP category: Identification and Authentication Failures) -- Stage 1's entire purpose is to confirm the person changing the password still knows the current one (defense against a hijacked/left-open session); that gate currently provides zero real protection. This is more severe than the original bug, not less: previously no one (including legitimate users) could change their password; now anyone with an authenticated session can very likely reach and submit a password change without ever proving they know the current password. Recommend immediate product-team attention given the severity and that this touches live credentials -- flagging rather than further probing the live Update Password endpoint.
- **Reverification (2026-09-15, production, via regression-pin test failure):** ✅ **LIKELY FIXED.** The regression-pin test `test_misc_118_incorrect_current_password_rejected` (which deliberately asserts the broken behavior -- "Stage 2 unlocks for a wrong password" -- so that it fails loudly the moment the bug is fixed) failed on production: `is_stage_two_unlocked()` returned `False` for a deliberately wrong password, meaning Stage 2 now stays correctly locked. This was caught by an automated regression run, not a fresh manual dive, so treat as a strong positive signal rather than a full reverification -- worth one direct manual confirmation (try a wrong current password, confirm Stage 2 stays locked and no network shortcut exists) before formally closing this out, but the evidence points to this critical vulnerability being resolved.
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
- **Reverification (2026-09-13, live, 3x pass):** ❌ **STILL BROKEN**, unchanged -- searching "device" (still a guaranteed match, the real "Device" category and its "L-400 Overview" article both still exist) returns "0 found"/"No results found" every time.
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
- **Reverification (2026-09-13, confirmed via automated suite):** ❌ **STILL BROKEN**, unchanged -- `test_misc_203_bug39_browser_back_leaves_help_center_entirely` still passes against the confirmed-broken behavior.

### 41. [WITHDRAWN -- test automation false positive, not a product bug] Feedback form's Attachment field "accepts a disguised executable with no content-based validation"
- **Test**: `Tests/functional/test_misc_feedback_functional.py::test_misc_245_reject_spoofed_mime_extension`
- **Original finding (2026-09-13)**: A file with real executable content (`MZ` DOS/PE header) but a `.png` extension appeared to be accepted by the Attachment field with no validation message, and Submit became enabled.
- **User correction (2026-09-13)**: User manually tried the same scenario (rename an executable to `.png`, attach it) and was correctly blocked/errored -- the opposite of what the automated finding claimed. User asked for a retest rather than accepting the original result.
- **Root cause (my test script, not the app)**: the Attachment `<input>` carries `accept=".png,.jpg,.jpeg,.pdf"` (confirmed via `outerHTML`). A real user's native OS "Choose File" dialog enforces this extension filter against the file's actual extension. My diagnostic used Playwright's `set_input_files()`, which injects the file directly into the DOM input via the browser automation protocol and **completely bypasses the native file-picker dialog and its `accept`-attribute enforcement** -- a well-known Playwright/CDP limitation, not something the app can guard against from the client side. Separately, Windows' default "hide extensions for known file types" setting means a naive rename of `app.exe` to `app.png` typically produces `app.png.exe` (the real extension is preserved, not replaced) -- which the accept filter would also correctly exclude from the picker. Both factors independently explain why the user's manual attempt was blocked while my script's was not: the script never went through the real enforcement path the user's browser did.
- **Retest (2026-09-13, live)**: re-ran with both a synthetic `MZ`-header dummy file and a real, full-size `notepad.exe` copy renamed to `.png` -- both still show as "accepted" through `set_input_files()`, confirming the acceptance is an artifact of bypassing the native dialog, not a reproducible app behavior. Not reproducible through any interaction that respects the app's actual `accept` restriction.
- **Correction**: Retracted as a confirmed bug. The Attachment field's client-side `accept` restriction works as intended for normal use and matches the user's live result.
- **Server-side follow-up (2026-09-13, user-authorized live test)**: user asked directly whether this is an exploitable vulnerability -- correctly pointed out that a real attacker wouldn't use the browser's file picker at all, just a raw HTTP request (curl/Burp/Postman), which makes the client-side `accept` attribute irrelevant to real exploitability. Tested this properly: captured the real `POST https://beta2.trackofy.com/api/feedback` request shape live (via Playwright route interception, aborted before send, so nothing was actually submitted by that step), then replayed it directly with Python's `requests` library -- fully bypassing the browser, the file picker, and the `accept` attribute -- with the attachment swapped for real Windows PE executable bytes (`notepad.exe`) disguised as `totally_a_photo.png` (`image/png` content-type). **Result: rejected -- `HTTP 422`, `{"errors": {"attachment": ["The attachment field must be a file of type: jpg, jpeg, png, pdf, webp."]}}`.** A clean control request (identical shape, genuine PNG bytes) through the same raw path was accepted (`HTTP 200`, `"Feedback saved successfully"`), confirming the 422 is specifically about file content, not an unrelated payload issue. This proves the server performs real, content-based (magic-byte) validation independent of the browser/client -- not just an extension check.
- **Final conclusion**: not a vulnerability. Confirmed safe at both layers: the browser-enforced `accept` attribute blocks the naive path (matches the user's manual result), and the server independently rejects mismatched file content even when that client-side layer is bypassed entirely via a raw API call. No further action needed.

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
- **Reverification (2026-09-14, live):** ✅ **FIXED.** The Notification filter now offers 5 options ("All Status", "Sent", "Pending", "Failed", "Skipped") -- confirmed live the new "Skipped" option is present and, when selected, correctly filters the report to only SKIPPED rows (checked 5 of 50 returned rows, all SKIPPED).
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
- **Reverification (2026-09-14, live):** ❌ **STILL BROKEN**, unchanged -- clicking "Export report to Excel" produced no export-related network request and no file download; the only requests observed after the click were unrelated in-flight map-address lookups already caused by the report's own map rendering.
- **Reverification (2026-09-15, production, via regression-pin test failure):** ⚠️ **PARTIALLY FIXED.** The regression-pin test `test_vt_166_export_report` (deliberately asserts each export button is still a no-op) showed a split result: Export to **Excel** is still confirmed a no-op (that assertion held). Export to **CSV** now genuinely fires a download (that assertion failed, exactly as the test's own docstring predicts it would if fixed) -- confirmed a real file download now occurs. The test stopped at CSV (first failure), so PDF/Print/Copy were not re-checked this pass. Caught via an automated regression run, not a fresh manual dive -- worth a direct manual pass to confirm CSV's download content is correct and check PDF/Print/Copy's current state.
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
- **Reverification (2026-09-15, production, via regression-pin test failure):** ✅ **LIKELY FIXED.** The regression-pin test `test_vt_129_alert_type_specific` (deliberately asserts the filter is still ignored) failed: every row returned for a "Speeding"-filtered report was genuinely "Speeding" (`alert_names == {'Speeding'}`), meaning the backend now correctly honors the `alarm_code` filter. Caught via an automated regression run, not a fresh manual dive -- worth one direct confirmation with a second alert type before formally closing this out.

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
- **Note (2026-09-14):** not independently re-verified this pass (time-boxed to other VT findings); no reason to believe it has changed, but flagging as not freshly confirmed today.
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
- **Reverification (2026-09-14, live 3x pass):** ⚠️ **PARTIALLY FIXED.** The main content-hiding half is fixed: the Dashboard heading is now genuinely visible at a 390x844 viewport (confirmed 3x, `is_visible() == True`), so the drawer no longer traps the page's real content behind it. The Close button half is still broken, unchanged: its bounding box is still positioned off-screen (`x: -49`, confirmed identical across all 3 checks), so the auto-opened drawer still cannot be dismissed via its own visible-but-unreachable Close control.

### 89. [Low] Video Telematics Alert Configuration: toggling Status in the Edit dialog is eventually-consistent -- the alert list can still show the old status for several seconds after a confirmed-successful save
- **Test**: `Tests/functional/test_vt_alert_create_functional.py::test_vt_081_082_083_084_085_086_087_edit_alert_full_flow` (now polls with retries to accommodate this).
- **Found**: 2026-09-14, while reverifying Bug #41 (now fixed). Toggling an alert's Status off in the Edit dialog and saving, then reloading once, showed the list still reporting "Enabled".
- **Symptom**: Confirmed live via full network capture: the `toggle_adas_alert_config` API call fires correctly (`{"id":<n>,"is_active":false}`) and its own response confirms success immediately (`{"status":1,"msg":"success","id":<n>,"is_active":0}`). Despite this, the alert list's own read endpoint (`get_adas_alert_config`) can still report the OLD status (`is_active:1`) for several seconds afterward -- confirmed it does eventually catch up after polling with repeated reload cycles (typically resolves within 2-4 reload attempts, a few seconds).
- **Impact**: Low -- same shape and severity as the already-documented Bug #60 (Admin Panel device assignment eventually-consistent). Not data-destructive (the toggle genuinely saved), but an admin checking the list immediately after saving could see a stale, contradictory status and reasonably conclude the save failed.
- **Reverification (2026-09-14, live):** REPRODUCED once, confirmed via raw API response inspection; the test now polls rather than checking once to avoid this exact false failure.

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
- **Reverification (2026-09-14, live):** ✅ **FIXED.** The heading now correctly reads "Sign in to your account". This one-locator fix (`Pages/login_page.py`'s `heading`) had been silently hard-coded to the old typo text, cascading into fixture-setup failures across almost the entire Login test suite (`login_page.open()` waits on this heading) -- fixed to match loosely, which also resolved that unrelated mass-failure. (tabindex="-1")
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
- **Reverification (2026-09-14, live):** ✅ **FIXED.** `tabindex="-1"` is gone from the button entirely (now `None`, natural DOM tab order); the aria-label also changed from "Toggle password visibility" to state-specific "Show password"/"Hide password" (a real, working accessible name either way). This locator change had cascaded into 3 unrelated test failures (`test_login_018_019`, `test_login_020`) whose own `password_toggle_btn` locator was hard-coded to the old aria-label -- fixed once at the page-object level.
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
- **Reverification (2026-09-14, live):** ✅ **FIXED.** Confirmed live against both a nonexistent username and a real account with a wrong password: the error toast now reads a clean, safe "Invalid credentials or you are not authorized." with no raw HTTP client text, no backend hostname, and no endpoint path anywhere. Both scenarios show the identical message (no username-enumeration risk introduced by the fix).
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
- **Reverification (2026-09-14), corrected after user root-cause):** ❌ **STILL BROKEN, but the symptom changed -- server no longer reachable with an invalid PIN Code, replaced by a silent, zero-feedback dead click.** Initial re-check found Submit permanently disabled and wrongly concluded the scenario was unverifiable (Bug #78 below); the user correctly pointed out the real cause was two silently-mandatory fields ("Saler Person" / "Sales Person Contact", no asterisk, unreachable via `get_by_label` -- same missing-`for`-attribute gap as Company Name/GST/PAN/Address/City/PIN Code) that this test's own helper (`fill_billing_info_minimal()`) was failing to fill correctly (a generic bulk-fill loop was overwriting them with a format Sales Person Contact's own validator silently rejects). Fixed the helper to fill both via their real placeholder text with valid-format values -- Create Dealer now reaches Submit-enabled cleanly and a normal dealer creation completes successfully end-to-end (`Tests/Admin Panel/functional/test_admin_dealer_functional.py`, all 7 tests pass). With that fixed, re-tested the ORIGINAL Bug #58 scenario (non-numeric PIN Code) properly: Submit's `disabled` attribute stays cleared (button reports enabled), but **clicking it with an invalid PIN Code fires zero network requests at all** -- no `create-dealer` call, no toast, no visible change, the dialog just stays open with no indication anything happened. Confirmed live 2x. This means the original information-disclosure bug (raw SQL error reaching the client) no longer reproduces -- the request never reaches the server now -- but it's been replaced by a different, still-real UX defect: an admin who mistypes the PIN Code sees an apparently-clickable, enabled Submit button that silently does nothing, with zero feedback that anything is wrong. See Bug #81 (new) for this corrected finding.
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
- **Reverification (2026-09-14, live):** ❌ **STILL BROKEN**, unchanged -- 10 consecutive raw API requests against a nonexistent username all returned `401` with no growth in response time (0.14-0.21s throughout) and no `429`/lockout.
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

**Consolidated reverification note (2026-09-14, full automated suite re-run, bugs #52-57, #59-61, #63-69):** ran the complete Admin Panel suite fresh today (79 tests: `Tests/Admin Panel/**`, 63 passed / 10 failed / 2 skipped / 4 errors). Every one of today's 14 failures/errors was individually triaged live and traces to either a stale test assumption (fixed -- see Bugs #79-88 below) or a genuinely new finding (Bugs #79-88); **none** of them map to bugs #52-57, #59-61, or #63-69's own dedicated tests/regression pins, meaning every test tied to those bug numbers passed cleanly against today's live app with no change from their 2026-09-13 status above. Bugs #58 and #62 got dedicated 2026-09-14 re-checks (see their own notes above -- #58's symptom changed, see Bug #82's correction below; #62 is now fixed).

### 78. [WITHDRAWN -- root cause found, corrected below] "Create Dealer wizard's Submit button never enables, even with every required field correctly filled"
- **Original claim**: Create Dealer's Submit button stayed disabled no matter how completely the form was filled, blocking dealer creation entirely.
- **Correction (2026-09-14, same day, user-provided root cause)**: the user correctly identified the real cause -- two fields, "Saler Person" (a real typo in the app's own placeholder text) and "Sales Person Contact", are silently mandatory (no asterisk) and were never actually being filled by this suite's own `fill_billing_info_minimal()` helper: they're unreachable via `get_by_label` (no `for` attribute, same gap as several other Dealer-wizard fields), so the helper's `if sales_name.count() > 0:`-guarded fill silently no-opped, and a separate generic "fill every empty textbox with 100001" loop then overwrote them with a value Sales Person Contact's own format validator silently rejects (6 digits, not a real phone number) -- with no visible error anywhere to reveal this. This was a test-automation gap, not a product defect: a real admin filling the form normally (typing an actual name and phone number) would never hit this. Fixed `fill_billing_info_minimal()` to reach both fields by their real placeholder text and fill them with valid-format values, filling them BEFORE the generic bulk-fill loop so it can no longer overwrite them. Confirmed fixed: all 7 tests in `test_admin_dealer_functional.py` pass, including a full real dealer creation end-to-end.
- **Residual, real finding kept**: see Bug #81 below -- Sales Person Contact (and likely "Saler Person") having no asterisk despite being effectively required, with zero validation feedback when the format is wrong, is itself worth flagging.

### 79. [Low] Admin Panel: /admin/billing/dashboard silently redirects to /admin/dashboard, same pattern as Bug #62
- **Test**: `Tests/Admin Panel/functional/test_admin_smoke_functional.py::test_admin_smoke_002_billing_dashboard_loads`
- **Found**: 2026-09-14, while reverifying Bug #62 (whose original 4 routes are now confirmed FIXED). This 5th route, not part of Bug #62's original list, still exhibits the exact same symptom.
- **Symptom**: Confirmed live: navigating directly to `/admin/billing/dashboard` (a real, clickable nav destination -- "Billing" sub-items exist in Quick Actions/menus referencing it) silently lands on `/admin/dashboard` instead, with no error, no "not implemented" notice, no permission-denied indication.
- **Impact**: Low, same reasoning as Bug #62 -- a secondary reporting page, not core CRUD, but a real broken nav destination.
- **Reverification (2026-09-14, live 3x pass, via test loop):** REPRODUCED 3/3.

### 80. [Minor] Admin Panel: two redundant sign-out controls have inconsistent labels -- "Sign Out" (desktop, profile-icon dropdown) vs. "Logout" (a separate, mobile-only nav item)
- **Test**: `Tests/Admin Panel/security/test_admin_security_functional.py::test_admin_security_005_admin_session_cookie_not_usable_after_logout` (uses the desktop path).
- **Found**: 2026-09-14, flagged directly by the user while reviewing this session's work, then confirmed live and via screenshot.
- **Symptom**: Confirmed live: clicking the profile icon (`.pi.pi-user`, top-right, desktop-visible at any standard width) opens a dropdown containing a red "Sign Out" option -- this is the real, primary desktop sign-out control. Separately, a `p-menubar` nav item literally labeled "Logout" also exists, but is CSS-gated `mobile-only` (invisible at any width above ~768px, only reachable via a hamburger toggle that itself only appears at mobile widths). Two different, redundant controls for the same action, with two different labels depending on which one a viewport happens to expose.
- **Impact**: Minor/cosmetic -- doesn't block sign-out (the desktop path works fine, confirmed: session is genuinely invalidated server-side afterward), but is a real, confirmed naming inconsistency an admin could notice if they ever see both (e.g. resizing a browser window, or comparing desktop vs. tablet use).
- **Reverification (2026-09-14, live):** REPRODUCED -- confirmed via automated DOM inspection at 1280x720/1920x1080 (desktop) vs. 390x844 (mobile), and independently confirmed by the user's own screenshot of the desktop "Sign Out" dropdown.

### 81. [Medium] Admin Panel Create Dealer: "Saler Person" [sic] and "Sales Person Contact" are silently mandatory with no asterisk, and no `for`-attribute label association
- **Test**: `Pages/admin_user_page.py::fill_billing_info_minimal` (documented inline); found via the user's own live testing and correction of the withdrawn Bug #78.
- **Symptom**: Confirmed live: the Billing Information step's "Saler Person" (a real typo in the app's own placeholder -- not "Sales Person") and "Sales Person Contact" fields render with no `*` and no `for` attribute connecting them to their visible label text (same gap already documented for Company Name/GST/PAN/Address/City/PIN Code on this same wizard), yet Create Dealer's Submit stays disabled/ineffective without them being filled with valid-format values. A screen-reader user, or an admin scanning for which fields are required by their asterisks, has no way to know these two are effectively mandatory.
- **Impact**: Medium -- an admin who skips these two (reasonably, since nothing marks them required) fills out the entire rest of a long form only to find Submit doesn't work, with no field-level indication of why (see Bug #82 for the compounding "no feedback at all" issue).
- **Reverification (2026-09-14, live):** REPRODUCED via a full field-by-field DOM probe (`get_by_label` returns 0 matches for both; both filled instead via their real placeholder text).

### 82. [High] Admin Panel Create Dealer: submitting an invalid PIN Code silently does nothing -- Submit reports enabled and clickable but fires no request, no error, no visible change at all
- **Test**: `Tests/Admin Panel/functional/test_admin_dealer_functional.py::test_admin_dealer_008_bug82_invalid_pin_code_silently_does_nothing_on_submit`
- **Symptom**: Confirmed live 2x: with every other field validly filled, entering a non-numeric value (e.g. `AutoQA123`) into either PIN Code field and clicking the now-enabled "Create Dealer" button produces **zero observable effect** -- no `POST .../api/create-dealer` request fires (confirmed via full network capture, every other real background call still fires normally), no toast or inline error appears, the dialog simply stays open exactly as it was. Contrast with a fully valid submission, which correctly fires the request and succeeds (confirmed via the passing `test_admin_dealer_002` in the same pass).
- **Impact**: High -- this is arguably worse than the originally-reported SQL-leak bug it replaces: an admin who mistypes a PIN Code gets no feedback whatsoever that their click did anything at all. The button looks and reports as enabled and clickable, so there's nothing to suggest the form is invalid -- a real user would likely conclude the page is frozen or broken, with no path to understanding what to fix. (On the positive side: this does mean the original raw-SQL-error information disclosure no longer reproduces, since the request never reaches the server with invalid input.)
- **Reverification (2026-09-14, live 2x pass):** REPRODUCED 2/2 -- zero network activity and zero visible feedback both times, against a control confirming a valid submission works normally in the same session.
- **CORRECTION (2026-09-14, same day, user root-cause):** ⚠️ **This finding was itself based on a flawed test method and does not reflect real user-reachable behavior.** The user manually tested and reported the PIN Code input genuinely does NOT accept non-numeric characters at all when typed normally -- confirmed live: real keystrokes (`.type()`, not `.fill()`) of `"Ab12Cd34"` register as `"1234"` in the field (letters are silently filtered character-by-character as they're typed). My original finding used Playwright's `.fill()`, which sets the DOM value directly and bypasses this real keystroke-level filter entirely -- the exact same class of automation-vs-reality gap as the earlier MIME-spoofing correction (Bug #41) this session. **The scenario this bug describes (a non-numeric value reaching Submit) cannot actually happen through normal use**, so it's withdrawn as a real, user-reachable defect. The regression test (`test_admin_dealer_008`) is kept, since the underlying "invalid PIN Code silently produces no request" observation itself is still real and worth pinning -- it's just not reachable via normal typing, only via a direct value injection (as an automation script, or conceivably a non-browser API client, could do). See the two real, related findings the user found manually instead: Bug #86 (no max/min length limit on PIN Code) and Bug #87 (editing a dealer with an out-of-range PIN Code fails with a raw SQL error).

### 83. [High] Admin Panel: Brand/Model images are served over plain HTTP from an HTTPS page, so they silently fail to load everywhere -- list table, and (per the user's own live testing) the Edit wizard
- **Test**: none automated yet; found via the user's own live testing (uploaded a brand logo, saw it render corrupted in the table and missing in the Edit dialog), confirmed via automated DOM inspection.
- **Symptom**: Confirmed live: every brand image URL returned by the API and rendered in Manage Brand's list table is `http://beta2.trackofy.com/public/images/brands/...` -- plain HTTP -- while the app itself runs entirely on `https://staging.trackofy.com` and its own API calls go to `https://beta2.trackofy.com`. Checked all 6 images visible on the Brand list (5 real pre-existing brands plus 1 created live this session): **all 6** report `naturalWidth: 0, naturalHeight: 0` (a definitively broken/failed image load, not a slow one -- `complete: true` on the `<img>` element) despite the browser considering the load "finished." This is the classic mixed-content pattern: a browser loading an HTTPS page silently blocks/fails an embedded plain-HTTP image resource. The user independently confirmed the same broken image in the list AND that the Edit Brand wizard's own image preview fails to load the existing logo at all.
- **Impact**: High -- this affects every single brand's logo, with no working image anywhere in the Manage Brand feature (list or edit), for both pre-existing real data and anything newly uploaded. Very likely affects Model images identically, since they're uploaded/served through the same pattern (not independently confirmed this pass due to time).
- **Reverification (2026-09-14, live):** REPRODUCED on all 6/6 images checked in the Brand list; corroborated independently by the user's own manual testing of the Edit wizard.

### 84. [Medium] Admin Panel Documentation > Category: "Create" button has no required-field gating at all -- reports enabled on a completely empty form
- **Test**: none automated yet; found while covering the Configuration tab's 3 create-forms at the user's request.
- **Symptom**: Confirmed live: opening Documentation's "Create Category" dialog fresh (Category Name*, Slug*, Sort Order*, Status* all marked required with an asterisk) shows the "Create" button already `is_enabled() == True` with every field completely empty -- unlike the equivalent Create Brand, Create Model, and Create Menu dialogs, which all correctly keep their own Submit/Create buttons disabled until required fields are filled.
- **Impact**: Medium -- inconsistent with every sibling form in the same Configuration tab; risks an admin submitting a genuinely empty/incomplete category record with no client-side warning. (Not tested to see what the server does with a truly empty submission, to avoid creating bad data.)
- **Reverification (2026-09-14, live):** REPRODUCED -- `Create` button reports enabled immediately on dialog open, before any field is touched.

### 86. [Medium] Admin Panel Create/Edit Dealer: PIN Code field has no minimum or maximum length validation
- **Test**: none automated yet; found by the user's own manual testing, confirmed via real (typed, not `.fill()`-injected) keystrokes.
- **Symptom**: Confirmed live: the PIN Code field correctly filters out non-digit characters as they're typed (a real, working restriction), but enforces no length bounds at all -- typing 13 digits (`"1234567890123"`) registers all 13 characters with no truncation or rejection, and typing as few as 2 digits (`"12"`) is equally accepted with no minimum-length warning. A real PIN Code (Indian postal format, matching this app's other address fields) is a fixed 6 digits.
- **Impact**: Medium on its own (a length-format gap), but see Bug #87 below -- this is what makes that more severe, server-side-error bug reachable in the first place.
- **Reverification (2026-09-14, live):** REPRODUCED via real typed keystrokes (not `.fill()`), both over-length and under-length.

### 87. [High] Admin Panel Edit Dealer: an out-of-range-length PIN Code is accepted on Create but fails Edit with a raw SQL error
- **Test**: none automated yet; found and reported by the user's own manual testing (attempted to reproduce via automation but ran into an unrelated dialog-overlay timing issue in the test script itself; not independently confirmed by me this pass -- reporting as the user found it, per the instruction to mark unconfirmed findings honestly rather than assume).
- **Symptom (as reported by the user)**: A dealer created with a PIN Code longer than 6 digits (see Bug #86 -- nothing prevents this at Create time) later fails when that same dealer is edited: submitting the Edit form shows an "Edit failed" toast, and the Network tab shows a SQL-related error response. The user also specifically noted the asymmetry: a PIN Code shorter than 6 digits does NOT trigger this failure on Edit, only longer-than-6-digit values do.
- **Impact**: High if confirmed -- this is the same class of issue as the original Bug #58 (raw SQL error from unvalidated PIN Code input), just reached via a different path (Edit, with an over-length value that Create itself never blocks) rather than the originally-reported non-numeric-value path (which, per the correction above, cannot actually be typed).
- **Status**: ❔ **REPORTED BY USER, NOT YET INDEPENDENTLY VERIFIED.** Needs a live reverification pass: create a dealer with a >6-digit PIN Code, then edit it and resubmit, capturing the Network tab response.

### 88. [High] Admin Panel Profile: the shared "Send OTP" mechanism fails with a raw technical error, leaking the backend endpoint path -- blocks BOTH Update Mobile Number and Change Password
- **Test**: none automated yet; found while covering Admin Panel Profile/Change Password at the user's request.
- **Symptom**: Confirmed live: opening My Profile > the Mobile field's edit (pencil) icon opens an "Update Mobile Number" dialog; clicking its "Send OTP to Current Mobile" button shows an error toast reading the literal, unmodified HTTP client error: `"Http failure response for https://beta2.trackofy.com/user_new.php: 0 Unknown Error"` -- the same raw-error-leak pattern as Bug #50 (main app login), but in a different location (Admin Panel Profile) and a different backend endpoint (`user_new.php`, newly disclosed here). Status `0` typically indicates the request never received a proper HTTP response at all (a network/CORS-level failure) -- confirmed via full response capture: no `user_new.php` call appears among the responses received at all, only unrelated dashboard calls, meaning the request never got a response of any kind. **The user separately reported live that Change Password's own "Send OTP" hits this exact same failure** -- reverified directly: identical toast text, identical endpoint, identical `0 Unknown Error` status, confirming both features share one broken underlying OTP-send mechanism, not two independent bugs.
- **Impact**: High -- discloses an internal backend endpoint name/path, and completely blocks TWO real account-management features (Update Mobile Number and Change Password both have no working path to completion -- no OTP is ever sent for either).
- **Reverification (2026-09-14, live):** REPRODUCED for both Update Mobile Number and Change Password.

### 91. [Medium] Admin Panel Profile: the "Copy" icon (Address -> Billing Address) in the Update Profile dialog does nothing
- **Test**: none automated yet; found by the user's own live testing.
- **Symptom**: Confirmed live: the Update Profile dialog (My Profile's main edit pencil) has a `.pi-copy` icon between the Address and Billing Address sections. Clicking it produces **zero observable effect** -- every field's value (Address, PIN Code, City, State, Country) is byte-identical before and after the click; the Billing Address section's own (different) values are never overwritten with the Address section's values.
- **Impact**: Medium -- a real, visible control that does nothing at all, forcing an admin to always manually retype the full billing address even when it's identical to the main address (the obvious use case this icon exists for).
- **Reverification (2026-09-14, live):** REPRODUCED -- confirmed via a full before/after field-value dump across all 10 address-related inputs.

### 93. [Medium] Admin Panel Profile: Update Profile Picture crashes with a raw PHP/GD error for a technically-imperfect but browser-decodable PNG, instead of a clean validation message
- **Test**: none automated yet; found while verifying the Update Profile Picture feature works correctly (it does, for a genuinely valid image -- see the confirmation note below).
- **Symptom**: Confirmed live: uploading a minimal PNG file (one that every browser tested happily decodes and displays -- confirmed via `<img>` `naturalWidth`/`naturalHeight` both reporting correctly, and the app's own client-side file-picker accepting it with no complaint) and clicking "Update Profile Image" returns `HTTP 500` from `/api/update-profile` with the raw body: `{"status":false,"message":"Something went wrong","data":{"error":"imagecreatefrompng(): gd-png: fatal libpng error: IDAT: incorrect data check","line":3461}}`. The UI surfaces this as a generic "Internal Server Error" toast, but the raw PHP function name, library error text, and source line number are all present in the actual API response, visible to anyone inspecting the Network tab. **Confirmed this is a real, distinct backend gap and not just a bad test file**: a genuinely valid PIL-generated PNG (200x200, spec-compliant) uploaded via the identical flow immediately afterward succeeded cleanly (`200 {"status":true,"message":"Profile updated successfully"}`).
- **Impact**: Medium -- the core feature works for normal images (see below), but the server-side image processing (PHP's GD library) is stricter than what client-side/browser validation accepts, and failures in that gap surface as a raw technical error with internal implementation details, rather than a clean "please upload a valid image" message.
- **Reverification (2026-09-14, live):** REPRODUCED once for the crash, with an immediate clean-success control confirming the feature otherwise works correctly.
- **Positive finding, not a bug**: Update Profile Picture's core flow (Choose file -> "Update Profile Image" button -> real `POST /api/update-profile` -> success toast -> avatar visibly updates with a new cache-busting timestamp) is confirmed working correctly end-to-end for a genuinely valid image.

### 94. [Low] Admin Panel Profile: after updating the profile picture, the old photo is still briefly/sometimes visible instead of the new one -- NOT YET INDEPENDENTLY REPRODUCED

- **Test**: none automated yet; found by the user's own live testing.
- **Symptom (as reported by the user)**: After successfully updating the profile picture (new photo confirmed uploaded), the old photo is still shown somewhere referred to as the "profile menu" instead of the new one.
- **Verification attempts (2026-09-14, automated, 3 separate scenarios -- could NOT reproduce)**: (1) Upload new photo, then navigate away via an SPA link (Dashboard) and back to My Profile via the profile-icon menu, with no hard reload -- the `<img>` `src` on the Profile page picked up the new cache-busting timestamp correctly every time. (2) Upload new photo, then do a full hard page reload (`page.reload()`) -- same result, new timestamp reflected correctly. (3) Checked the profile dropdown menu itself (the one opened by clicking the header's person icon, containing "My Profile"/"Sign Out") for its own avatar thumbnail -- it contains **zero `<img>` elements at all**, on the Dashboard, on the Profile page, and after a hard `goto` between them, so that specific dropdown cannot be the "profile menu" showing a stale photo, since it never renders any photo.
- **Impact**: Low, pending reproduction -- if real, this is a stale-cache/re-render bug in whichever component the user means by "profile menu," but which specific element that is has not been pinned down yet.
- **Status**: ❔ **REPORTED BY USER, NOT YET INDEPENDENTLY VERIFIED.** Open questions for the user to help narrow this down: which screen/element specifically shows the old photo (the small header icon, the My Profile page's own big avatar, or something else)? Does it happen after a full browser refresh, or only when re-opening the menu/page without refreshing? Same browser tab as the upload, or a different one/a different device?

### 92. [High] Admin Panel Profile: Address/City/State/Country/PIN Code fields have zero input validation -- and the live account data already contains garbage values proving it
- **Test**: none automated yet; found by the user's own live testing, confirmed live and further corroborated by the real, already-persisted profile data.
- **Symptom**: Confirmed live 2x: (1) typing pure digits (`"999888777"`) into the City field via real keystrokes registers completely, with no character filtering, format check, or validation message. (2) The account's own REAL, currently-saved profile data already contains exactly this class of garbage, proving the gap isn't just theoretical: **Country** = `"223232313213123"` (a number where a country name belongs), **Billing PIN Code** = `"67238052e23232"` (mixed alphanumeric garbage in a numeric field), **Billing City** = `"6723805sdsd"` (garbage), **Billing State** = `"6723805"` (a number), **Billing Country** = `"6723805"` (a number). This data was already live and persisted before this session touched the page at all -- meaning some prior submission (whether a real user, a test, or a script) got this garbage all the way into the saved account record, confirming no validation exists server-side either, not just client-side.
- **Impact**: High -- this isn't a hypothetical "could someone submit bad data" question, it's a confirmed, already-happened instance of exactly that, sitting in a real account's profile right now. Address-shaped fields with no format/type validation anywhere in the pipeline is a real data-integrity gap.
- **Reverification (2026-09-14, live):** REPRODUCED -- both the live-typing check and the pre-existing garbage data were confirmed in the same session.

### 96. [Info] Admin Panel login: backend authentication succeeds but the page never redirects to /admin/dashboard, after the dedicated admin test account was used for very heavy repeated fresh logins

- **Test**: none automated yet; found while running the Admin Panel functional batch against production, isolated and diagnosed separately outside the batch run.
- **Symptom**: Logging in as the dedicated Admin Panel test account (`ADMIN_TEST_USERNAME`) via the normal login form: the backend calls succeed cleanly (`POST /core/token.php` -> 200, `POST /core/user.php` -> 200, no error response), but the page never navigates away from the public landing page (`/`) to `/admin/dashboard` -- confirmed hanging for 30+ seconds with no error toast, no console error, nothing. This exact login flow worked normally earlier the same day (confirmed at the start of this session, and via 86 passing tests in the func_admin batch that log in the same way).
- **Context (why this is filed as Info, not a confirmed severity-rated bug)**: this account had just been used for several hundred rapid, fresh, back-to-back UI logins in a short window (3 consecutive full attempts at the ~67-test Admin Panel functional batch, each test doing its own fresh login). The most likely explanation is some form of account- or session-level throttling kicking in under that volume, rather than a defect an ordinary user would ever hit -- but this hasn't been confirmed one way or the other (no explicit rate-limit error, no lockout message, nothing surfaced to distinguish "throttled" from "a real intermittent backend/session bug"), so it's logged as an open observation rather than assumed to be either.
- **Impact**: Blocked all Admin Panel functional/security test coverage for this pass (every test in that suite depends on this login succeeding). Whether it has any real-world impact on normal (non-test-automation) admin usage is unknown and would need investigation by someone with visibility into the backend/session layer.
- **Status**: ❔ **OPEN / INFO -- not root-caused.** Needs either: (a) time for any throttling to clear and a clean retry, or (b) backend-side investigation (auth/session logs for this account) if it recurs under normal usage, not just heavy automated re-login load.

---

## CAN Module

### 73. [Critical] Any account can access all 6 CAN module pages by direct URL, even with no CAN entitlement and no CAN nav link
- **Test**: `Tests/security/test_can_security.py::test_can_sec_003_non_can_account_direct_url_access_denied`
- **Symptom**: Confirmed live, reproduced across 3 independent fresh sessions: logging in as the main test account (`tarun_01`), which has no `CAN` entry in its left nav (confirmed absent), and then navigating directly to any of `/can/dashboard`, `/can/units`, `/can/trends`, `/can/report`, `/can/alerts`, `/can/settings` renders the real CAN page for every single route -- correct heading, correct module chrome, no redirect, no access-denied state, no empty/placeholder view. This is not a partial leak: all 6 CAN routes are fully accessible to an account with no CAN entitlement.
- **Impact**: The CAN nav link's absence is purely a UI convenience, not an access control -- there is no server- or route-level authorization check gating the CAN module by account entitlement. Any authenticated user of this application (any tenant/account) can view another account's CAN fleet data (units, protocols, alert thresholds, generated reports) simply by knowing/guessing the URL, regardless of whether their own account is provisioned for CAN. This is a serious cross-feature authorization gap, not merely a cosmetic nav-visibility issue.
- **Reverification (2026-09-10, live 3x pass):** REPRODUCED 3/3 -- all 6 `/can/*` routes rendered full real content for the non-CAN account in every one of 3 independent fresh sessions.
- **Reverification (2026-09-14, live 3x pass):** ✅ **FIXED.** All 6 `/can/*` routes now correctly bounce a non-CAN account to `/home` with an "Info: You do not have access to the CAN module." toast, reproduced 3/3 in independent fresh sessions. A real server/route-level authorization check now exists. `Tests/security/test_can_security.py::test_can_sec_003_non_can_account_direct_url_access_denied` (all 6 parametrized routes) confirmed passing.

### 74. The Live Fleet Map's full-viewport overlay layer blocks normal clicks on the CAN sub-menu and page controls, despite being marked `pointer-events: none`
- **Test**: `Tests/edgecase/test_can_navigation_edgecase.py::test_can_nav_edge_001_unforced_click_on_unit_nav_is_blocked_by_map_overlay` (regression pin); also surfaced live while automating `Tests/Smoke/test_can_smoke.py` and several `Tests/positive/test_can_*.py` files before those were updated to use a click-interception workaround
- **Symptom**: Every CAN page renders a full-viewport `.can-map-viewport-boundary` wrapper (`position: fixed; inset: 0; z-index: 9998`) for the Live Fleet Map widget. The wrapper itself has `pointer-events: none` (confirmed via computed style), correctly signaling it shouldn't intercept clicks -- but an unstyled child `<div>` inside it (`pointer-events: auto`, no CSS class) does not inherit that behavior and can sit directly on top of ordinary page controls. Confirmed live and reproduced 3/3 in independent fresh sessions: a plain, unforced Playwright click on the CAN sub-menu's "Unit" link times out with Playwright's own diagnostic explicitly naming this div as the element intercepting the click. The same pattern was observed intermittently blocking comboboxes and buttons elsewhere on Trends, Report, and Settings pages during this session's live test runs.
- **Impact**: Depending on exactly where this invisible click-catching div is positioned at a given moment (likely tied to the floating map widget's current on-screen position/state), it can silently block normal mouse interaction with core CAN navigation and form controls, with no visual indication to the user of why their click didn't register.
- **Reverification (2026-09-10, live 3x pass):** REPRODUCED 3/3 -- identical click-interception by the same unstyled child div, confirmed via `document.elementFromPoint` at the target control's coordinates in all 3 independent fresh sessions.
- **Reverification (2026-09-13, live, slow/deliberate re-check):** ✅ **FIXED.** Confirmed via 4 independent checks: 3 fresh manual sessions plus the existing pinned regression test, all against the CAN-entitled account. The map widget's overlay child (`<app-can-map-window>`) now computes `pointer-events: none` (correctly inherited from its parent, not `auto`) and has a collapsed `0x0` bounding rect, so it can no longer sit on top of anything. `document.elementFromPoint` at the Unit nav link's coordinates now correctly resolves to the link's own inner text, not the overlay. A plain, unforced click on Unit -- and on every other CAN sub-nav link (Trends/Reports/Alerts/Settings/Dashboard) checked in the same pass -- now succeeds and navigates correctly, with no `force=True` needed. `test_can_nav_edge_001_...` flipped to assert the fixed behavior and now passes; `CanBasePage.safe_click()`'s fallback workaround was left in place as a harmless no-op (plain click is always tried first and now always succeeds) rather than removed, to keep the diff minimal.
- **Reverification (2026-09-14, full-suite confirmation):** Still ✅ **FIXED** -- `test_can_nav_edge_001_...` passes as part of a full CAN suite run. No new interception observed across Dashboard/Unit/Trends/Report/Alerts/Settings during this pass's broader regression run.

### 90. [Low] CAN Report page has no PDF export button, unlike its sibling Alerts/Unit/Settings pages
- **Test**: `Tests/positive/test_can_report_positive.py::test_can_report_pos_003_generated_report_has_export_search_pagination` (no longer asserts a PDF button here).
- **Found**: 2026-09-14, while fixing the export-button locator naming difference between CAN pages ("Export to X" vs. Report's "Export report to X").
- **Symptom**: Confirmed live: after generating a CAN report with real results, the export row shows only "Export report to Excel", "Export report to CSV", and "Copy report content" -- no PDF export at all. Confirmed live that CAN Alerts and CAN Unit both DO have a working "Export to PDF" button in the identical shared export-row component (`Tests/positive/test_can_alerts_positive.py::test_can_alerts_pos_004`, `test_can_unit_positive.py::test_can_unit_pos_006`, both pass with a real PDF button present).
- **Impact**: Low -- a real, minor feature-parity gap; an admin wanting a PDF of report data has no way to get one here, unlike every other CAN table view.
- **Reverification (2026-09-14, live):** REPRODUCED -- confirmed absent via a full icon/button sweep of the report's export row, contrasted against 2 sibling pages that do have it.

### 102. [Low] Reports: rapidly clicking Generate fires a duplicate request per click, with no debounce or disable-while-loading guard

- **Test**: `Tests/edgecase/test_reports_standard_edgecase.py::test_rep_rel_003_rapid_generate_clicks_no_duplicate_requests`.
- **Symptom**: Confirmed live: clicking Generate 5 times in rapid succession on Fleet Summary fires 5 separate real `POST /laravel/api/v3/fleet_summary_new` requests (one per click) rather than the button disabling itself after the first click or debouncing extra clicks while a request is already in flight.
- **Impact**: Low -- doesn't corrupt the final rendered result (the last response presumably wins), but wastes backend load proportional to how many times a user impatiently re-clicks, and is generally not how a "Generate" action should behave.
- **Reproduction (2026-09-16, live, production, 2x)**: REPRODUCED both times -- exactly 5 requests for 5 clicks.

### 101. [Medium] CAN Report: generating a report with no Protocol/Units selected never settles into a result or "no data" state within 30 seconds

- **Test**: `Tests/negative/test_can_report_negative.py::test_can_report_neg_001_generate_with_nothing_selected_does_not_crash`.
- **Symptom**: Confirmed live: Generate Report on the CAN Report page stays enabled even with no Protocol/Units selected (not disabled up front, matching how other CAN pages generally behave). Clicking it in that state never renders either a results table or a "no data" message within 30 seconds -- the page doesn't crash or show an error, it just never resolves to any observable end state.
- **Impact**: Medium -- a user who clicks Generate without configuring filters gets an indefinite, unexplained non-response instead of either real (default-scope) results or a clear "select a protocol/unit first" message.
- **Reproduction (2026-09-16, live, production, 2x)**: REPRODUCED both times -- 30s timeout waiting for either a results table or "No data" text.

### 98. [Low, data-sense observation] CAN Alerts: a "Critical"-severity alert row where Actual equals Limit (both 0) for "unknown pid count" -- ambiguous whether this is a real breach

- **Test**: `Tests/functional/test_can_alerts_functional.py::test_can_alerts_func_003_actual_vs_limit_consistent_with_level_for_sampled_rows` (a deliberately soft data-sense check, not a hard business-rule assertion, since the correct breach direction per metric isn't documented).
- **Symptom**: Confirmed live on the CAN Alerts table: a row shows Level = "Critical", Metric = "unknown pid count", Actual = `0`, Limit = `0`. Actual equaling Limit exactly is ambiguous -- it's unclear whether 0 unknown PIDs (a value that intuitively sounds like "nothing is wrong") should ever be classified "Critical" at all, or whether the Level/Actual/Limit computation has a bug for this metric.
- **Related observation (not separately asserted by the test, since breach direction isn't documented)**: two other Critical rows for a different unit/metric also show Actual well *under* a positive Limit ("Error information": Actual 0, Limit 40; "Compressor Voltage": Actual 0, Limit 45) -- plausible if these metrics use "under is bad" semantics (e.g. a sensor reading dropping to 0 indicating a fault), but worth the same scrutiny: confirm the Level/Actual/Limit relationship is intentional per metric, not a shared computation defect.
- **Impact**: Low -- doesn't block any workflow, but a "Critical" label on data that doesn't obviously represent a breach undermines trust in the alert severity system.
- **Reproduction (2026-09-16, live, production)**: REPRODUCED -- confirmed via a full row dump of the CAN Alerts table (CAN-entitled account), row 2: `Critical | unknown pid count | 0 | 0`.

---

## Settings Module — Route Management

### 99. [High] Route Management's location search (Google Places Autocomplete) returns zero results for every query -- the app's own Google Maps API key is not authorized for the Places API

- **Tests**: `Tests/positive/test_settings_route_positive.py::test_set_156_create_valid_route`, `test_set_160_add_waypoint_to_route`, `test_set_169_edit_route` (all 3 fail identically at the same step).
- **Symptom**: Confirmed live via full network + browser console capture: typing into the Origin/Destination/Waypoint search boxes on Create/Edit Route correctly triggers real `GetPredictions` calls to `maps.googleapis.com/maps/api/place/js/AutocompletionService.GetPredictions` for every keystroke (confirmed for queries "Delhi", "Mumbai", "New York", and even a single character "a") -- every one of these requests returns HTTP 200, but the browser console logs the real reason nothing renders: **"This API key is not authorized to use this service or API. Please check the API restrictions settings of your API key in the Google Cloud Console..."**. The base Google Maps JS library and map tiles load and render fine (a different, apparently still-authorized part of the same API key/product) -- only the Places Autocomplete predictions service is blocked.
- **Impact**: High -- this is not a test-only artifact; it's a real, currently-broken feature for every real user of the app. Nobody can search for or select a location by typing in Create Route, Edit Route, or Add Waypoint right now (the input accepts typed text, but no suggestion ever appears to pick, and the underlying flow appears to depend on picking a suggestion -- confirmed live no suggestion means no way to proceed with a typed-only value). Root cause is Google Cloud Console-side API key configuration (Places API not enabled/authorized for this key), not application code -- needs whoever manages the Trackofy Google Cloud project to enable the Places API for this key, not a code fix.
- **Reproduction (2026-09-16, live, production)**: REPRODUCED -- zero suggestions for 4 different test queries including a single generic character, with the exact "API key is not authorized" console error captured directly from the browser in all cases.

---

## Tracking Module (continued)

### 100. ~~[High, Security/UX] An expired session (API returns 401) during Live Tracking or Playback is not detected~~ -- **RETRACTED, likely test defect, not confirmed as an application bug**

- **Tests**: `Tests/negative/test_tracking_state_negative.py::test_trk_state_007_session_expiry_during_live_tracking`, `test_trk_state_008_session_expiry_during_playback_load`.
- **Original symptom (2026-09-16)**: with every `/api/**` and `/trackofy_api_new/**` request mocked via `page.route()` to return a synthetic `401 Unauthorized`, the app did not redirect to login or show any error during Live Tracking / Playback.
- **Retraction (2026-09-16)**: The user manually reproduced a real expired session against production and confirmed the app correctly forces re-authentication -- directly contradicting this test's finding. Follow-up investigation into *why* found real problems with the test's own simulation, not the app:
  - Corrupting the real `localStorage` `token` value and performing a live tracking action produced an ordinary **HTTP 200** from `trackofy_api_new/user.php`, not a 401 -- so tampering the token this way doesn't even reach the code path the test assumes.
  - Probing the same endpoint directly (`fetch()` with an invalid/missing `Authorization` header) returned **400 `"Missing 'method' in request"`** regardless of the auth header, showing this backend does not appear to authenticate via a standard `Authorization: Bearer` header at all -- the real auth mechanism (and therefore what a genuine expired-session response actually looks like) is not what the test assumed when it hand-built a generic `{"message":"Unauthorized"}` / 401 mock.
  - In short: the test's synthetic 401 may not resemble a real auth-failure response closely enough to be a valid simulation, so "the app didn't react to it" doesn't establish that the app fails to react to a *genuine* expired session -- which the user's manual test shows it does handle correctly.
- **Status**: Not a confirmed application defect. Removed from the bug-tracking CSV. Left the two regression tests unmodified for now (touching them without first nailing down the real auth-failure response shape would just trade one guess for another) -- a proper fix needs the actual auth mechanism (token transport, real 401/expired-session response shape) confirmed with the dev team before the test can meaningfully simulate it.

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
