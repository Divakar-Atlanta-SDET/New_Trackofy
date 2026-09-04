# Trackofy Home Module --- Functional & QA Explanation

## 1. Overview

The **Home module** is the primary operational monitoring workspace of
Trackofy. It brings together live vehicle visibility,
vehicle/group/driver navigation, KPI-based status filtering, map
visualization, alerts and notifications, driver information, vehicle
assignment, GeoLinks, and contextual vehicle actions.

The Home module should be understood as a **stateful, real-time fleet
monitoring system**, not merely a collection of UI cards.

Its core workflow is:

``` text
Fleet Data
    ↓
Home
    ↓
Filter / Search / Select
    ↓
Vehicle / Group / Driver Context
    ↓
Map / Details / Action
    ↓
Backend Operation
    ↓
Updated UI State
```

------------------------------------------------------------------------

## 2. Home Module Functional Areas

``` text
Home
│
├── KPI Cards
│   └── KPI Settings
│
├── View Presets
│
├── Search
│
├── Side Panel
│   ├── Fleet
│   ├── Groups
│   └── Drivers
│
├── Fleet Vehicle Cards
│   ├── Status Filters
│   ├── Current Location
│   ├── Signal Strength
│   ├── Unit Commands
│   └── More Actions
│
├── Group View
│   └── Group-specific Status Filters
│
├── Driver View
│   ├── Driver Details
│   ├── Call Driver
│   ├── Licence
│   └── Vehicle Assignment
│
├── Map
│   ├── Map / Hybrid
│   └── Map Toolbar
│
├── Contextual Right-side Views
│   ├── Playback
│   ├── POI
│   ├── Alert
│   ├── Unit Maintenance
│   └── Unit Insights
│
├── Alerts & Notifications
│   ├── Alerts
│   ├── Acknowledged
│   ├── View All Alerts
│   └── Live
│
└── GeoLinks
    ├── GeoLink List
    └── Create GeoLink
```

------------------------------------------------------------------------

# 3. Home Screen Layout

The Home screen is divided into several functional regions.

``` text
┌─────────────────────────────────────────────────────────────┐
│                       KPI AREA                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Search / Side Panel          Map / Live Fleet             │
│                                                             │
│  ┌───────────────────┐       ┌───────────────────────────┐ │
│  │ Fleet             │       │                           │ │
│  │ Groups            │       │            MAP            │ │
│  │ Drivers           │       │                           │ │
│  │                   │       │                           │ │
│  │ Vehicle / Group / │       │                           │ │
│  │ Driver Cards      │       │                           │ │
│  └───────────────────┘       └───────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                  VIEW PRESETS / CONTROLS                    │
└─────────────────────────────────────────────────────────────┘
```

The exact visual arrangement changes according to the selected view
preset.

------------------------------------------------------------------------

# 4. View Presets

The Home module provides multiple view presets through controls at the
bottom-left area.

These presets change how much space is occupied by the side menu versus
the map.

Conceptually:

``` text
View Presets
│
├── Expanded / 3-column style
├── Medium / 2-column style
└── Compact / 1-column style
```

The purpose is to allow the user to control the amount of fleet
information visible while maintaining access to the map.

### QA checks

Verify:

-   Every available preset can be selected.
-   The selected preset is visually identifiable.
-   Vehicle cards remain usable.
-   Map remains usable.
-   Controls do not overlap.
-   Switching presets repeatedly does not corrupt the layout.
-   Opening/closing panels does not unexpectedly change the selected
    preset.
-   Layout works at different viewport sizes.

------------------------------------------------------------------------

# 5. KPI Cards

KPI cards provide a high-level summary of fleet status.

The provided Home screen shows KPIs including:

``` text
Total Vehicles
Running
Idle
Stopped
No Data
BMS Enabled
Video Enabled
Expired Devices
Critical Alerts
Active Trips
```

KPIs have two primary purposes:

1.  Display a fleet-level count.
2.  Allow quick filtering by the corresponding category where supported.

Example:

``` text
Running KPI
    ↓
Running filter
    ↓
Running vehicles shown
```

The same concept applies to Idle, Stopped, No Data, and other supported
KPI categories.

------------------------------------------------------------------------

# 6. KPI Settings

The KPI header is configurable.

The **KPI Settings** dialog provides:

-   Select All.
-   Individual KPI checkboxes.
-   Save.
-   Cancel.
-   Minimum selection validation.

The provided screen explicitly shows:

``` text
Select at least 6 KPIs.
Currently selected: 10
```

Therefore, the visible implementation establishes a minimum of **6
selected KPIs**.

## KPI configuration flow

``` text
Open KPI Settings
        ↓
View available KPIs
        ↓
Select / Unselect KPIs
        ↓
Validate minimum selection
        ↓
Save
        ↓
Header updates
```

### Select All

Verify:

``` text
Select All
    ↓
All available KPIs selected
```

No KPI should remain visually or logically inconsistent with the Select
All state.

### Individual selection

Verify:

-   Selecting a KPI adds it to the header.
-   Unselecting a KPI removes it.
-   The count of selected KPIs is correct.
-   The checkbox state and header state remain synchronized.

### Minimum KPI validation

``` text
Selected KPIs < 6
        ↓
Save
        ↓
Validation message
        ↓
Invalid configuration rejected
```

### Cancel

``` text
Modify KPI configuration
        ↓
Cancel
        ↓
Changes discarded
```

### Save

``` text
Valid configuration
        ↓
Save
        ↓
Dialog closes
        ↓
New KPI configuration visible
```

------------------------------------------------------------------------

# 7. KPI and Header Layout Interaction

KPI configuration dynamically changes the Home header.

This creates an important layout-risk area.

For example:

``` text
Many KPIs
────────────────────────────────────
KPI  KPI  KPI  KPI  KPI     Settings
```

After removing KPIs:

``` text
Few KPIs
────────────────────
KPI  KPI             Settings
```

The remaining controls must reposition correctly.

### QA risks

Test for:

-   Settings icon movement.
-   Overlapping KPI cards.
-   Hidden settings icon.
-   Incorrect spacing.
-   Broken alignment.
-   Horizontal overflow.
-   Incorrect responsive behaviour.
-   KPI cards becoming inaccessible after reducing the number of KPIs.

------------------------------------------------------------------------

# 8. Fleet / Groups / Drivers

The Home side panel contains three sub-tabs:

``` text
Fleet
Groups
Drivers
```

Each provides a different perspective:

``` text
Fleet
  ↓
Vehicle-centric

Groups
  ↓
Group-centric

Drivers
  ↓
Driver-centric
```

------------------------------------------------------------------------

# 9. Fleet Sub-tab

The Fleet tab displays vehicles individually.

``` text
Fleet
│
├── Vehicle A
├── Vehicle B
├── Vehicle C
└── Vehicle D
```

Each vehicle appears as a card containing vehicle information and
actions.

------------------------------------------------------------------------

# 10. Fleet Status Filters

The Fleet view provides status/capability filters including:

``` text
Active
Running
Idle
Stopped
No Data
BMS
Video
```

The expected filtering model is:

``` text
Select category
      ↓
Filter fleet
      ↓
Display matching vehicles
```

For example:

``` text
Running
   ↓
Only running vehicles
```

### QA checks

For every filter verify:

-   Correct vehicles are displayed.
-   Vehicles outside the category are excluded.
-   Filter count is correct.
-   Empty result is handled correctly.
-   Switching filters updates the list.
-   Search and filters work together.
-   Map state is consistent with the filtered list where applicable.

------------------------------------------------------------------------

# 11. Vehicle Cards

Each Fleet vehicle is represented as a card.

A vehicle card can expose:

``` text
Vehicle information
Current location
Signal strength
Unit commands
More actions
```

The card is therefore a central interaction point.

------------------------------------------------------------------------

# 12. Current Location

The vehicle card provides access to the vehicle's current location.

Expected conceptual flow:

``` text
Vehicle Card
     ↓
Current Location
     ↓
Map focuses on selected vehicle
```

QA should verify:

-   Correct vehicle is selected.
-   Map focuses on the correct vehicle.
-   Correct marker is displayed.
-   Location is not associated with another vehicle.
-   Repeated vehicle selection updates the map correctly.

------------------------------------------------------------------------

# 13. Signal Strength

Vehicle cards expose signal/connectivity information.

Conceptually:

``` text
Tracking Unit
      ↓
Communication
      ↓
Signal Strength
```

Test:

-   Strong signal.
-   Weak signal.
-   No signal.
-   Signal changes.
-   Correct icon/state.
-   Tooltip/details where available.

The displayed signal state should correspond to the underlying unit
state.

------------------------------------------------------------------------

# 14. Unit Commands

Vehicle cards expose Unit Commands.

The **Arm** command has been identified as a dangerous/operationally
sensitive command.

This makes Unit Commands a high-risk area.

## Safe command workflow

``` text
Select Vehicle
      ↓
Open Unit Commands
      ↓
Select Command
      ↓
Confirmation / Safety Check
      ↓
Confirm
      ↓
Command sent
      ↓
Success / Failure feedback
```

### Critical QA scenarios

Test:

-   Correct vehicle selected.
-   Correct command selected.
-   Confirmation behaviour.
-   Cancel command.
-   Double-click / duplicate submission.
-   Network failure.
-   Device unavailable.
-   Timeout.
-   Unauthorized user.
-   Incorrect/stale vehicle context.
-   Success feedback.
-   Failure feedback.

The most important rule is:

> A dangerous command must never be executed against a different vehicle
> because of stale selection or a UI race condition.

------------------------------------------------------------------------

# 15. Vehicle Three-dot Menu

The vehicle card's three-dot menu exposes additional actions:

``` text
Playback
POI
Alert
Unit Maintenance
Unit Insights
```

Conceptually:

``` text
Vehicle Card
    ↓
    ⋮
    │
    ├── Playback
    ├── POI
    ├── Alert
    ├── Unit Maintenance
    └── Unit Insights
```

These actions can open contextual information on the right side of the
Home screen.

------------------------------------------------------------------------

# 16. Playback

Playback is used for historical movement review.

``` text
Vehicle
   ↓
Historical movement
   ↓
Playback
   ↓
Map visualization
```

Test:

-   Correct vehicle context.
-   Correct date/time.
-   Playback controls.
-   Map synchronization.
-   Start/pause/stop behaviour where supported.
-   Closing playback.
-   Returning to live tracking.
-   Switching vehicles during/after playback.

A historical playback context must not accidentally overwrite the live
vehicle context.

------------------------------------------------------------------------

# 17. POI

POI refers to Points of Interest.

The POI action operates within the selected vehicle/map context.

QA should verify:

-   Correct vehicle context.
-   Correct POI information.
-   Map behaviour.
-   Opening/closing.
-   No stale POI context.
-   Switching vehicles correctly changes context.

------------------------------------------------------------------------

# 18. Vehicle Alert

The vehicle-level Alert action provides alert information associated
with the selected vehicle.

``` text
Vehicle A
   ↓
Alert
   ↓
Vehicle A alerts
```

The alert view must not accidentally display alerts belonging to another
selected vehicle.

------------------------------------------------------------------------

# 19. Unit Maintenance

Unit Maintenance provides maintenance-related information/actions for
the selected unit.

Verify:

-   Correct vehicle/unit.
-   Correct maintenance context.
-   Permissions.
-   Save/update operations where applicable.
-   API failure handling.
-   No stale selected-unit information.

------------------------------------------------------------------------

# 20. Unit Insights

Unit Insights provides additional information/analysis for the selected
unit.

The key QA requirement is context preservation:

``` text
Vehicle A selected
      ↓
Unit Insights
      ↓
Insights for Vehicle A
```

A previous Vehicle B selection must never leak into the panel.

------------------------------------------------------------------------

# 21. Groups Sub-tab

The Groups tab categorizes vehicles by group.

Example structure from the supplied screen:

``` text
Default
Delhi
Bhopal
Dwarka
```

Conceptually:

``` text
Groups
│
├── Delhi
│   ├── Vehicle 1
│   ├── Vehicle 2
│   └── Vehicle 3
│
├── Bhopal
│   ├── Vehicle 4
│   └── Vehicle 5
│
└── Dwarka
    └── Vehicle 6
```

Each group displays a vehicle count and status information.

------------------------------------------------------------------------

# 22. Group Status Filters

Each group can expose status filters.

The supplied screen shows:

``` text
Active
Running
Idle
Stopped
```

and the Home functionality also includes No Data as a relevant category.

The filtering model is hierarchical:

``` text
Group
  ↓
Status
  ↓
Matching vehicles
```

Example:

``` text
Delhi
 +
Idle
 ↓
Idle vehicles belonging to Delhi
```

A vehicle from another group must not appear simply because it has the
same status.

------------------------------------------------------------------------

# 23. Group Expand / Collapse

Groups can be expanded or collapsed.

``` text
Group
 ↓
Expand
 ↓
Group contents
```

and:

``` text
Group
 ↓
Collapse
 ↓
Summary view
```

Test:

-   Correct group expands.
-   Correct group collapses.
-   Vehicle count remains correct.
-   Status counts remain correct.
-   Group-specific filters remain associated with that group.
-   Rapid expand/collapse does not create duplicate content.
-   Switching tabs does not corrupt group state.

------------------------------------------------------------------------

# 24. Drivers Sub-tab

The Drivers tab provides a driver-centric view.

The supplied screens show information such as:

``` text
Driver name
Mobile number
Assigned vehicle
Driving licence number
Address
Licence status
Licence expiry
Vehicle assignment
```

Conceptually:

``` text
Driver
│
├── Personal information
├── Contact information
├── Licence
└── Assigned vehicle
```

------------------------------------------------------------------------

# 25. Driver Card

Each driver is displayed using a card.

The card can expose:

``` text
Call
More actions
Driver details
Vehicle assignment
```

The screenshot also shows licence status, including an **Expired**
state.

------------------------------------------------------------------------

# 26. Call Driver

The driver card provides a call action.

``` text
Driver Card
     ↓
Call
     ↓
Calling action
```

QA should verify:

-   Correct driver's phone number.
-   Correct driver context.
-   Missing phone number handling.
-   Invalid number handling.
-   Permission behaviour.
-   No wrong-driver call due to stale card context.

------------------------------------------------------------------------

# 27. Driver Licence

Driver details include a **View Licence Copy** button.

``` text
Driver
  ↓
Driving Licence
  ↓
View Licence Copy
  ↓
Licence document/image
```

QA should verify:

-   Correct driver's licence is opened.
-   Licence belongs to selected driver.
-   Licence number is correct.
-   Issue date is correct.
-   Expiry date is correct.
-   Expired status is correct.
-   Missing licence copy is handled.
-   Broken/unavailable document is handled.
-   Viewer can be closed safely.

------------------------------------------------------------------------

# 28. Driver Details

The three-dot menu provides additional driver actions.

The identified functionality includes:

``` text
View Driver Details
Assign Vehicle
```

Driver details can contain:

``` text
Date of Birth
Mobile
Address
Driving Licence
Vehicle Assignment
```

The supplied screen shows:

``` text
Licence Number
Issued
Expires
View Licence Copy
```

and:

``` text
Vehicle Assignment
Assigned
Change
```

------------------------------------------------------------------------

# 29. Vehicle Assignment

Vehicle assignment is a multi-step workflow.

The described implementation requires an existing vehicle to be
unassigned before assigning a new vehicle.

The flow is:

``` text
Driver
   ↓
Assign Vehicle
   ↓
Existing assignment?
   │
   ├── Yes
   │    ↓
   │  Unassign current vehicle
   │    ↓
   │  Reopen Assign Vehicle dialog
   │
   └── No
        ↓
     Assign Vehicle dialog
        ↓
   Select vehicle
        ↓
      Submit
        ↓
   Assignment saved
```

------------------------------------------------------------------------

# 30. Vehicle Assignment --- Detailed Steps

### Step 1 --- Open assignment

``` text
Driver
  ↓
⋮
  ↓
Assign Vehicle
```

### Step 2 --- Unassign current vehicle

If the driver already has a vehicle:

``` text
Current Vehicle
      ↓
Unassign
```

### Step 3 --- Reopen assignment dialog

``` text
Assign Vehicle
      ↓
Vehicle dropdown
```

### Step 4 --- Select a vehicle

``` text
Vehicle dropdown
      ↓
Available vehicles
      ↓
Select vehicle
```

### Step 5 --- Submit

``` text
Selected vehicle
      ↓
Submit
      ↓
Assignment saved
```

### Step 6 --- Verify

The driver should show the newly assigned vehicle.

------------------------------------------------------------------------

# 31. Vehicle Assignment QA Scenarios

Test:

-   Driver with no vehicle → assign.
-   Driver with current vehicle → unassign.
-   Reopen dialog after unassignment.
-   Dropdown shows eligible vehicles.
-   Select vehicle.
-   Submit.
-   Cancel.
-   Submit without selection.
-   No available vehicles.
-   Vehicle already assigned.
-   Network failure.
-   Duplicate submit.
-   Refresh after assignment.
-   Assignment persists after reopening Home.
-   Driver and vehicle views remain consistent.

This is a high-risk relationship because the operation changes:

``` text
Driver ↔ Vehicle
```

------------------------------------------------------------------------

# 32. Map

The map is the central geographical visualization area.

The supplied screen shows:

``` text
Map
Hybrid
```

The map represents tracked vehicles and supports additional map
controls.

------------------------------------------------------------------------

# 33. Map / Hybrid Mode

Users can switch between:

``` text
Map
  ↕
Hybrid
```

QA should verify:

-   Correct mode is selected.
-   Vehicle markers remain visible.
-   Vehicle positions remain consistent.
-   Map controls remain usable.
-   Switching repeatedly does not break rendering.
-   Selected vehicle remains selected.

------------------------------------------------------------------------

# 34. Map Toolbar

The supplied screens show a vertical map toolbar containing controls for
different map/vehicle functions.

The visible icons include functions associated with:

``` text
Layers
Vehicles
Route / movement
POI
Alerts
Playback / tracking
Other map controls
```

The exact business meaning of individual icons should be verified
against the live implementation because icon appearance alone does not
establish its exact function.

QA should nevertheless verify:

-   Every control opens the correct function.
-   Correct panel appears.
-   Correct vehicle context is maintained.
-   Closing the panel returns the user to the correct map state.

------------------------------------------------------------------------

# 35. Search

The side panel provides a search box.

The search should operate against the currently selected entity type.

``` text
Fleet tab
   ↓
Vehicle search

Groups tab
   ↓
Group search

Drivers tab
   ↓
Driver search
```

Test:

-   Exact match.
-   Partial match.
-   Case variation.
-   Numeric identifiers.
-   No-result state.
-   Clear search.
-   Special characters.
-   Search after changing tabs.

------------------------------------------------------------------------

# 36. Search + Filter

Search and filters should work together.

Example:

``` text
Status = Running
+
Search = ABC
        ↓
Running vehicles matching ABC
```

Test combinations:

``` text
Search + Active
Search + Running
Search + Idle
Search + Stopped
Search + No Data
```

The result should satisfy **both** conditions.

------------------------------------------------------------------------

# 37. Alerts & Notifications

The Home screen contains an Alerts & Notifications panel.

The supplied screen shows:

``` text
Alerts & Notifications
Recent notifications from today

Alerts (20)
Acknowledged (0)
```

Each alert card can show:

``` text
Alert title
Alert source/type
Severity
Description
Timestamp
Data source/tag
Acknowledge
View
```

------------------------------------------------------------------------

# 38. Alert Card

The supplied example is similar to:

``` text
┌─────────────────────────────────────────┐
│ Odometer Service Alert          Warning │
│ service                                  │
│ Vehicle service alert generated...       │
│                                          │
│ 12:20 pm • 15 min ago • GPS             │
│                              ✓       👁  │
└─────────────────────────────────────────┘
```

The important actions are:

``` text
Acknowledge
View
```

------------------------------------------------------------------------

# 39. Acknowledge Alert

The acknowledgement workflow is:

``` text
Active Alert
     ↓
Acknowledge
     ↓
Alert state changes
     ↓
Acknowledged tab
```

The important requirement is that acknowledgement changes the alert's
state.

QA should verify:

-   Alert is acknowledged.
-   Active list updates.
-   Acknowledged list updates.
-   Counts update.
-   Alert information remains intact.
-   Refresh preserves the state.
-   Duplicate acknowledgement is handled safely.

------------------------------------------------------------------------

# 40. Acknowledged Tab

The Acknowledged tab contains acknowledged alerts.

Expected model:

``` text
New Alert
   ↓
Alerts
   ↓
Acknowledge
   ↓
Acknowledged
```

Test:

-   Alert moves to correct tab.
-   Active count changes.
-   Acknowledged count changes.
-   Alert remains viewable.
-   Reopening the panel preserves state.
-   Refresh does not incorrectly restore the alert to active state.

------------------------------------------------------------------------

# 41. View Alert

The View action opens additional information for the selected alert.

``` text
Alert Card
    ↓
View
    ↓
Alert details
```

Verify:

-   Correct alert.
-   Correct vehicle.
-   Correct timestamp.
-   Correct alert type.
-   Correct description.
-   Correct map context where applicable.

------------------------------------------------------------------------

# 42. View All Alerts

The bottom of the Alerts panel provides:

``` text
View all alerts
```

This should navigate to the broader alert history/list.

``` text
Home Alerts
    ↓
View all alerts
    ↓
Complete alert view
```

The navigation should not lose the relevant alert context unexpectedly.

------------------------------------------------------------------------

# 43. Live Alerts

The bottom of the panel also provides:

``` text
Live
```

Live mode is intended for real-time alert monitoring.

``` text
Live mode
    ↓
New alert generated
    ↓
Alert appears
```

Test:

-   New alerts appear without unnecessary manual refresh where
    supported.
-   Timestamp is correct.
-   Alert appears only once.
-   Acknowledge works.
-   View works.
-   Connection loss is handled.
-   Reconnection does not duplicate alerts.
-   Ordering remains correct.

------------------------------------------------------------------------

# 44. Real-Time Alert Risks

Real-time functionality introduces race conditions.

Example:

``` text
Alert arrives
     ↓
User acknowledges
     ↓
Same alert arrives again
```

Expected:

``` text
One logical alert
```

not:

``` text
Duplicate alert
```

Other risks:

-   Duplicate events.
-   Missing events.
-   Out-of-order events.
-   Stale counts.
-   Incorrect acknowledgement state.
-   Reconnection duplication.

------------------------------------------------------------------------

# 45. Alert Counts

The alert tabs display counts.

Example:

``` text
Alerts (20)
Acknowledged (0)
```

Acknowledge transition should produce:

``` text
20 active
   ↓
Acknowledge one
   ↓
19 active
1 acknowledged
```

For a new live alert:

``` text
New alert
   ↓
Active count increments
```

Counts should remain synchronized with actual alert records.

------------------------------------------------------------------------

# 46. GeoLinks

GeoLinks allow users to create and manage temporary vehicle tracking
links.

The supplied screen describes the feature as:

``` text
Create and manage temporary vehicle tracking links
```

The GeoLinks list contains:

``` text
Title
Status
Created
Expires
Actions
Details
```

When there are no links, the page displays:

``` text
No GeoLinks found
```

------------------------------------------------------------------------

# 47. Create GeoLink

The Create GeoLink screen contains:

``` text
General
Schedule
Access
```

### General

``` text
Share name*
Select Vehicles
```

### Schedule

``` text
Start date*
Start time*
Expiry days*
Expiry hours*
```

The UI shows:

``` text
Max 48 hrs
```

### Access

``` text
Map only
Map and details
```

------------------------------------------------------------------------

# 48. GeoLink Creation Flow

``` text
Create GeoLink
       ↓
Enter Share Name
       ↓
Select Vehicle(s)
       ↓
Set Start Date
       ↓
Set Start Time
       ↓
Set Expiry
       ↓
Select Access Level
       ↓
Create
       ↓
GeoLink created
```

------------------------------------------------------------------------

# 49. GeoLink Access Levels

Two access levels are visible.

### Map only

``` text
Vehicle location without details
```

### Map and details

``` text
Location with Vehicle information
```

This creates a clear information-exposure boundary.

QA must verify:

``` text
Map only
   ↓
Location available
   ↓
Vehicle details restricted
```

versus:

``` text
Map and details
   ↓
Location + permitted vehicle information
```

------------------------------------------------------------------------

# 50. GeoLink Expiry

The UI explicitly shows:

``` text
Max 48 hrs
```

This should be treated as a critical business-rule boundary.

Test:

``` text
1 hour
24 hours
48 hours
>48 hours
0 hours
Negative values
Boundary combinations
```

Validation should exist at the backend as well as in the UI.

------------------------------------------------------------------------

# 51. GeoLink Security

GeoLinks expose live vehicle tracking and therefore require strong
security testing.

Verify:

-   Only selected vehicles are exposed.
-   Access level is respected.
-   Map-only links do not expose restricted details.
-   Expired links stop working.
-   Deleted/revoked links stop working.
-   Unauthorized vehicles cannot be added through tampered requests.
-   Vehicle selection changes do not leak previous selections.
-   Expiry cannot be bypassed through client-side manipulation.
-   Invalid/tampered link parameters are rejected.

------------------------------------------------------------------------

# 52. Home State Management

The Home module contains many simultaneous states:

``` text
Selected view preset
Selected tab
Selected vehicle
Selected group
Selected driver
Selected KPI
Selected status filter
Search value
Map mode
Opened contextual panel
Alert state
GeoLink state
```

This makes state management one of the highest-risk areas.

Example:

``` text
Select Vehicle A
      ↓
Open Playback
      ↓
Select Vehicle B
      ↓
Close Playback
```

The application must correctly determine the current context.

------------------------------------------------------------------------

# 53. Context Preservation

Every contextual action must remain associated with the entity that
initiated it.

Example:

``` text
Vehicle A
   ↓
⋮
   ↓
Unit Insights
```

Expected:

``` text
Unit Insights → Vehicle A
```

not:

``` text
Unit Insights → Previously selected Vehicle B
```

Test this for:

``` text
Playback
POI
Alert
Unit Maintenance
Unit Insights
```

------------------------------------------------------------------------

# 54. Refresh Behaviour

Because Home contains real-time and stateful data, refresh behaviour
requires dedicated testing.

Test refresh while:

``` text
Fleet + Running filter
Groups + Idle filter
Drivers + selected driver
Alerts panel open
Contextual panel open
Search active
KPI filter active
GeoLinks open
```

Verify:

-   Data reloads correctly.
-   No duplicate vehicle cards.
-   No duplicate alerts.
-   Counts are correct.
-   Map markers are correct.
-   Contextual data is not stale.
-   Loading states resolve correctly.

------------------------------------------------------------------------

# 55. Loading States

Potential asynchronous components include:

``` text
Fleet
Groups
Drivers
Map
Alerts
Driver details
Licence
Assignment
GeoLinks
Unit commands
Contextual panels
```

For each asynchronous operation:

``` text
Request
  ↓
Loading
  ↓
Success / Empty / Error
```

The UI should not remain indefinitely in loading.

------------------------------------------------------------------------

# 56. Empty States

Possible Home empty states include:

``` text
No vehicles
No groups
No drivers
No alerts
No acknowledged alerts
No GeoLinks
No search results
No vehicles for selected status
No vehicles for search + status
```

These states must be clearly different from:

``` text
Loading
```

and:

``` text
Error
```

------------------------------------------------------------------------

# 57. API Failure Isolation

Home depends on several backend operations.

Potential services include:

``` text
Vehicle API
Group API
Driver API
Location API
Alert API
KPI API
Command API
Assignment API
GeoLink API
```

One service failing should not unnecessarily destroy unrelated Home
functionality.

Example:

``` text
Alert API failure
      ↓
Alerts show error/retry state
      ↓
Fleet monitoring remains usable
```

------------------------------------------------------------------------

# 58. Permissions

The Home module contains sensitive operational and personal information.

Permissions should be tested for:

``` text
Vehicle visibility
Driver information
Driver licence
Alerts
Unit commands
Maintenance
Insights
GeoLinks
Vehicle assignment
```

The security model should be:

``` text
Unauthorized user
      ↓
UI restricted
      +
Backend authorization
```

Hiding a button alone is not sufficient security.

------------------------------------------------------------------------

# 59. Dangerous Operations

The following areas deserve elevated QA priority:

``` text
Unit Commands
Vehicle Assignment
GeoLink Creation
Vehicle Tracking Sharing
Driver Licence Access
```

For operational commands:

``` text
Correct Entity
+
Correct Permission
+
Correct Command
+
Correct Confirmation
+
Correct Backend Request
=
Safe Execution
```

------------------------------------------------------------------------

# 60. Real-Time Vehicle Status

Vehicle status can change dynamically.

Example:

``` text
Vehicle A
Idle
 ↓
Running
```

Expected downstream updates may include:

``` text
Idle count ↓
Running count ↑
Vehicle card status updated
KPI updated
Map status updated
```

Where the UI components represent the same point in time, they should
remain consistent.

------------------------------------------------------------------------

# 61. KPI / Fleet Consistency

The KPI layer and Fleet list should reconcile.

Example:

``` text
Running KPI = 5
```

After selecting Running:

``` text
Running vehicles = 5
```

If the values differ, investigate:

-   Data timing.
-   Permission filtering.
-   Pagination.
-   Stale API response.
-   Duplicate/missing records.
-   Incorrect status calculation.

------------------------------------------------------------------------

# 62. Group / Fleet Consistency

Group counts should reconcile with vehicle-level information.

Example:

``` text
Delhi
Active = 3
Running = 0
Idle = 2
Stopped = X
```

The vehicles represented by the group should produce the corresponding
counts.

Test:

``` text
Fleet vehicle
      ↓
Group membership
      ↓
Group filter
      ↓
Correct group result
```

------------------------------------------------------------------------

# 63. Driver / Vehicle Consistency

Driver assignment creates a relationship:

``` text
Driver A
   ↔
Vehicle X
```

After reassignment:

``` text
Driver A
   ↔
Vehicle Y
```

The relationship should be consistent across:

``` text
Driver card
Driver details
Assignment dialog
Vehicle information
Backend/API data
```

------------------------------------------------------------------------

# 64. Accessibility

Home contains many interactive elements:

``` text
KPI checkboxes
Status chips
Search
Vehicle menus
Driver menus
Alert actions
Map controls
Dialogs
Dropdowns
Buttons
```

Test:

-   Keyboard navigation.
-   Visible focus.
-   Logical tab order.
-   Accessible labels.
-   Dialog focus management.
-   Escape-to-close.
-   Meaningful button names.
-   Status not communicated through color alone.

------------------------------------------------------------------------

# 65. Responsive Behaviour

The Home layout is highly dynamic.

Test:

``` text
Desktop
Laptop
Small viewport
Tablet-sized viewport
Browser zoom
```

Pay particular attention to:

``` text
KPI overflow
Side-panel overflow
Map compression
Action-menu clipping
Alert panel overflow
Driver details overflow
Dialog overflow
Horizontal scrolling
```

------------------------------------------------------------------------

# 66. Cross-Component Regression Matrix

High-value combinations include:

  Component A   Component B    What to Verify
  ------------- -------------- ---------------------------------------
  KPI           Fleet          KPI changes vehicle list
  KPI           Map            Filtered vehicles reflected correctly
  Fleet         Map            Selected vehicle focuses map
  Fleet         Playback       Correct vehicle playback
  Fleet         Alert          Correct vehicle alerts
  Fleet         Unit Command   Command targets selected vehicle
  Groups        Status         Correct group-specific filtering
  Drivers       Assignment     Correct vehicle reassignment
  Drivers       Licence        Correct licence displayed
  Alerts        Live           Real-time alert handling
  Alerts        Acknowledged   Correct state transition
  Search        Filters        Combined filtering
  View Preset   KPI            Header remains usable
  View Preset   Side Panel     Correct layout
  GeoLink       Vehicle        Correct vehicle sharing
  GeoLink       Access         Correct information exposure

------------------------------------------------------------------------

# 67. Recommended Home Smoke Test

A practical smoke suite should verify:

``` text
1. Home loads
2. KPI cards display
3. KPI Settings opens
4. KPI selection saves
5. Minimum KPI validation works
6. Fleet tab opens
7. Vehicle status filter works
8. Vehicle search works
9. Vehicle card actions open
10. Current location works
11. Groups tab works
12. Group filters work
13. Drivers tab works
14. Driver details opens
15. Licence copy opens
16. Vehicle assignment works
17. Alerts panel opens
18. Alert acknowledgement works
19. Alert view works
20. Live alerts works
21. Map/Hybrid switching works
22. View presets work
23. GeoLinks opens
24. GeoLink creation works
```

------------------------------------------------------------------------

# 68. Recommended Automation Structure

A practical Playwright/pytest structure is:

``` text
tests/
└── home/
    ├── test_navigation.py
    ├── test_kpis.py
    ├── test_view_presets.py
    ├── test_fleet.py
    ├── test_vehicle_actions.py
    ├── test_groups.py
    ├── test_drivers.py
    ├── test_vehicle_assignment.py
    ├── test_alerts.py
    ├── test_map.py
    ├── test_geolinks.py
    ├── test_permissions.py
    └── test_home_regression.py
```

API/data tests can be separated:

``` text
api/
└── home/
    ├── test_vehicle_status.py
    ├── test_alerts.py
    ├── test_assignments.py
    ├── test_geolinks.py
    └── test_commands.py
```

------------------------------------------------------------------------

# 69. Automation Priority

## P0 --- Critical

``` text
Home loading
Vehicle filtering
Vehicle/location accuracy
Dangerous unit commands
Driver-vehicle assignment
Alert acknowledgement
Live alerts
Permissions
GeoLink access and expiry
```

## P1 --- High

``` text
KPI Settings
Groups
Driver details
Licence viewing
Playback
Vehicle alerts
Unit Maintenance
Unit Insights
Search
Map/Hybrid
```

## P2 --- Medium

``` text
View presets
Secondary map controls
Cosmetic layout
Minor UI interactions
```

------------------------------------------------------------------------

# 70. Home Module Risk Model

  Area                        Risk
  --------------------------- ----------
  Dangerous unit commands     Critical
  Vehicle/location accuracy   Critical
  Real-time vehicle status    Critical
  Alert acknowledgement       Critical
  Live alerts                 Critical
  Permissions                 Critical
  Driver-vehicle assignment   Critical
  GeoLink security            Critical
  GeoLink expiry              Critical
  KPI/filter consistency      High
  Group filtering             High
  Driver licence access       High
  Playback context            High
  API failure handling        High
  Search + filter             High
  Map rendering               High
  View presets                Medium
  Cosmetic layout             Low

------------------------------------------------------------------------

# 71. Most Important Data Relationships

Home should be tested through relationships, not only individual
screens.

## Vehicle ↔ Status

``` text
Vehicle status
      =
Fleet filter
      =
KPI count
      =
Map state
```

## Driver ↔ Vehicle

``` text
Driver assignment
      =
Driver card
      =
Driver details
      =
Vehicle relationship
```

## Alert ↔ Vehicle

``` text
Alert
  =
Correct vehicle
+
Correct timestamp
+
Correct alert type
```

## GeoLink ↔ Vehicle

``` text
GeoLink
  =
Only selected vehicle(s)
```

## Alert ↔ State

``` text
Active
  ↓
Acknowledge
  ↓
Acknowledged
```

------------------------------------------------------------------------

# 72. The Most Important QA Principle

The Home module should not be tested as a collection of buttons and
cards.

It should be tested as a **stateful real-time system**.

The correct mental model is:

``` text
                    HOME
                     │
             Current State
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
   Fleet           Drivers          Alerts
     │               │                │
     ▼               ▼                ▼
  Vehicle          Driver           Alert
  Status          Assignment        State
     │               │                │
     └───────────────┼────────────────┘
                     ▼
                  Map/UI
                     │
                     ▼
              User Interaction
                     │
                     ▼
              Backend/API Action
                     │
                     ▼
               Updated State
```

Every user action should result in the correct:

``` text
Entity
+
State
+
Data
+
Context
+
Backend operation
+
UI update
```

------------------------------------------------------------------------

# 73. Final Mental Model

The Home module can be reduced to:

``` text
                    TRACKOFY HOME
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
        MONITOR          FILTER          ACT
          │               │               │
          ▼               ▼               ▼
        Map +          KPI + Search     Commands
        Vehicles       + Status         Assignment
          │                              GeoLinks
          │
          └───────────────┬───────────────┘
                          ▼
                     CONTEXT
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       Vehicle          Driver           Alert
       Context          Context          Context
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                    UPDATED STATE
```

Therefore:

``` text
HOME
=
REAL-TIME FLEET MONITORING
+
FILTERING
+
MAP VISUALIZATION
+
VEHICLE ACTIONS
+
DRIVER MANAGEMENT
+
ALERT MANAGEMENT
+
VEHICLE/DRIVER RELATIONSHIPS
+
SECURE TRACKING SHARING
```

The strongest Home test does not ask only:

> "Did the button work?"

It asks:

> **"Did the correct entity, state, data, map context, backend
> operation, permission boundary, and downstream UI update occur after
> the interaction?"**

------------------------------------------------------------------------

## 74. Scope Notes

This document is based on the Home-module behaviour described in the
supplied screenshots and the functional explanation provided with them.

The screenshots establish the visible concepts including:

-   KPI Settings and the minimum six-KPI rule.
-   Home Settings/view configuration.
-   Fleet, Groups, and Drivers navigation.
-   Vehicle and group cards.
-   Driver information, licence, and vehicle assignment.
-   Alerts & Notifications with Alerts and Acknowledged tabs.
-   View All Alerts and Live.
-   GeoLinks list and creation configuration.
-   Map/Hybrid controls and map-side controls.

Where the supplied material does not establish an exact backend
calculation, API contract, permission rule, or real-time transport
mechanism, this document intentionally describes the item as a **QA
validation area** rather than claiming an implementation detail as fact.

The live Trackofy implementation and applicable functional/API
specifications should remain the source of truth for exact business
rules.
