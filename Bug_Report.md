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

---

## Test Suite Notes (not application bugs, for context)

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
