# Trackofy Unit Module --- Explanation Guide

## 1. What is the Unit Module?

The **Unit module** is the area of Trackofy used to manage the
configuration and operational settings associated with a tracked
vehicle/unit.

A useful mental model is:

``` text
Unit
 ├── General
 ├── Icon
 ├── Sensors
 ├── Service
 │    ├── Pollution
 │    ├── Fitness
 │    ├── Insurance
 │    └── Vehicle Service
 └── Alert
```

The Unit module is important because the configuration maintained here
can affect how a unit is represented, configured, monitored, and
associated with operational data elsewhere in Trackofy.

> **Simple definition:** Unit = the configuration and management area
> for a tracked vehicle/unit.

------------------------------------------------------------------------

## 2. How to Enter Unit Settings

The current Unit workflow starts from the **Unit List**.

1.  Open the Unit module.
2.  Locate the required unit.
3.  Open its Settings.
4.  Unit Settings opens for the selected unit.
5.  The selected unit's identity/context should remain consistent while
    moving between tabs.

The current Unit test suite explicitly verifies that Unit Settings opens
for the selected unit and that the selected unit context is retained
when switching tabs.

------------------------------------------------------------------------

## 3. Unit Settings Structure

Unit Settings contains five main tabs:

1.  **General**
2.  **Icon**
3.  **Sensors**
4.  **Service**
5.  **Alert**

Switching between these tabs should load the correct content without
layout or console errors.

``` text
                 UNIT LIST
                     |
               Select a Unit
                     |
                     v
               UNIT SETTINGS
                     |
       +-------------+-------------+
       |             |             |
    General         Icon        Sensors
       |                           |
       |                       Standard/
       |                         Custom
       |
       +-------------+-------------+
                     |
                  Service
                     |
       +-------------+-------------+
       |             |             |
   Pollution      Fitness      Insurance
                     |
                Vehicle Service
                     |
                  Alert
```

------------------------------------------------------------------------

# 4. General Tab

The **General** tab contains the main configuration values for the
selected unit.

The current test specification identifies these fields:

-   Serial No
-   SIM 1
-   SIM 2
-   Port No
-   Creation Date
-   Expiry Date
-   Mileage Calculation
-   Speed Limit
-   Fuel Consumption Avg
-   Fuel Consumption in Idling
-   Polyline Colour
-   Location Group

### What these fields represent

  -----------------------------------------------------------------------
  Field                               Purpose
  ----------------------------------- -----------------------------------
  Serial No                           Identifies the unit/device

  SIM 1 / SIM 2                       Stores SIM-related configuration

  Port No                             Device/communication configuration

  Creation Date                       Unit creation/reference date

  Expiry Date                         Unit expiry/reference date

  Mileage Calculation                 Controls the configured mileage
                                      calculation option

  Speed Limit                         Configured speed threshold

  Fuel Consumption Avg                Average fuel-consumption
                                      configuration

  Fuel Consumption in Idling          Idling fuel-consumption
                                      configuration

  Polyline Colour                     Configures route/polyline
                                      representation where applicable

  Location Group                      Associates the unit with a
                                      configured location group
  -----------------------------------------------------------------------

### QA focus

The General tab should be tested for:

-   Correct existing values loading.
-   Read-only fields remaining non-editable where applicable.
-   Valid numeric values.
-   Negative numeric values.
-   Non-numeric input.
-   Blank required values.
-   Excessively large numeric values.
-   Date-format validation.
-   Expiry date vs creation date.
-   Decimal speed-limit behaviour.
-   Leading/trailing spaces.
-   Saving multiple fields together.
-   Persistence after reopening and browser refresh.

For example:

``` text
Speed Limit = 50       -> Valid
Speed Limit = 50.5     -> Verify supported precision
Speed Limit = -10      -> Reject
Speed Limit = abc      -> Reject
```

The exact business rule for boundary values such as zero or equal dates
should be confirmed against the product specification rather than
assumed.

------------------------------------------------------------------------

# 5. Icon Tab

The **Icon** tab controls the visual representation of the selected
unit.

The tab contains:

-   Unit Type
-   Current Icon
-   Available Icons

### Important dependency

The selected **Unit Type** can determine which icons are available.

``` text
Change Unit Type
       |
       v
Available Icons Update
       |
       v
Select Icon
       |
       v
Click Update
       |
       v
Unit List Shows New Icon
```

### QA focus

Test:

-   Unit Type dropdown.
-   Available unit types.
-   Current icon.
-   Available icons.
-   Changing unit type before selecting an icon.
-   Rapid unit-type switching.
-   Selecting another valid icon.
-   Invalid/unavailable icon submission.
-   Cancelling an icon change.
-   Persistence after reopening.
-   Unit List reflection after successful update.

A critical cross-module check is:

> Change icon → Update → close settings → verify the Unit List shows the
> new icon.

------------------------------------------------------------------------

# 6. Sensors Tab

The **Sensors** tab manages sensor configurations associated with the
selected unit.

The current test suite distinguishes between:

-   Standard Sensors
-   Custom Sensors

It also covers sensor configuration and calibration behaviour.

A sensor list can contain information such as:

-   Sensor Name
-   Sensor Type
-   Created Date
-   Last Updated
-   Detail

### Sensor configuration

A configuration can involve:

-   Sensor Configuration Name
-   Sensor Type
-   Configuration Expression
-   Calibration Table

The configuration workflow includes controls such as:

-   Add Row
-   Clear
-   Cancel
-   Save Config

### Calibration

Calibration allows raw/input values to be mapped to meaningful output
values.

Example:

``` text
Raw value       Actual value
---------       ------------
10              20
20              40
30              60
```

The exact calculation/business rule should be verified against the
application's implementation.

### QA focus

Test:

-   Sensor list loading.
-   Empty-state behaviour.
-   Large sensor datasets.
-   Pagination.
-   Standard/custom sensor distinction.
-   Sensor configuration creation.
-   Adding one calibration row.
-   Adding multiple calibration rows.
-   Editing/removing rows where supported.
-   Saving configuration.
-   Persistence after reopening.
-   API failure handling.
-   Incorrect or incomplete configuration data.

------------------------------------------------------------------------

# 7. Service Tab

The **Service** section manages service/compliance information
associated with the unit.

The current Unit test suite identifies these service areas:

``` text
Service
 ├── Pollution
 ├── Fitness
 ├── Insurance
 └── Vehicle Service
```

------------------------------------------------------------------------

## 7.1 Pollution

Pollution-related information includes certificate and expiry
information.

The test coverage includes areas such as:

-   Certificate information.
-   Valid From.
-   Valid Till.
-   Certificate Cost.
-   Expiry Reminder Before Days.
-   Certificate upload.
-   View History.

### QA focus

Verify:

-   Required-field validation.
-   Valid date ranges.
-   Invalid/reversed dates.
-   Certificate cost validation.
-   Reminder-day validation.
-   Supported file upload.
-   Unsupported file rejection.
-   Oversized file rejection.
-   Successful save.
-   History display.

------------------------------------------------------------------------

## 7.2 Fitness

Fitness handles fitness certificate information.

The current test specification identifies:

-   Valid From
-   Valid Till
-   Certificate Cost
-   Expiry Reminder Before Days

### QA focus

Test:

-   Blank submission.
-   Invalid certificate cost.
-   Negative cost.
-   Non-numeric cost.
-   Invalid reminder days.
-   Negative reminder days.
-   Reversed validity dates.
-   Equal validity dates.
-   Boundary certificate cost.
-   Valid fitness submission.

Required-field validation and successful valid submission are
high-priority scenarios in the current test suite.

------------------------------------------------------------------------

## 7.3 Insurance

Insurance manages insurance information for the unit.

The current test specification identifies:

-   Insurance Company
-   Total Premium
-   Depreciation
-   IDV
-   Valid From
-   Valid Till
-   Expiry Reminder Before Days
-   Insurance File
-   Submit
-   View History

### QA focus

Test:

-   Blank submission.
-   Zero premium.
-   Zero depreciation.
-   Premium boundaries.
-   Depreciation boundaries.
-   IDV boundaries.
-   Invalid numeric values.
-   Invalid date ranges.
-   Reminder-day validation.
-   Unsupported files.
-   Oversized files.
-   Valid insurance submission.
-   Valid document upload.
-   Insurance history.

------------------------------------------------------------------------

## 7.4 Vehicle Service

Vehicle Service records maintenance/service activity for the unit.

The current test suite identifies:

-   Service No
-   Service Date
-   Odometer Before
-   Odometer After
-   Service Cost
-   Next Service Odometer
-   Next Service Duration
-   Reminder Before
-   Service Parts
-   Add Part
-   View History
-   Submit

### Important business relationship

Odometer values need logical progression.

Example:

``` text
Odometer Before = 10,000 km
Odometer After  = 10,500 km
```

This is logically progressive.

But:

``` text
Odometer Before = 10,000 km
Odometer After  = 9,000 km
```

should be rejected if decreasing odometer values are prohibited by the
product rules.

The current test suite explicitly treats this as a critical negative
scenario.

### Service Parts

The workflow also supports service parts.

QA should verify:

-   Adding one part.
-   Adding multiple parts.
-   Removing a part where supported.
-   Invalid/incomplete part data.
-   Persistence of parts after successful submission.

------------------------------------------------------------------------

# 8. Alert Tab

The **Alert** tab manages alert configurations associated with the
selected unit.

The current test specification identifies these columns/configuration
values:

-   Alert Name
-   Limit
-   Duration
-   SMS
-   Email
-   Notification

Example:

``` text
Overspeed Alert
    |
    +-- Limit        = configured threshold
    +-- Duration     = configured duration
    +-- SMS          = Enabled/Disabled
    +-- Email        = Enabled/Disabled
    +-- Notification = Enabled/Disabled
```

### QA focus

Test:

-   Alert tab loading.
-   Configured alerts.
-   Empty state when no alerts exist.
-   Alert count.
-   Table columns.
-   SMS status.
-   Email status.
-   Notification status.
-   Pagination.
-   Large numbers of alerts.
-   API failure.
-   Active alerts.
-   Rapid switching between tabs.

------------------------------------------------------------------------

# 9. Save, Cancel and Persistence Behaviour

This is one of the most important areas of Unit testing.

The basic lifecycle is:

``` text
Open Settings
      |
      v
Modify Value
      |
      +---- Close/Cancel ----> Change should not be persisted
      |
      v
    Update
      |
      v
Success Feedback
      |
      v
Close + Reopen
      |
      v
Saved Value Present
```

The test suite also verifies persistence after a browser refresh.

### Important scenarios

#### Successful update

``` text
Change value
    ↓
Update
    ↓
Success toast
    ↓
Reopen
    ↓
Value remains changed
```

#### Unsaved change

``` text
Change value
    ↓
Do NOT Update
    ↓
Close
    ↓
Reopen
    ↓
Original saved value should remain
```

#### Network failure

``` text
Change value
    ↓
Update
    ↓
Network failure
    ↓
Clear error feedback
    ↓
Existing saved value remains intact
```

#### Double submission

``` text
Double-click Update
        ↓
Only one update should occur
```

The current test suite specifically marks network interruption during an
update as **Critical**, and also checks duplicate submission
prevention/handling.

------------------------------------------------------------------------

# 10. Unit Context Must Never Be Lost

A major functional rule is that settings must remain tied to the unit
selected from the Unit List.

Example:

``` text
Unit A
  ↓
Open Settings
  ↓
General
  ↓
Icon
  ↓
Sensors
  ↓
Service
  ↓
Alert
```

Every tab must still represent **Unit A**.

A serious defect would be:

``` text
Select Unit A
     ↓
Open Settings
     ↓
Switch tab
     ↓
Data from Unit B appears
```

The test suite explicitly includes selected-unit-context validation.

------------------------------------------------------------------------

# 11. Error Handling

Unit Settings must not create false confidence.

When an API fails:

``` text
API Failure
     ↓
User-visible error
     ↓
No false success
     ↓
No corrupted/stale data presented as current
```

Important error scenarios include:

-   Settings API failure.
-   Update API failure.
-   Network interruption.
-   Expired session.
-   Validation failure.
-   Unsupported file.
-   Oversized file.
-   Invalid numeric input.
-   Invalid dates.

A success toast should only appear when the operation actually succeeds.

------------------------------------------------------------------------

# 12. Accessibility and Responsive Behaviour

The Unit test suite also includes usability/accessibility checks.

### Keyboard navigation

A user should be able to:

-   Reach focusable controls logically.
-   Navigate settings without requiring a mouse where applicable.
-   Activate controls from the keyboard.

### Close controls

Close buttons should:

-   Have accessible names.
-   Be reachable by keyboard.
-   Be activatable without a mouse.

### Responsive behaviour

At supported viewport sizes:

``` text
Desktop
   ↓
Tablet
   ↓
Mobile
```

Unit Settings should remain usable without:

-   Unintended overlap.
-   Hidden controls.
-   Broken layouts.
-   Inaccessible actions.

------------------------------------------------------------------------

# 13. Complete Unit Module Testing Model

For QA, divide the module into these layers:

``` text
                 UNIT MODULE
                     |
        +------------+------------+
        |            |            |
     Functional   Validation   Persistence
        |            |            |
        +------------+------------+
                     |
              Cross-Module
                     |
          +----------+----------+
          |          |          |
       Security   Accessibility Reliability
```

### Functional

Does each feature work?

### Validation

Does the system reject invalid input?

### Persistence

Does saved data remain correct after reopening/refreshing?

### Cross-module

Does a Unit change appear correctly elsewhere?

### Reliability

What happens during API/network/session failures?

### Accessibility

Can users operate the feature with keyboard/accessibility tools?

------------------------------------------------------------------------

# 14. Highest-Priority QA Areas

Based on the current Unit test suite, these deserve particular
attention:

  -----------------------------------------------------------------------
  Priority                Area                    Why
  ----------------------- ----------------------- -----------------------
  Critical                Network interruption    Prevent data
                          during update           corruption/false state

  Critical                Blank Fitness           Required validation
                          submission              

  Critical                Valid Fitness           Core workflow
                          submission              

  Critical                Blank Insurance         Required validation
                          submission              

  Critical                Valid Insurance         Core workflow
                          submission              

  Critical                Blank Vehicle Service   Required validation
                          submission              

  Critical                Invalid odometer        Protect data integrity
                          progression             

  High                    Unit context retention  Prevent editing wrong
                                                  unit

  High                    API failure handling    Prevent false success

  High                    General field           Protect configuration
                          validation              data

  High                    Icon persistence        Cross-module
                                                  consistency

  High                    Alert loading           Core unit monitoring
                                                  configuration

  High                    Expired session         Authentication/data
                          handling                integrity
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 15. A Practical QA Mental Model

When testing any Unit feature, ask these seven questions:

### 1. Can I open it?

``` text
Unit List → Unit Settings
```

### 2. Is it showing the correct unit?

``` text
Selected Unit = Displayed Unit
```

### 3. Does the UI load correctly?

``` text
Correct tab
Correct fields
Correct existing values
```

### 4. Can I enter valid data?

``` text
Valid input → Successful operation
```

### 5. Does it reject invalid data?

``` text
Invalid input → Validation/Error
```

### 6. Does the saved data persist?

``` text
Save → Reopen → Refresh → Verify
```

### 7. What happens when something goes wrong?

``` text
API failure
Network failure
Expired session
Double click
Invalid file
Invalid data
```

If you consistently apply these seven questions, your Unit testing
becomes much more systematic instead of simply clicking through the UI.

------------------------------------------------------------------------

# 16. Relationship to the Wider Asset/Fleet System

The broader Asset Management FRS describes a current-state system where
asset-related information can be distributed across separate areas such
as installations, vehicle transfers, maintenance, and vehicle usage. It
identifies fragmented navigation and the need to cross-reference asset
information across different menu areas as current-state limitations.

Therefore, when testing Unit functionality, keep the distinction clear:

-   **Unit module:** unit/device configuration and unit-specific
    settings.
-   **Asset Management:** broader asset lifecycle management.
-   **Tracking:** operational/location visibility.
-   **Reports:** historical/analytical representation of data.
-   **Alerts:** event/threshold notifications.

The current-state Asset Management FRS itself should be treated as a
baseline rather than as a specification for the redesigned system.

------------------------------------------------------------------------

# 17. Final Summary

The Trackofy Unit module can be understood as:

``` text
                         UNIT
                          |
          +---------------+---------------+
          |               |               |
       GENERAL           ICON          SENSORS
          |               |               |
     Configuration    Visual Type     Sensor Setup
          |
          +---------------+
                          |
                       SERVICE
                          |
       +----------+-------+-------+----------+
       |          |               |          |
   Pollution   Fitness       Insurance   Vehicle
                                          Service
                          |
                        ALERT
                          |
             Alert configuration
```

### The core idea

**Unit is the place where the selected tracked unit is configured and
maintained.**

It covers:

-   Basic unit configuration.
-   Visual representation.
-   Sensor configuration.
-   Compliance/service information.
-   Vehicle service history.
-   Alert configuration.
-   Persistence and update behaviour.

For QA, don't test each tab as an isolated page. Test the **entire
lifecycle**:

``` text
Select Unit
   ↓
Open Settings
   ↓
Configure
   ↓
Validate
   ↓
Save
   ↓
Verify Feedback
   ↓
Reopen
   ↓
Refresh
   ↓
Verify Persistence
   ↓
Verify Cross-Module Impact
```

That is the most useful way to understand and test the Unit module in
Trackofy.

------------------------------------------------------------------------

## Source Basis

This guide is based primarily on the uploaded
**unit_module_test_cases.csv**, which defines the current Unit module
test coverage, including General, Icon, Sensors, Service, Alert,
persistence, failure handling, accessibility, and responsive scenarios.
The current Asset Management FRS was used only for broader system
context.
