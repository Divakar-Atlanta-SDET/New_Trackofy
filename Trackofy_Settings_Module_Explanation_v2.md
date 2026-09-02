# Trackofy Settings Module --- Functional & QA Explanation

## 1. Overview

The **Settings** module in Trackofy is the platform's operational
configuration area. It is not a single CRUD screen. It is a collection
of configuration and management features used to define how drivers,
vehicles, alerts, locations, performance rules, and routes behave across
the application.

From the current Trackofy interface, Settings is divided into **four
major sections**:

``` text
Settings
│
├── Driver Management
│   ├── Driver
│   └── Driver Performance
│
├── Vehicle Management
│   ├── Vehicle Group
│   ├── Vehicle Performance
│   └── Location Control
│
├── Alert Configuration
│   ├── AC Alert
│   ├── Ignition Alert
│   ├── Main Power Alert
│   ├── Panic Alert
│   ├── Speed Alert
│   ├── Idle Alert
│   ├── Temperature
│   ├── BMS Alert
│   ├── POI Alert
│   ├── Geofence Alert
│   ├── Vehicle Odometer Alert
│   └── AIS Alert
│
└── Route Management
```

The important thing to understand is that these four sections are
**connected**.

For example:

``` text
Driver
   ↓
Assigned to Vehicle
   ↓
Vehicle generates tracking data
   ↓
Alerts / Performance rules evaluate the data
   ↓
Reports and Tracking use the resulting information
```

Similarly:

``` text
Vehicle
   ↓
Vehicle Group
   ↓
Location Control
   ↓
Route Assignment
   ↓
Tracking / Alerts / Reports
```

Therefore, Settings should be tested not only as individual CRUD
screens, but also as a **configuration layer for the rest of Trackofy**.

------------------------------------------------------------------------

# 2. Settings Architecture

A useful high-level model is:

``` text
                         TRACKOFY SETTINGS
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   DRIVER DATA              VEHICLE DATA           EVENT RULES
        │                       │                       │
        │                       │                       └── Alerts
        │                       ├── Groups
        │                       ├── Performance
        │                       └── Location Control
        │
        ├── Driver
        └── Driver Performance
                                │
                                ▼
                         ROUTE MANAGEMENT
                                │
                                ├── Routes
                                ├── Waypoints
                                └── Assigned Units
```

This makes Settings a combination of:

-   **Master-data management**
-   **Configuration**
-   **Assignment**
-   **Rule definition**
-   **Operational planning**

------------------------------------------------------------------------

# 3. Common UI Pattern

Most Settings pages follow a common management pattern.

A typical list page contains:

``` text
Page Header
    │
    ├── Page title
    ├── Record/configuration count
    └── Add / Configure action
    │
    ▼
Toolbar
    ├── Rows per page
    ├── Pagination
    ├── Export
    ├── Print
    ├── Copy
    └── Search
    │
    ▼
Data Table
    ├── Records
    ├── Edit
    ├── Delete
    └── Feature-specific actions
```

The screenshots show common actions such as:

-   Add/Create
-   Edit
-   Delete
-   Search
-   Pagination
-   Export
-   Print
-   Copy
-   Feature-specific assignment/view/detail actions

This means the common CRUD behaviour should be tested consistently
across Settings.

------------------------------------------------------------------------

# 4. Driver Management

## 4.1 Purpose

**Driver Management** is used to maintain driver records and
driver-related performance configuration.

It contains:

``` text
Driver Management
│
├── Driver
└── Driver Performance
```

------------------------------------------------------------------------

# 5. Driver

The Driver page maintains driver profiles and driving-licence
information.

The current UI displays a table containing information such as:

-   Sr No
-   Name
-   DL No
-   Assigned Unit
-   DL Issued Date
-   DL Expiry Date
-   DOB
-   Email
-   Contact No
-   Emergency No
-   Address
-   Additional licence-related information

The page also provides an **Add Driver** action.

------------------------------------------------------------------------

## 5.1 Create Driver

The current Create Driver form is divided into two major sections.

### Personal Information

The form contains:

-   Name \*
-   Mobile No \*
-   Email \*
-   Date of Birth \*
-   Emergency Contact

### Driving Licence

The form contains:

-   DL Number \*
-   DL Issue Date \*
-   DL Expiry Date \*
-   Driving Licence Copy \*

The licence copy supports the file types displayed by the UI:

``` text
PDF
JPG
JPEG
PNG
```

The form provides:

``` text
Cancel
Create Driver
```

------------------------------------------------------------------------

## 5.2 Driver CRUD Flow

``` text
Driver
  │
  ├── Create Driver
  │      ├── Enter personal information
  │      ├── Enter licence information
  │      ├── Upload licence copy
  │      └── Create
  │
  ├── Read
  │      ├── Search
  │      ├── View table
  │      └── Pagination
  │
  ├── Update
  │      └── Edit existing driver
  │
  └── Delete
         └── Delete driver
```

------------------------------------------------------------------------

# 6. Assigning a Driver to a Vehicle/Unit

Driver management has an important operational relationship: **a driver
can be assigned to a unit/vehicle**.

The Driver list contains an **Assigned Unit** field and a
feature-specific action next to the driver record.

The conceptual workflow is:

``` text
Driver
   ↓
Assign
   ↓
Select Unit / Vehicle
   ↓
Confirm Assignment
   ↓
Driver becomes associated with the unit
```

This is more than a normal CRUD operation because it creates a
**relationship between two entities**.

### QA considerations

Test:

-   Assign an unassigned driver.
-   Assign a driver to a valid unit.
-   Change the driver's assigned unit.
-   Remove/unassign the driver if supported.
-   Assign the same driver again.
-   Assign a unit already associated with another driver.
-   Verify the assignment after refresh.
-   Verify the assignment from the dependent Unit/Vehicle view if
    available.
-   Verify the assignment is reflected wherever driver/unit
    relationships are consumed.

------------------------------------------------------------------------

# 7. Driver Performance

Driver Performance is used to define **performance categories and
scoring/configuration rules** for evaluating drivers.

The screenshot shows configurations such as:

``` text
AVERAGE
GOOD
EXCELLENT
```

The configuration table contains parameters including:

-   Category
-   Overspeed Limit
-   Distance Range
-   Halt Time
-   Running Time
-   Idle Time
-   Harsh Acceleration
-   Harsh Braking
-   Rash Turning
-   Edit
-   Delete

Therefore, Driver Performance is essentially a **rule configuration
engine for driver evaluation**.

------------------------------------------------------------------------

## 7.1 Configure Driver Performance

The configuration form contains two important stages.

### Performance Parameters

First select a category.

Then select the parameters to monitor.

The available parameters shown in the UI include:

``` text
Overspeed Limit
Distance Range
Halt Time Range
Idle Time Range
Harsh Acceleration
Harsh Braking
Rash Turning
Running Time Range
```

### Selected Parameter Configuration

After selecting parameters, the system allows the corresponding limits,
ranges, or occurrence counts to be configured.

Conceptually:

``` text
Category
   ↓
Select Parameters
   ↓
Configure parameter values
   ↓
Save Configuration
```

------------------------------------------------------------------------

## 7.2 Example Driver Performance Model

A simplified model is:

``` text
Driver
   ↓
Driving Data
   │
   ├── Speed
   ├── Distance
   ├── Halt
   ├── Running
   ├── Idle
   ├── Harsh Acceleration
   ├── Harsh Braking
   └── Rash Turning
   ↓
Configured Performance Rules
   ↓
Performance Category
   ↓
Driver Evaluation
```

This explains why changes to performance configuration can affect how
drivers are evaluated.

------------------------------------------------------------------------

# 8. Vehicle Management

Vehicle Management contains:

``` text
Vehicle Management
│
├── Vehicle Group
├── Vehicle Performance
└── Location Control
```

These features manage vehicle organization, vehicle performance
criteria, and location-based assignment/control.

------------------------------------------------------------------------

# 9. Vehicle Group

Vehicle Group allows vehicles/units to be organized into manageable
operational groups.

The screenshot shows:

``` text
Unit Groups
```

with the description:

> Organize vehicles into manageable operational groups.

The list contains:

-   Sr No
-   Unit Group Name
-   Unit List
-   Edit
-   Delete

------------------------------------------------------------------------

## 9.1 Create Unit Group

The Create Unit Group form contains:

``` text
Group Information
    │
    ├── Unit Group Name *
    │
    └── Assigned Units
          └── Select Units
```

Therefore a group is not just a name. It can contain an **assignment of
units**.

Workflow:

``` text
Create Unit Group
      ↓
Enter Group Name
      ↓
Select Units
      ↓
Create Group
      ↓
Group appears in list
```

------------------------------------------------------------------------

## 9.2 Vehicle Group Testing

Important scenarios:

-   Create group with valid name.
-   Create group without a name.
-   Create duplicate group.
-   Create group with one unit.
-   Create group with multiple units.
-   Edit group name.
-   Add units to an existing group.
-   Remove units from a group.
-   Delete group.
-   View Unit List.
-   Verify assignments after refresh.
-   Verify group relationships in dependent functionality.

------------------------------------------------------------------------

# 10. Vehicle Performance

Vehicle Performance defines performance ranges for vehicle/unit
evaluation.

The screenshot shows categories such as:

``` text
EXCELLENT
AVERAGE
POOR
```

The table includes:

-   Category
-   Distance Range
-   Halt Time Range
-   Running Time Range
-   Idle Time Range
-   Edit
-   Delete

------------------------------------------------------------------------

## 10.1 Create Unit Performance

The configuration form contains:

### Performance Category

A category is selected first.

### Performance Ranges

Ranges can then be defined for parameters such as:

``` text
Distance Range
Halt Time
Idle Time
Running Time
```

The UI uses range controls/sliders for configuring minimum and maximum
values.

Conceptually:

``` text
Category
   ↓
Performance Ranges
   ↓
Minimum / Maximum values
   ↓
Create Performance
```

------------------------------------------------------------------------

## 10.2 Why Vehicle Performance Matters

The purpose is to classify/evaluate vehicle behaviour based on
configured ranges.

For example:

``` text
Vehicle Data
    ↓
Distance / Halt / Running / Idle
    ↓
Compare with configured ranges
    ↓
Performance Category
```

Therefore, boundary testing is particularly important.

Test:

``` text
Minimum
Minimum - 1
Maximum
Maximum + 1
Zero
Decimal values
```

where those values are valid/invalid according to the actual business
rules.

------------------------------------------------------------------------

# 11. Location Control

Location Control is used to create operational control locations and
assign units to them.

The list displays:

-   Sr No
-   Location
-   Assign Unit
-   Edit
-   Delete

Example locations shown include:

``` text
Bhopal
Delhi
Haryana
```

------------------------------------------------------------------------

## 11.1 Add Location

The current form contains:

``` text
Location Information
      ↓
Location *
```

and the action:

``` text
Create Location
```

After creating a location, the operational relationship can be
established through the **Assign Unit** action.

Conceptually:

``` text
Location
   ↓
Assign Unit
   ↓
Select Vehicle/Unit
   ↓
Save
```

This means Location Control is another **relationship-management
feature**, not just a simple name-based CRUD screen.

------------------------------------------------------------------------

# 12. Alert Configuration

Alert Configuration is the largest event-oriented section visible in the
current Settings navigation.

It contains:

``` text
Alert Configuration
│
├── AC Alert
├── Ignition Alert
├── Main Power Alert
├── Panic Alert
├── Speed Alert
├── Idle Alert
├── Temperature
├── BMS Alert
├── POI Alert
├── Geofence Alert
├── Vehicle Odometer Alert
└── AIS Alert
```

The name describes its purpose:

> Configure conditions under which Trackofy should generate
> alerts/events for vehicles.

------------------------------------------------------------------------

# 13. Alert Configuration Mental Model

Alerts can be understood as:

``` text
Vehicle
   ↓
Vehicle/Device Data
   ↓
Configured Condition
   ↓
Condition Triggered
   ↓
Alert Generated
   ↓
User/Platform consumes alert
```

For example:

``` text
Speed
   ↓
Configured Speed Threshold
   ↓
Vehicle exceeds threshold
   ↓
Speed Alert
```

Another example:

``` text
Ignition State
   ↓
Configured Ignition Rule
   ↓
Condition occurs
   ↓
Ignition Alert
```

The exact fields and conditions vary by alert type.

------------------------------------------------------------------------

# 14. Alert Types

## 14.1 AC Alert

Configuration related to AC events.

QA should verify:

-   Configuration creation.
-   Threshold/condition behaviour.
-   Vehicle association.
-   Enable/disable behaviour if available.
-   Trigger generation.
-   Edit/delete.

------------------------------------------------------------------------

## 14.2 Ignition Alert

Handles ignition-related events.

Conceptual flow:

``` text
Ignition state
    ↓
Configured rule
    ↓
Condition met
    ↓
Ignition alert
```

------------------------------------------------------------------------

## 14.3 Main Power Alert

Used for main-power related events.

Important scenarios include:

-   Correct vehicle selection.
-   Correct condition configuration.
-   Trigger behaviour.
-   Repeated events.
-   Edit/delete.
-   Invalid configuration.

------------------------------------------------------------------------

## 14.4 Panic Alert

Handles panic/emergency events.

Because this can represent a high-priority operational event, test:

-   Correct configuration.
-   Correct vehicle association.
-   Trigger behaviour.
-   Alert visibility.
-   Duplicate/repeated events.
-   Permission restrictions.

------------------------------------------------------------------------

## 14.5 Speed Alert

Speed Alert is particularly important because speed thresholds directly
influence event generation.

Conceptually:

``` text
Configured speed threshold
          ↓
Vehicle speed
          ↓
Threshold exceeded
          ↓
Speed Alert
```

Boundary testing is critical:

``` text
Threshold - 1
Threshold
Threshold + 1
```

------------------------------------------------------------------------

## 14.6 Idle Alert

Idle Alert relates to vehicle idle conditions.

Conceptually:

``` text
Vehicle idle duration
       ↓
Configured idle threshold
       ↓
Threshold reached
       ↓
Idle Alert
```

Test boundary durations and repeated idle periods.

------------------------------------------------------------------------

## 14.7 Temperature

Temperature configuration handles temperature-related events/conditions.

Potential testing dimensions include:

``` text
Temperature threshold
Vehicle association
Sensor value
Boundary value
Above threshold
Below threshold
```

The exact configuration fields should be taken from the live Temperature
screen.

------------------------------------------------------------------------

## 14.8 BMS Alert

BMS stands for Battery Management System in the current navigation
terminology.

BMS-related alert configuration should be tested against the fields and
event conditions exposed by the actual BMS screen.

------------------------------------------------------------------------

## 14.9 POI Alert

POI-related alerts concern **Points of Interest**.

A conceptual model is:

``` text
Vehicle
   ↓
POI / location
   ↓
Configured POI condition
   ↓
Vehicle enters/leaves/reaches condition
   ↓
POI Alert
```

The exact trigger behaviour must be verified from the actual POI
configuration.

------------------------------------------------------------------------

## 14.10 Geofence Alert

Geofence alerts are location-boundary events.

Conceptually:

``` text
Vehicle
   ↓
Geofence
   ↓
Vehicle crosses boundary
   ↓
Configured event
   ↓
Geofence Alert
```

Important scenarios include:

-   Entry.
-   Exit.
-   Boundary conditions.
-   Vehicle assignment.
-   Repeated crossings.
-   Configuration changes.
-   Disabled/deleted geofence dependencies where applicable.

------------------------------------------------------------------------

## 14.11 Vehicle Odometer Alert

This alert is based on odometer-related vehicle values.

A conceptual flow is:

``` text
Vehicle Odometer
       ↓
Configured threshold
       ↓
Threshold reached
       ↓
Odometer Alert
```

Boundary and repeated-trigger behaviour should be tested.

------------------------------------------------------------------------

## 14.12 AIS Alert

AIS Alert is available as a separate alert configuration item in the
current Settings navigation.

The exact AIS fields and trigger rules should be verified from the live
AIS configuration screen rather than assumed from the menu name alone.

------------------------------------------------------------------------

# 15. Alert Configuration as CRUD

Each alert type should be considered its own configuration entity.

The common model is:

``` text
Create Alert Configuration
        ↓
Read/List Configurations
        ↓
Edit Configuration
        ↓
Delete Configuration
        ↓
Verify resulting alert behaviour
```

The last step is essential.

A configuration CRUD test alone is insufficient.

For example:

``` text
Create Speed Alert
       ↓
Verify record exists
       ↓
Generate qualifying speed condition
       ↓
Verify Speed Alert is actually produced
```

This is **configuration-to-runtime validation**.

------------------------------------------------------------------------

# 16. Route Management

Route Management is used to:

-   Create routes.
-   View routes.
-   Manage waypoints.
-   Assign units.
-   Show route details.

The current route list displays columns including:

``` text
Name
Distance
Duration
Origin
Destination
Show Route
Assign Unit
Details
Delete
```

------------------------------------------------------------------------

# 17. Route Creation

The current Route Setup screen contains two modes:

``` text
Create Route
Custom Route
```

The Create Route flow contains:

### Route Details

``` text
Route Name *
```

### Route Locations

``` text
Start Location *
Destination *
Add Waypoint
```

### Route Summary

The interface provides a calculated route summary including:

``` text
Distance
Estimated travel time
```

The map is used to visualize the route.

------------------------------------------------------------------------

# 18. Route Creation Flow

The complete conceptual flow is:

``` text
Route Management
       ↓
Add Route
       ↓
Route Name
       ↓
Start Location
       ↓
Destination
       ↓
Optional Waypoints
       ↓
Show Route
       ↓
Route Calculation
       ↓
Review Distance/Duration
       ↓
Save Route
```

------------------------------------------------------------------------

# 19. Custom Route

The Route Setup interface also exposes a **Custom Route** option.

This indicates that route creation is not limited to automatically
calculated origin-to-destination routing.

A custom route should therefore be treated as a separate testing path:

``` text
Custom Route
     ↓
Define route manually
     ↓
Review route
     ↓
Save
```

The exact drawing/editing interaction should be verified from the
current implementation.

------------------------------------------------------------------------

# 20. Route Waypoints

A waypoint is an intermediate point between the start and destination.

Example:

``` text
Start
  ↓
Waypoint 1
  ↓
Waypoint 2
  ↓
Destination
```

QA should verify:

-   Add one waypoint.
-   Add multiple waypoints.
-   Waypoint ordering.
-   Change/remove waypoint if supported.
-   Route recalculation.
-   Distance update.
-   Duration update.
-   Save and reopen route.

------------------------------------------------------------------------

# 21. Assigning a Route to a Vehicle

The route list contains an **Assign Unit** action.

The conceptual flow is:

``` text
Saved Route
    ↓
Assign Unit
    ↓
Select Vehicle/Unit
    ↓
Confirm
    ↓
Route becomes associated with the unit
```

This is another relationship-based operation.

Therefore, route testing should include:

``` text
Route CRUD
+
Route calculation
+
Route visualization
+
Unit assignment
```

------------------------------------------------------------------------

# 22. Route Details and Show Route

The route list provides:

### Show Route

Used to visually display the route on the map.

### Details

Used to inspect route information.

The test model should therefore be:

``` text
Create Route
   ↓
List
   ↓
Show Route
   ↓
Verify map representation
   ↓
Details
   ↓
Verify stored route information
```

------------------------------------------------------------------------

# 23. Relationship Model Across Settings

The most important part of understanding Settings is the relationships
between entities.

A simplified model is:

``` text
                    DRIVER
                      │
                      │ assigned to
                      ▼
                    VEHICLE
                 /     │      \
                /      │       \
               ▼       ▼        ▼
         UNIT GROUP  LOCATION  ROUTE
               │       │        │
               │       │        │
               └───────┴────────┘
                       │
                       ▼
                    TRACKING
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       ALERTS      PERFORMANCE    REPORTS
```

This is why Settings should be tested as an interconnected system.

------------------------------------------------------------------------

# 24. Settings Data Dependencies

Examples of dependencies include:

### Driver → Vehicle

``` text
Driver
  ↓
Assignment
  ↓
Vehicle/Unit
```

### Vehicle → Group

``` text
Vehicle
  ↓
Vehicle Group
```

### Vehicle → Location

``` text
Vehicle
  ↓
Location Control
```

### Vehicle → Route

``` text
Vehicle
  ↓
Assigned Route
```

### Vehicle → Alerts

``` text
Vehicle
  ↓
Alert Configuration
```

### Driver → Performance

``` text
Driver
  ↓
Driving Data
  ↓
Driver Performance Rules
```

### Vehicle → Performance

``` text
Vehicle
  ↓
Operational Data
  ↓
Vehicle Performance Rules
```

------------------------------------------------------------------------

# 25. CRUD + Assignment Testing

A major mistake in testing Settings would be to test only CRUD.

For example:

``` text
Create Driver ✓
Edit Driver ✓
Delete Driver ✓
```

but never test:

``` text
Driver → Assign Vehicle → Verify Relationship
```

The stronger model is:

``` text
CRUD
+
Assignment
+
Dependency
+
Runtime Verification
```

The same principle applies to:

-   Driver → Vehicle.
-   Vehicle → Group.
-   Vehicle → Location.
-   Route → Vehicle.
-   Alert → Vehicle.

------------------------------------------------------------------------

# 26. Cross-Module Validation

Settings should be tested against the modules that consume its
configuration.

Example:

``` text
Settings
   ↓
Create Configuration
   ↓
Unit / Tracking / Reports
   ↓
Verify configuration is reflected
```

Examples:

### Driver assignment

``` text
Assign Driver to Unit
       ↓
Open Unit/Tracking
       ↓
Verify driver relationship
```

### Vehicle group

``` text
Create Vehicle Group
       ↓
Assign Units
       ↓
Verify group membership
```

### Route

``` text
Create Route
       ↓
Assign Unit
       ↓
Tracking / Route view
       ↓
Verify assigned route
```

### Alert

``` text
Create Alert Rule
       ↓
Generate qualifying event
       ↓
Verify alert
```

------------------------------------------------------------------------

# 27. Permission Model

The current Settings interface explicitly displays:

> Menu access follows assigned permissions.

This is an important testing clue.

Settings should therefore be tested with different permission levels.

``` text
User
 │
 ├── View
 ├── Create
 ├── Edit
 ├── Delete
 └── Assign/Configure
```

Do not assume that access to a Settings submenu automatically means
access to every action.

Test separately:

``` text
Can view?
Can create?
Can edit?
Can delete?
Can assign?
Can configure?
```

And verify backend authorization as well as UI behaviour.

------------------------------------------------------------------------

# 28. Search, Filter and Pagination

Most list-oriented Settings screens contain:

-   Search.
-   Rows-per-page.
-   Pagination.
-   Export/print/copy controls.

For every applicable Settings list, test:

### Search

``` text
Exact
Partial
Case variation
No result
Clear search
Special characters
```

### Pagination

``` text
First
Middle
Last
Next
Previous
Page size
```

### CRUD + Search

``` text
Search
 ↓
Edit
 ↓
Save
 ↓
Verify
```

### CRUD + Pagination

``` text
Go to page 2
 ↓
Edit/Delete
 ↓
Verify list state
```

------------------------------------------------------------------------

# 29. Export and Data Presentation

The Settings list toolbar exposes multiple data-output actions in the
current UI.

Where enabled, verify:

-   Export output is generated.
-   Export contains the expected records.
-   Export reflects active search/filter state where intended.
-   Column values are correct.
-   Large datasets do not produce truncated or corrupted output.
-   Print output is usable.
-   Copy action contains the expected table data.

The exact export formats and business rules should be verified from the
implementation.

------------------------------------------------------------------------

# 30. Validation and Boundary Testing

Because Settings contains many numeric, date, range, and configuration
fields, boundary testing is critical.

Examples:

``` text
0
1
Minimum - 1
Minimum
Maximum
Maximum + 1
Negative
Decimal
Blank
Very large value
```

For dates:

``` text
Valid date
Invalid date
Issue date > Expiry date
Expiry date = Issue date
Past date
Future date
```

For driver licence data:

``` text
Valid document
Unsupported file type
Oversized file
Empty upload
Duplicate upload
Corrupt file
```

The exact allowed values must follow the actual field requirements.

------------------------------------------------------------------------

# 31. Data Integrity

For every important Settings operation, verify:

``` text
UI
 ↓
Request Payload
 ↓
Backend
 ↓
Response
 ↓
List
 ↓
Refresh
 ↓
Reopen
```

The same value should remain consistent across the entire lifecycle.

Example:

``` text
Create:
Category = EXCELLENT

API:
Category = EXCELLENT

List:
Category = EXCELLENT

After refresh:
Category = EXCELLENT
```

------------------------------------------------------------------------

# 32. Negative Testing

Settings should receive aggressive negative testing because invalid
configuration can affect other modules.

Examples:

-   Empty required fields.
-   Invalid numeric values.
-   Invalid dates.
-   Duplicate records.
-   Invalid file upload.
-   Invalid assignment.
-   Assigning unavailable unit.
-   Delete referenced record.
-   Unauthorized API request.
-   Network failure during save.
-   Repeated save clicks.
-   Stale API responses.
-   Session expiry during CRUD.

------------------------------------------------------------------------

# 33. High-Risk Areas

  -----------------------------------------------------------------------
  Priority                Area                    Why
  ----------------------- ----------------------- -----------------------
  🔴 Critical             Alert configuration     Directly affects event
                                                  generation

  🔴 Critical             Driver ↔ Vehicle        Incorrect operational
                          assignment              ownership

  🔴 Critical             Route ↔ Vehicle         Can affect route
                          assignment              operations

  🔴 Critical             Delete referenced       Downstream impact
                          configuration           

  🔴 Critical             Permission bypass       Security risk

  🔴 Critical             Incorrect performance   Incorrect
                          thresholds              driver/vehicle
                                                  evaluation

  🟠 High                 Vehicle grouping        Organizational/data
                                                  consistency

  🟠 High                 Location assignment     Location-based
                                                  operations

  🟠 High                 Route calculation       Distance/time
                                                  correctness

  🟠 High                 Driver licence data     Data integrity

  🟠 High                 Search/pagination       Record discoverability

  🟠 High                 API failure handling    False configuration
                                                  state

  🟡 Medium               Export/print            Reporting usability

  🟡 Medium               Empty/loading states    User experience
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 34. Common Bugs to Hunt

## Driver

-   Driver created but not visible after refresh.
-   Incorrect licence date accepted.
-   Expired licence treated as valid when it should not be.
-   Unsupported file accepted.
-   Wrong unit assigned.
-   Assignment not persisted.
-   Driver edit modifies unrelated fields.

## Driver Performance

-   Category can be duplicated incorrectly.
-   Invalid range accepted.
-   Minimum greater than maximum.
-   Parameter selected but configuration not saved.
-   Updated threshold not reflected in evaluation.
-   Delete leaves dependent configuration active.

## Vehicle Group

-   Same unit incorrectly assigned to conflicting groups.
-   Group name duplication.
-   Unit assignment not persisted.
-   Deleted group remains available.
-   Unit list displays stale membership.

## Vehicle Performance

-   Minimum \> maximum.
-   Boundary values handled incorrectly.
-   Decimal values incorrectly rejected/accepted.
-   Category configuration does not affect expected evaluation.
-   Delete/update does not persist.

## Location Control

-   Location duplication.
-   Location name accepts invalid data.
-   Wrong unit assigned.
-   Assignment not persisted.
-   Deleted location remains selectable.

## Alerts

-   Alert saved but never triggers.
-   Alert triggers below threshold.
-   Alert does not trigger above threshold.
-   Duplicate alerts generated.
-   Alert configuration affects wrong vehicle.
-   Disabled/deleted alert still triggers.
-   Incorrect alert type generated.

## Routes

-   Incorrect route distance.
-   Incorrect duration.
-   Waypoints change order unexpectedly.
-   Saved route differs from displayed route.
-   Wrong unit assigned.
-   Deleted route remains available.
-   Route assignment not reflected downstream.

------------------------------------------------------------------------

# 35. Recommended Automation Structure

Because Settings is large, automation should be organized by business
entity rather than creating one enormous test file.

A practical structure is:

``` text
tests/
│
├── settings/
│   │
│   ├── driver/
│   │   ├── test_driver_create.py
│   │   ├── test_driver_update.py
│   │   ├── test_driver_delete.py
│   │   └── test_driver_assignment.py
│   │
│   ├── driver_performance/
│   │   └── test_driver_performance.py
│   │
│   ├── vehicle_group/
│   │   └── test_vehicle_group.py
│   │
│   ├── vehicle_performance/
│   │   └── test_vehicle_performance.py
│   │
│   ├── location_control/
│   │   └── test_location_control.py
│   │
│   ├── alerts/
│   │   ├── test_ac_alert.py
│   │   ├── test_ignition_alert.py
│   │   ├── test_speed_alert.py
│   │   ├── test_idle_alert.py
│   │   └── ...
│   │
│   └── routes/
│       ├── test_route_create.py
│       ├── test_route_update.py
│       ├── test_route_delete.py
│       └── test_route_assignment.py
```

The exact file structure can be adapted to your existing automation
framework.

------------------------------------------------------------------------

# 36. API + UI + E2E Strategy

Do not automate all Settings coverage through UI.

Use:

``` text
                 SETTINGS
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
       API          UI          E2E
        │           │           │
   Data/CRUD   Interaction   Critical
   validation   validation    workflows
```

### API layer

Best for:

-   CRUD.
-   Validation.
-   Duplicate checks.
-   Permission checks.
-   Large datasets.
-   Error handling.
-   Response contracts.

### UI layer

Best for:

-   Navigation.
-   Forms.
-   Search.
-   Pagination.
-   Dialogs.
-   Assignment controls.
-   Visible validation.
-   User feedback.

### E2E layer

Best for:

-   Driver → Vehicle assignment.
-   Vehicle → Group relationship.
-   Location → Unit assignment.
-   Route → Unit assignment.
-   Alert configuration → actual alert.
-   Performance configuration → resulting evaluation.

------------------------------------------------------------------------

# 37. The Most Important Settings Test Model

For every Settings feature, use this sequence:

``` text
1. Navigate
      ↓
2. Read existing data
      ↓
3. Search
      ↓
4. Create
      ↓
5. Validate
      ↓
6. Verify persistence
      ↓
7. Edit
      ↓
8. Verify update
      ↓
9. Assign / configure relationship
      ↓
10. Verify dependency
      ↓
11. Delete / deactivate
      ↓
12. Verify final state
      ↓
13. Test permissions
      ↓
14. Test API/network failures
```

For alerts and performance configuration, add:

``` text
Configuration
      ↓
Generate qualifying operational condition
      ↓
Verify actual runtime behaviour
```

For routes, add:

``` text
Route configuration
      ↓
Map calculation
      ↓
Distance/Duration
      ↓
Assign Unit
      ↓
Verify route behaviour
```

------------------------------------------------------------------------

# 38. Settings as a Configuration Dependency Graph

A more accurate mental model of Trackofy Settings is:

``` text
                         SETTINGS
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
       DRIVERS           VEHICLES          ROUTES
          │                 │                 │
          │           ┌─────┼─────┐           │
          │           │     │     │           │
          │         GROUP  PERF  LOCATION     │
          │                                   │
          └──────────────┐        ┌────────────┘
                         │        │
                         ▼        ▼
                      TRACKING / OPERATIONS
                             │
                 ┌───────────┼───────────┐
                 │           │           │
                 ▼           ▼           ▼
               ALERTS    PERFORMANCE   REPORTS
```

This is why a Settings regression can have a much wider impact than a
normal UI defect.

------------------------------------------------------------------------

# 39. Final Understanding

Trackofy Settings should be understood as **four connected operational
configuration domains**:

### 1. Driver Management

Manages:

``` text
Driver profiles
Licence information
Driver ↔ Vehicle assignments
Driver performance rules
```

### 2. Vehicle Management

Manages:

``` text
Vehicle groups
Vehicle performance rules
Location control
Vehicle ↔ Location relationships
```

### 3. Alert Configuration

Manages:

``` text
AC
Ignition
Main Power
Panic
Speed
Idle
Temperature
BMS
POI
Geofence
Vehicle Odometer
AIS
```

and defines conditions under which vehicle events become alerts.

### 4. Route Management

Manages:

``` text
Routes
Start/Destination
Waypoints
Route calculation
Distance
Duration
Route visualization
Route ↔ Unit assignment
```

------------------------------------------------------------------------

# 40. Final QA Mental Model

Do not think:

``` text
Settings = Many CRUD Pages
```

Think:

``` text
Settings
   =
Master Data
   +
Configuration
   +
Relationships
   +
Operational Rules
   +
Assignments
   +
Runtime Behaviour
```

Therefore:

``` text
CRUD Testing
      +
Validation
      +
API Testing
      +
Permission Testing
      +
Assignment Testing
      +
Dependency Testing
      +
Boundary Testing
      +
Runtime Verification
      +
E2E Testing
```

That is the correct testing mindset for Trackofy's Settings module.

> **The real question is not simply "Can I create this configuration?"**
>
> **The real question is "After I create or modify this configuration,
> does Trackofy behave correctly everywhere that configuration is
> used?"**

That distinction is what makes Settings one of the most important
modules in Trackofy to test thoroughly.

------------------------------------------------------------------------

## Source Basis

This document is based primarily on the current Trackofy Settings
screenshots provided with the request. The screenshots establish the
visible four-section Settings structure, the displayed submenus,
Driver/Unit forms, performance configuration screens, alert categories,
Location Control, and Route Setup/assignment workflows.

Where the screenshots do not expose the exact backend rules or fields
for a particular alert type or action, this document deliberately
describes the functional purpose and QA model without inventing
undocumented requirements.
