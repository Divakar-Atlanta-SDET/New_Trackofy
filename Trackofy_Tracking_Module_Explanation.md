# Trackofy Tracking Module — Explanation Guide

## 1. What is the Tracking Module?

The **Tracking module** is the part of Trackofy used to visualize and work with vehicle tracking data on a map.

Based on the current Tracking automation specification, the module has two primary modes:

1. **Live Tracking** — monitor selected vehicles using their latest available tracking data.
2. **Playback Tracking** — load and visualize historical tracking data for a selected vehicle and time range.

The Tracking page also provides map controls and layout/preset controls.

> **Simple definition:** Tracking = view vehicles on a map in real time or inspect their historical movement through playback.

The uploaded Trackofy UI source also shows **Tracking** as a top-level application module alongside Unit, Reports, Settings, and Administrator.

---

## 2. Tracking Module Structure

```text
                         TRACKING
                            |
              +-------------+-------------+
              |                           |
           Live Tracking              Playback
              |                           |
       +------+-------+          +--------+---------+
       |              |          |        |         |
   Split Screen    Vehicles    Vehicle   Date/Time  Filters
       |              |          |        Range
       |              |          |          |
   Trail Color     Selection    Hold Time  Overspeeding
   Thickness                    More Filters
              |                           |
              +-------------+-------------+
                            |
                           MAP
                            |
                 Markers / Routes / Trails
```

The automation test suite is organized around navigation, Live Tracking, Playback, Map, state handling, authentication, network failures, and API concurrency. 

---

## 3. Opening the Tracking Module

When the Tracking module is opened, the expected initial experience is:

```text
Open Tracking
     |
     v
Tracking Page
     |
     +--> Map
     |
     +--> Bottom Navigation / Presets
     |
     +--> Live Tracking
     |
     +--> Playback Tracking
```

The current test specification identifies the following expected behaviour:

- Tracking page loads successfully.
- Map is displayed.
- Bottom navigation/preset controls are available.
- Live Tracking tab can be opened.
- Playback Tracking tab can be opened.
- Initial API failures should produce an appropriate error/retry state rather than a false tracking state.

---

## 4. Bottom Presets / Layout

The Tracking page has bottom layout presets.

### Map Only

```text
+-----------------------------+
|                             |
|            MAP              |
|                             |
|                             |
+-----------------------------+
```

The bottom tracking panel is hidden.

### Map + Bottom Panel

```text
+-----------------------------+
|                             |
|            MAP              |
|                             |
+-----------------------------+
|      TRACKING PANEL         |
+-----------------------------+
```

The test suite checks that:

- Map Only displays the map and hides the bottom tracking panel.
- Map + Bottom Panel displays both.
- Repeatedly switching presets does not create duplicate or broken UI.

---

# 5. Live Tracking

**Live Tracking** is used when the user wants to see the latest available position of one or more vehicles.

The basic workflow is:

```text
Live Tracking
      |
      v
Select Layout
      |
      v
Select Vehicle(s)
      |
      v
Configure Trail
      |
      v
Start Tracking
      |
      v
Vehicle Marker + Live Route
      |
      v
Position Updates
```

The current test suite treats successful live tracking and live position updates as Critical scenarios.

---

# 6. Split Screen

The Live Tracking form includes a **Split Screen** setting.

The current tests verify:

- Default Split Screen value.
- Opening the Split Screen dropdown.
- Available options.
- Selecting an available option.
- Applying the corresponding layout behaviour.
- Starting live tracking with a custom Split Screen configuration.

The exact number and names of available Split Screen options should be taken from the live product; the uploaded test specification does not define their names.

---

# 7. Vehicle Selection in Live Tracking

Vehicle selection is one of the most important parts of Live Tracking.

```text
Select Vehicle
      |
      v
Available Vehicles
      |
      +--> Select Vehicle A
      |
      +--> Select Vehicle B
      |
      +--> Select Vehicle C
      |
      v
Selected Vehicles Counter
      |
      v
Start Tracking
```

The current test cases cover:

- Opening the vehicle dropdown.
- Selecting one vehicle.
- Selecting multiple vehicles.
- Selecting the maximum supported number.
- Attempting to exceed the supported limit.
- Deselecting a vehicle.
- Preventing duplicate vehicle selection.
- Handling an empty vehicle list.
- Handling vehicle-list API failure.

The counter should match the actual number of selected vehicles.

---

# 8. Why Vehicle Selection Matters

The selected vehicle list determines what is displayed on the map.

```text
Vehicle A ──> Marker A + Trail A
Vehicle B ──> Marker B + Trail B
Vehicle C ──> Marker C + Trail C
```

The system must keep each marker and trail correctly associated with its vehicle.

The test suite specifically checks simultaneous updates for multiple vehicles.

---

# 9. Trail Color

Live Tracking provides a **Trail Color** setting.

```text
Open Trail Color
      |
      v
Select Color
      |
      v
Start Tracking
      |
      v
Live Vehicle Trail
```

The test suite checks both the selected UI value and the resulting map route.

---

# 10. Trail Thickness

Live Tracking also provides **Trail Thickness**.

The current tests cover:

- Increasing thickness.
- Decreasing thickness.
- Minimum supported value.
- Maximum supported value.

The selected thickness should be reflected in the displayed route.

---

# 11. Reset in Live Tracking

The Live Tracking form has a **Reset** action.

### Reset after modifications

```text
Change Vehicle
Change Trail Color
Change Thickness
       |
       v
     Reset
       |
       v
All resettable values → Defaults
```

The test suite also verifies Reset when no values were changed.

---

# 12. Starting Live Tracking

### Invalid workflow

```text
No vehicle selected
       |
       v
Start Tracking
       |
       v
Validation / Feedback
       |
       X
Tracking must not start
```

### Valid workflow

```text
Select vehicle
      |
      v
Start Tracking
      |
      v
Tracking starts
      |
      v
Selected vehicle appears on map
```

### Multiple vehicles

```text
Select A + B + C
       |
       v
Start Tracking
       |
       v
A + B + C tracked correctly
```

These are Critical scenarios in the current test suite.

---

# 13. Live Position Updates

Live Tracking is not a static map.

```text
Initial Position
      |
      v
New Tracking Data
      |
      v
Marker Updates
      |
      v
New Tracking Data
      |
      v
Marker Updates Again
```

The current tests verify:

- Vehicle position updates.
- Route/trail rendering for moving vehicles.
- No-data behaviour when a vehicle has no current location.
- Correct association when multiple vehicles update simultaneously.

---

# 14. Live Tracking Failure Scenarios

### Live Tracking API failure

```text
Start Tracking
      |
      v
API Failure
      |
      v
Error State
      |
      X
Do not show false "tracking started" state
```

### Network disconnect

```text
Live Tracking
      |
      v
Network Disconnect
      |
      v
Stale/unavailable updates handled
      |
      v
Failure/recovery feedback
```

### Network reconnect

```text
Network Failure
      |
      v
Reconnect
      |
      v
Retry / Recovery
      |
      v
Tracking resumes according to product behaviour
```

Rapid Start Tracking clicks must also not create duplicate tracking requests/sessions.

---

# 15. Playback Tracking

**Playback Tracking** is used to inspect historical movement.

It answers:

> Where did the vehicle move during a selected historical period?

The workflow is:

```text
Playback
   |
   v
Select Vehicle
   |
   v
Select From Date
   |
   v
Select To Date
   |
   v
Select From Time
   |
   v
Select To Time
   |
   v
Optional Filters
   |
   v
Load Playback
   |
   v
Historical Route on Map
```

The test suite treats valid same-day and multi-day playback as Critical workflows.

---

# 16. Playback Vehicle Selection

Playback requires a vehicle.

The current tests cover:

- Opening the Playback vehicle dropdown.
- Selecting a valid vehicle.
- Attempting to load playback without selecting a vehicle.
- No vehicles available.

```text
No Vehicle
    |
    v
Load Playback
    |
    v
Validation
    |
    X
Playback not loaded
```

---

# 17. Playback Date Range

Playback uses:

```text
From Date
    |
    v
To Date
```

The test suite covers:

- Valid same-day range.
- Valid multi-day range.
- From Date later than To Date.
- To Date earlier than From Date.
- Today's date.
- Future dates.
- Dates outside available tracking history.

Example invalid range:

```text
From Date = 10 Sep
To Date   = 05 Sep
        |
        v
Invalid Date Range
```

The application should reject the range or display appropriate validation.

---

# 18. Playback Time Range

Playback also supports:

```text
From Time
    |
    v
To Time
```

The current tests cover:

- Valid same-day time range.
- From Time later than To Time.
- Equal From/To Time.
- 00:00.
- End-of-day boundary.
- Different dates with valid times.

For the same date:

```text
From = 10:00
To   = 18:00
```

is chronological.

An inverted range such as 18:00 → 10:00 should be rejected or validated according to product behaviour.

---

# 19. Cross-Day Playback

Playback can cover different dates.

Example:

```text
From:
01 Sep 2026 20:00

To:
02 Sep 2026 06:00
```

The current test suite expects valid cross-day ranges to be accepted.

---

# 20. Hold Time Filter

Playback contains a **Hold Time** filter.

The current tests cover:

- Opening Hold Time dropdown.
- Selecting an option.
- Minimum Hold Time.
- Maximum Hold Time.
- Loading playback with the selected Hold Time.

The exact available Hold Time values are not defined in the uploaded test specification and should be verified from the live application.

---

# 21. Overspeeding Filter

Playback also includes an **Overspeeding** filter.

The test suite covers:

- Opening the Overspeeding dropdown.
- Selecting a threshold.
- Minimum threshold.
- Maximum threshold.
- Loading playback using the selected threshold.

```text
Overspeeding Threshold
          |
          v
      Load Playback
          |
          v
Playback respects threshold
```

The uploaded test source does not define the actual threshold values.

---

# 22. More Filters

Playback contains a **More Filters** control.

The current tests verify:

- Opening More Filters.
- Closing More Filters.
- Applying one additional filter.
- Applying multiple additional filters.
- Preserving unrelated state when closing the panel.

This follows a progressive-disclosure pattern:

```text
Basic Playback Form
        |
        v
More Filters
        |
        v
Additional options
```

---

# 23. Playback Trail Color and Thickness

Playback has its own visual route configuration.

It includes:

- Trail Color.
- Trail Thickness.

The tests verify:

```text
Change Color
     ↓
Load Playback
     ↓
Historical route uses selected color
```

and:

```text
Change Thickness
     ↓
Load Playback
     ↓
Historical route uses selected thickness
```

Minimum and maximum thickness values are also tested.

---

# 24. Load Playback

Load Playback requests historical tracking data.

```text
Vehicle
   +
Date Range
   +
Time Range
   +
Optional Filters
   |
   v
Load Playback
   |
   v
Request Processing
   |
   v
Historical Route
```

If required fields are missing, validation should appear and playback should not load.

With valid inputs:

```text
Valid Vehicle
Valid Date/Time Range
      |
      v
Load Playback
      |
      v
Historical route displayed
```

---

# 25. Playback Loading State

During processing:

- Load button indicates processing.
- Duplicate requests are prevented.

```text
Click Load Playback
       |
       v
Loading...
       |
       +--> Processing feedback
       |
       X
No duplicate requests
```

---

# 26. Playback API and Network Failures

### API failure

```text
Load Playback
      |
      v
API Failure
      |
      v
Error state
      |
      X
No false playback result
```

### Network disconnect

```text
Loading Playback
      |
      v
Network Disconnect
      |
      v
Loading terminates safely
      |
      v
Error / Retry state
```

### Recovery

```text
Network reconnect
      |
      v
Retry
      |
      v
Playback loads successfully
```

---

# 27. No Tracking Data

A valid request does not necessarily mean tracking data exists.

```text
Valid Vehicle
+
Valid Date Range
+
Valid Time Range
        |
        v
No historical tracking data
        |
        v
Clear "No Data" state
```

The application should not silently show an unexplained empty map.

---

# 28. Large Playback Range

The test suite includes requesting a large playback range.

The application should handle large result data without UI failure.

QA should check:

- UI responsiveness.
- Map stability.
- No browser crash.
- No broken controls.
- Correct loading state.
- No duplicate requests.
- Appropriate handling of large datasets.

The test source does not define a precise maximum date range.

---

# 29. Map

The map is the central visualization layer.

The current tests cover:

- Map rendering.
- Zoom in/out.
- Pan.
- Live vehicle markers.
- Live routes.
- Playback routes.
- Trail color.
- Trail thickness.
- Invalid coordinates.
- Overlapping vehicle routes.
- Map service/network failure.

---

# 30. Live Map vs Playback Map

### Live Map

```text
Selected Vehicle
      |
      v
Latest Position
      |
      v
Live Marker
      |
      v
Current / received route trail
```

### Playback Map

```text
Vehicle
   +
Historical Time Range
   |
   v
Historical Tracking Data
   |
   v
Playback Route
```

The map should clearly reflect the active tracking mode.

---

# 31. Map Controls

The current test suite checks:

### Zoom

```text
Zoom In  → Map scale increases
Zoom Out → Map scale decreases
```

### Pan

```text
Drag/Pan Map
      |
      v
Map position changes
```

Panning must not corrupt the Tracking form state.

---

# 32. Invalid Coordinates

If vehicle coordinates are unavailable or invalid:

```text
Invalid Coordinates
       |
       v
Do NOT render marker at invalid location
       |
       v
Keep UI stable
```

This prevents incorrect map positioning or rendering failures.

---

# 33. Multiple Overlapping Routes

When multiple vehicles share the same route:

```text
Vehicle A ────────┐
                  ├── Same area
Vehicle B ────────┘
```

The application must keep each marker and route correctly associated with its vehicle.

---

# 34. Live vs Playback State

Live Tracking and Playback should maintain separate state.

Example:

```text
Live Tracking
Vehicle = A
Color = Blue
Thickness = 5

        ↓ Switch to Playback

Playback
Vehicle = B
Date = Historical Date
Color = Red
Thickness = 3
```

Playback should not unexpectedly inherit unrelated Live values, and Live should not be contaminated by Playback state.

The current test suite explicitly covers both directions.

---

# 35. Preset Changes While Tracking

The Tracking UI allows preset/layout changes while Live Tracking or Playback is active.

The application must handle this without:

- Duplicate panels.
- Broken maps.
- Duplicate controls.
- Corrupted state.

The current tests cover changing presets while both modes are active.

---

# 36. Refresh and Browser Navigation

Tracking must initialize correctly after:

### Refresh

```text
Tracking
   |
Refresh
   |
Tracking initializes correctly
```

### Browser Back/Forward

```text
Tracking
   |
Other Page
   |
Back
   |
Tracking initializes correctly
```

The page should not retain corrupted state.

---

# 37. Authentication Handling

Tracking depends on authenticated API requests.

The current tests explicitly cover session expiry during:

- Live Tracking.
- Playback loading.

Expected behaviour:

```text
Session expires
      |
      v
Protected request fails
      |
      v
Authentication flow
```

The application should not continue protected requests incorrectly or display misleading results.

---

# 38. API Concurrency — Critical QA Concept

One of the most important advanced scenarios is **multiple tracking requests completing out of order**.

Example:

```text
User selects Vehicle A
      |
      +--> Request A --------------------> Response A

User quickly selects Vehicle B
      |
      +--> Request B -------> Response B
```

If Response B arrives first:

```text
Response B
   ↓
Display Vehicle B
```

A late Response A must NOT overwrite the latest state:

```text
Late Response A
      |
      X
Must not overwrite Vehicle B
```

Expected principle:

> **The latest valid user state must not be overwritten by stale API responses.**

The current test suite marks this concurrency scenario as **Critical**.

---

# 39. Complete Tracking Workflow

```text
                         TRACKING
                            |
                +-----------+-----------+
                |                       |
              LIVE                   PLAYBACK
                |                       |
         Select Vehicle(s)          Select Vehicle
                |                       |
         Split Screen              From Date
                |                       |
         Trail Color               To Date
                |                       |
       Trail Thickness             From Time
                |                       |
                |                   To Time
                |                       |
                |              Hold Time / Overspeeding
                |                  / More Filters
                |                       |
                +-----------+-----------+
                            |
                       Load / Start
                            |
                            v
                           MAP
                            |
             +--------------+--------------+
             |                             |
         Live Marker                 Playback Route
             |                             |
         Live Trail                 Historical Route
```

---

# 40. QA Testing Model

For every Tracking feature, test six layers.

## Layer 1 — UI

Does the control appear and behave correctly?

```text
Dropdown
Button
Slider
Date Picker
Map
Tab
Preset
```

## Layer 2 — Validation

Does invalid input get rejected?

```text
No Vehicle
Invalid Date Range
Invalid Time Range
Unsupported Selection
```

## Layer 3 — Functional Result

Does the actual map/result reflect the selection?

```text
Selected Vehicle → Correct Marker
Selected Color   → Correct Trail
Selected Range   → Correct Playback
```

## Layer 4 — State

Does switching between modes preserve the correct state?

```text
Live ↔ Playback
Preset changes
Refresh
Back/Forward
```

## Layer 5 — Reliability

What happens when things fail?

```text
API Failure
Network Failure
Session Expiry
No Data
Invalid Coordinates
Large Dataset
```

## Layer 6 — Concurrency

What happens when requests complete unexpectedly?

```text
Request A
Request B
     ↓
B response
     ↓
A response
```

The latest state must not be overwritten by stale data.

---

# 41. High-Priority Tracking Test Areas

Based on the uploaded Tracking automation test specification:

| Priority | Area | Why |
|---|---|---|
| Critical | Map initial rendering | Tracking depends on the map |
| Critical | Vehicle selection | Core tracking input |
| Critical | Start Live Tracking | Core feature |
| Critical | Live vehicle position updates | Core live functionality |
| Critical | Multiple vehicle tracking | Core multi-unit functionality |
| Critical | Live Tracking API failure | Prevent false tracking state |
| Critical | Network failure during live tracking | Reliability |
| Critical | Playback required-field validation | Data integrity |
| Critical | Valid same-day playback | Core playback |
| Critical | Valid multi-day playback | Core playback |
| Critical | Playback API failure | Prevent false result |
| Critical | Playback map rendering | Core visualization |
| Critical | API concurrency | Prevent stale data overwriting latest state |

The uploaded suite also contains High and Medium coverage for boundaries, filters, reset, layout, responsive behaviour, and recovery.

---

# 42. Relationship Between Unit and Tracking

The Unit and Tracking modules are closely related:

```text
                 UNIT
                  |
        Unit configuration
                  |
                  v
              TRACKING
                  |
        Vehicle selection
                  |
                  v
               MAP
                  |
          Live / Historical
                  |
                  v
              REPORTS
```

For QA, remember that the exact behaviour should be verified against the live product and the relevant module specifications.

---

# 43. Practical QA Checklist

### Page

- Does Tracking open?
- Does the map load?
- Are controls visible?
- Does the page handle initial API failure?

### Live Tracking

- Can I select a vehicle?
- Can I select multiple vehicles?
- Is the counter correct?
- Can I deselect?
- Are duplicates prevented?
- Is the maximum selection enforced?
- Does Start Tracking work?
- Does the marker represent the selected vehicle?
- Does the marker update?
- Does the trail render?
- Does trail color work?
- Does trail thickness work?

### Playback

- Can I select a vehicle?
- Can I select valid dates?
- Can I select valid times?
- Are invalid date/time ranges rejected?
- Do Hold Time and Overspeeding filters work?
- Do More Filters work?
- Does Reset work?
- Does Load Playback work?
- Does the historical route render?

### Map

- Does zoom work?
- Does pan work?
- Are invalid coordinates handled?
- Are multiple routes correctly associated?
- Does the map survive service/network failure?

### State

- Live → Playback?
- Playback → Live?
- Preset switching?
- Refresh?
- Browser back/forward?

### Reliability

- API failure?
- Network disconnect?
- Network reconnect?
- Session expiry?
- Rapid clicks?
- Out-of-order API responses?
- No tracking data?
- Large playback range?

---

# 44. Final Summary

The Trackofy Tracking module is fundamentally a **map-based vehicle monitoring and historical movement analysis module**.

Its two major modes are:

```text
LIVE TRACKING
     ↓
Monitor current/latest vehicle positions

PLAYBACK TRACKING
     ↓
Inspect historical vehicle movement
```

The core relationship is:

```text
Vehicle Selection
       +
Tracking Data
       +
Map
       +
Configuration
       ↓
Live or Historical Tracking
```

> **Live Tracking answers "Where is the vehicle now?" while Playback answers "Where did the vehicle move during this selected period?"**

From a QA perspective, don't stop after verifying that a map appears. The real depth comes from verifying:

**user selection → API request → returned data → map visualization → state changes → failure handling**

The uploaded Tracking automation suite contains coverage for these layers, including Critical scenarios around live updates, playback, map rendering, network/API failures, and stale-response/concurrency handling.

## Source Basis

This guide is based on the uploaded `tracking_module_automation_test_cases.xlsx` / CSV test specification and the uploaded Trackofy UI source. The exact names/values of controls that are not defined in those sources should be verified against the live application rather than assumed.
