# Trackofy v6 — Video Telematics Module
## Functional Explanation, UI Structure, Workflows & Testing Scope

> **Source basis:** This document is derived from the provided Trackofy v6 Video Telematics screenshots and the functional description supplied with them. Where the screenshots show a control/state but do not establish its backend rule, the item is explicitly described as a testing expectation rather than a confirmed implementation rule.

---

# 1. Module Overview

The **Video Telematics** module is a dedicated monitoring and analytics area for vehicle-camera data, ADAS/DMS alerts, historical playback and alert reporting.

The module has a dedicated left-side navigation menu containing:

1. **Dashboard**
2. **Alert**
3. **Playback**
4. **Report**

A persistent **Live Fleet Map** widget is visible at the bottom-left of the module. A vertical **Feedback** control is also visible on the right side of the application.

The primary objective of the module is to allow an operator to:

- Monitor vehicle camera channels in real time.
- Observe the current online/offline and alert state of the fleet.
- Configure ADAS/DMS/video alerts.
- Configure alert delivery channels and delivery behavior.
- Search and play historical video recordings.
- Generate and review video telematics alert reports.
- Inspect evidence associated with individual alerts, including available video and snapshots.

---

# 2. Module Navigation

## 2.1 Video Telematics Side Menu

The left navigation panel contains:

| Menu | Purpose |
|---|---|
| Dashboard | Real-time video monitoring and fleet safety overview |
| Alert | Create, view, edit and delete video telematics alert configurations |
| Playback | Search historical recorded MDVR/video files and play them |
| Report | Generate and review ADAS/DMS alert reports and evidence |

The active menu is visually highlighted.

### Navigation testing

Verify:

- Each menu item opens the correct page.
- The selected page remains highlighted.
- Switching between pages does not unexpectedly clear global/application state.
- Browser Back/Forward behaves correctly.
- Refreshing a page does not break the module.
- Unauthorized users cannot access restricted functionality.

---

# 3. Video Telematics Dashboard

## 3.1 Purpose

The Dashboard is the real-time operational screen of the Video Telematics module.

The screenshot shows the heading:

**Video Telematics Dashboard**

with the description indicating live fleet monitoring, camera status and safety events.

A **Live Monitoring** indicator is visible in the top-right.

---

# 4. Dashboard KPI Summary

The dashboard displays a KPI strip containing fleet and alert statistics.

The screenshot shows:

- **Total Vehicles: 2**
- **Online: 0**
- **Offline: 2**
- **Alerts Today: 0**
- **Critical Alerts: 0**
- **Warning: 0**
- **Info: 0**

These values provide an immediate operational summary.

## Testing expectations

Each KPI should:

- Display the correct value from backend data.
- Update when vehicle connectivity changes.
- Update when alert events are generated.
- Handle zero values correctly.
- Handle larger fleet counts correctly.
- Remain consistent with the corresponding Report/Alert data where the business rules overlap.

### Data-consistency examples

If Total Vehicles = 2 and Online = 0, Offline should normally reconcile to the configured fleet definition.

If an alert is generated and qualifies for today's count, Alerts Today should update according to the application's refresh/event model.

---

# 5. Live Video Panel

The central dashboard contains a **Live Video** panel.

The screenshot shows:

- Live status indicator.
- Vehicle selector.
- Channel selector.
- Camera/control icons.
- Four video panes.
- Video playback controls inside each pane.

The displayed vehicle is **B123456**, and the header indicates:

**4 Channels • B123456 • IMEI 018271129907**

The dashboard therefore supports multi-camera monitoring for a selected vehicle.

## 5.1 Four-camera layout

The screenshot shows a 2 × 2 video layout:

- Camera 1
- Camera 2
- Camera 3
- Camera 4

Each video panel provides controls such as:

- Play
- Stop
- Mute/unmute
- Snapshot/camera action
- Fullscreen

The exact availability of each control should be verified against the actual stream/player implementation.

## 5.2 Vehicle selection

The vehicle selector allows the operator to select the vehicle whose video feeds should be monitored.

Test:

- Vehicle list loading.
- Correct vehicle names/identifiers.
- Selecting another vehicle.
- Vehicle with four channels.
- Vehicle with fewer/more available channels.
- Offline vehicle.
- Vehicle with no video device.
- Unauthorized vehicle.
- Vehicle switching while streams are active.

## 5.3 Channel selection

The dashboard screenshot contains a channel selector showing **4**.

Testing should verify:

- Correct channel count.
- Channel selection.
- Camera stream mapping.
- Switching channel does not display the wrong camera.
- Unavailable channel is handled gracefully.

## 5.4 Video stream states

Important states:

- Stream loading.
- Stream playing.
- Stream stopped.
- Stream unavailable.
- Device offline.
- Network interruption.
- Camera unavailable.
- Invalid stream.
- Stream timeout.

The UI should clearly communicate unavailable/loading states rather than displaying misleading active video.

---

# 6. Video Player Controls

Each live video tile contains controls.

Visible controls include:

- Play
- Stop
- Audio/mute control
- Snapshot/camera control
- Fullscreen

Testing should verify:

### Play
- Starts the selected stream.
- Does not start a different camera.
- Handles delayed stream initialization.

### Stop
- Stops the intended stream.
- Does not unintentionally stop all other channels unless designed to.

### Audio
- Toggles audio state correctly where audio is supported.
- Does not alter video playback unexpectedly.

### Snapshot
- Captures the intended camera frame.
- Uses the correct vehicle/channel/time.
- Handles snapshot failure.

### Fullscreen
- Expands the correct video pane.
- Exits fullscreen correctly.
- Does not lose the active stream.

---

# 7. Alerts & Notifications Panel

The right side of the Dashboard contains **Alerts & Notifications**.

The screenshot shows:

- Alerts & Notifications heading.
- Count indicator.
- Refresh control.
- Empty state: **No alerts found**.
- Message indicating there are no video telematics alerts today.
- **View alert history** action.

## 7.1 Alert count

The count should reflect the alerts applicable to the current dashboard context.

Test:

- Zero alerts.
- One alert.
- Multiple alerts.
- New alert arriving while dashboard is open.
- Refreshing alert data.

## 7.2 Empty state

When there are no alerts, the UI should show a clear empty state.

It must not:

- Display stale alerts.
- Display alerts belonging to another vehicle.
- Show a broken/blank panel.
- Treat zero alerts as an error.

## 7.3 View alert history

Clicking **View alert history** should take the operator to the relevant alert-history/report view according to the implemented navigation.

Verify that the resulting page/context corresponds to video telematics alert data.

---

# 8. Alert Configuration

## 8.1 Purpose

The Alert page is used to manage video telematics alert rules.

The screenshot shows:

**Alert Configuration — 106 alerts**

The page provides:

- Vehicle filter.
- Priority filter.
- Add Alert button.
- Rows/page selector.
- Pagination.
- Export controls.
- Search alerts.
- Alert configuration table.

---

# 9. Alert Configuration Table

The observed columns are:

| Column | Purpose |
|---|---|
| Sr No | Sequential record number |
| Category | Alert category, e.g. ADAS |
| Vehicle | Vehicle to which configuration applies |
| Alert | Configured alert/event |
| Priority | Critical/Warning etc. |
| WhatsApp | Whether WhatsApp delivery is enabled |
| Email | Whether Email delivery is enabled |
| Delivery | Real-time/interval and cooldown information |
| Status | Enabled/disabled state |
| Edit | Edit configuration |
| Delete | Delete configuration |

The screenshot includes alerts such as:

- Impacting Pedestrians Start
- Impacting Vehicle Start
- Forward Collision Alarm Level Two Start
- Pedestrian Collision Alarm Level Two Start
- Car Distance Near Alarm Level Two Start

---

# 10. Alert Filters

The Alert page provides:

### Vehicle filter

Default observed state:

**All vehicles**

Testing:

- Select one vehicle.
- Select another vehicle.
- Verify filtering.
- Verify no cross-vehicle results.
- Reset to All vehicles.

### Priority filter

Default observed state:

**All priorities**

Test:

- Critical.
- Warning.
- Any additional supported priorities.
- All priorities.
- Empty result.

### Search

The search field is labeled:

**Search alerts...**

Test:

- Exact alert name.
- Partial alert name.
- Vehicle identifier.
- Category.
- No-result search.
- Case handling.
- Special characters.
- Search combined with filters.

---

# 11. Create Video Alert

The **Create Video Alert** dialog is a configuration workflow.

The screenshot shows the following sections:

1. Vehicle Selection
2. Alert Configuration
3. Delivery Channels
4. Delivery
5. Status

A **Create Alert** button is present at the bottom.

---

# 12. Vehicle Selection in Alert Creation

The dialog contains:

**Vehicle Selection**

with:

- Select Vehicles control.
- Selected-count indicator.
- Dropdown.

The screenshot initially shows:

**0 selected**

Testing should cover:

- One vehicle.
- Multiple vehicles if supported.
- Removing selections.
- Selected count accuracy.
- Empty selection.
- Unauthorized vehicle.
- Large vehicle list.
- Search within vehicle list if supported.
- Duplicate vehicle selection.

---

# 13. Alert Configuration

The configuration section contains:

- **Alerts***
- **Priority***

The screenshot shows Priority set to:

**Warning**

The alert field appears as a dropdown.

Testing:

- Alert field required validation.
- Alert selection.
- Priority selection.
- Critical priority.
- Warning priority.
- Any additional configured priority.
- Changing priority before submission.
- Correct saved value after creation.

---

# 14. Delivery Channels

The Create Video Alert form provides delivery-channel checkboxes.

Observed channels:

- **Application**
- **Email**
- **WhatsApp**

The screenshot shows Application and WhatsApp selected, while Email is not selected.

Testing should verify:

- Each channel independently.
- Multiple channels together.
- All channels.
- No channels.
- Channel persistence after editing.
- Channel display in the configuration table.

For example, a configuration showing WhatsApp = Yes and Email = No should match the underlying configuration.

---

# 15. Delivery Mode

The form contains:

- **Real time**
- **Interval**

The screenshot shows **Real time** selected.

## 15.1 Real-time delivery

When Real time is selected, the alert should follow the application's real-time delivery behavior.

The screenshot also shows:

**Cooldown Minutes: 30**

Testing should verify:

- Cooldown value accepts valid input.
- Zero value handling.
- Minimum value.
- Maximum supported value.
- Decimal/negative values if applicable.
- Non-numeric values.
- Cooldown persistence.

## 15.2 Interval delivery

If Interval is selected, verify:

- Interval configuration becomes available where applicable.
- Real-time-only fields are enabled/disabled appropriately.
- Saved configuration reflects interval mode.
- Generated alerts follow the configured interval.

---

# 16. Status

The Create Video Alert dialog contains a Status section.

The screenshot shows:

**Enabled**

as a selected checkbox.

Testing:

- Create enabled alert.
- Create disabled alert if supported.
- Edit enabled → disabled.
- Edit disabled → enabled.
- Verify status in table.
- Verify disabled rules do not generate notifications if that is the intended business behavior.

---

# 17. Create Alert Submission

A successful configuration should:

1. Validate mandatory fields.
2. Create the alert configuration.
3. Close the dialog or provide the configured success behavior.
4. Refresh/update the Alert table.
5. Display the newly created rule.
6. Preserve vehicle, alert, priority, delivery channels, delivery mode, cooldown and status.

### Duplicate submission

Rapid/double clicking **Create Alert** must not create duplicate configurations.

### API failure

If the create request fails:

- The UI must show an appropriate error.
- No false success message should be displayed.
- The dialog should preserve data where practical.
- The user should be able to retry safely.

---

# 18. Edit Alert

The Alert table provides an Edit icon for every configuration.

Editing should load the selected alert's existing configuration.

Verify that the edit form contains the correct:

- Vehicle.
- Alert type.
- Priority.
- Delivery channels.
- Delivery mode.
- Cooldown.
- Status.

After saving:

- Only the selected configuration should change.
- Other configurations must remain unchanged.
- Table values must reflect the new state.

---

# 19. Delete Alert

The table provides a Delete action.

Testing should cover:

- Delete an existing alert.
- Delete confirmation behavior if implemented.
- Cancel deletion.
- Successful deletion.
- Failed deletion.
- Repeated deletion.
- Attempt to delete a record that has already been removed.
- Table refresh after deletion.
- Record count update.

A delete action must never remove a different alert configuration.

---

# 20. Alert Export & Table Utilities

The Alert page shows several table utility icons, including export/print/copy-style actions.

Testing should verify:

- Correct data is exported.
- Applied filters are reflected where expected.
- Export does not include unauthorized records.
- Exported columns correspond to the visible/configured table.
- Large result sets export correctly.
- Export handles empty results.
- Search/filter state behaves correctly with export.

---

# 21. Playback

## 21.1 Purpose

Playback is used to search historical recorded MDVR files and review vehicle video.

The page heading is:

**Video Playback**

The screenshot shows:

**0 files**

and the description indicates that recorded MDVR files can be searched and vehicle playback reviewed.

---

# 22. Playback Filters

The filter area contains:

- Vehicle
- Channel
- Date
- From Time
- To Time
- Find Files
- Reset

Observed values include:

- Vehicle: B123459 / IMEI 108270989565
- Channel: All Channels
- Date: 02/09/2026
- From Time: 00:00:00
- To Time: 23:59:59

## 22.1 Vehicle

Test:

- Select valid vehicle.
- Change vehicle.
- Offline vehicle.
- Vehicle without recordings.
- Unauthorized vehicle.
- Vehicle with recordings.

## 22.2 Channel

Observed default:

**All Channels**

Test:

- All Channels.
- Individual channel.
- Invalid/unavailable channel.
- Channel-specific recording retrieval.

## 22.3 Date

Test:

- Current date.
- Historical date.
- Future date.
- Date with recordings.
- Date without recordings.
- Invalid date if input manipulation is possible.

## 22.4 Time range

Test:

- Full-day range.
- Start = end.
- Start < end.
- Start > end.
- 00:00:00.
- 23:59:59.
- Invalid time.
- Boundary seconds.

---

# 23. Find Files

The **Find Files** action retrieves recordings matching the selected filters.

Expected behavior:

- Valid criteria return matching files.
- No matching records show a clear empty state.
- Loading state is displayed while searching.
- Repeated searches replace/refresh the result appropriately.
- Search failures are communicated clearly.

The screenshot currently shows:

**No playback files found**

and:

**No playback selected**

This is a valid empty state and should not be treated as a playback failure by itself.

---

# 24. Playback Files Panel

The left content panel is titled:

**Playback Files**

It displays the selected vehicle/date context and the number of files.

When recordings exist, the expected workflow is:

1. Search files.
2. View returned recordings.
3. Select a recording.
4. Load it into Playback Video.
5. Play/review the recording.

Testing should verify correct file-to-vehicle/date/channel mapping.

---

# 25. Playback Video Panel

The right panel is titled:

**Playback Video**

When no recording is selected, it shows:

**No playback selected**

with guidance to search recorded files and select one from the Playback Files panel.

Testing should verify:

- Correct selected file is loaded.
- Video begins from the expected position.
- Play/pause works.
- Seek behavior works if supported.
- Fullscreen works.
- Video loading failures are handled.
- Switching between files updates the player correctly.
- A file from Vehicle A never plays for Vehicle B due to selection/state mismatch.

---

# 26. Video Telematics Reports

## 26.1 Purpose

The Report page provides historical ADAS/DMS alert reporting with notification and evidence information.

The screenshots show report counts such as:

- **98 records**
- **89 records**

The count changes depending on the selected report filters/data state.

The page description states that it is used to review:

- ADAS/DMS alert history.
- Evidence.
- Notification activity.

---

# 27. Report Filters

The Report page includes:

- From Date
- To Date
- Vehicle
- Alert Type
- Notification
- Report Data
- Clear All
- Generate Report

A second screenshot shows the filters collapsed into chips such as:

- Date range.
- All Vehicles.
- All Alerts.

The interface therefore supports both detailed filter controls and an active-filter summary.

---

# 28. Date Filtering

Test:

- Same-day report.
- Multi-day report.
- Start date < end date.
- Start date = end date.
- Start date > end date.
- Future date.
- Historical date.
- Boundary dates.
- Date format.
- Timezone-related date behavior.

Verify that only records within the requested range are returned.

---

# 29. Vehicle Filter

The report supports vehicle selection.

Test:

- All Vehicles.
- Single vehicle.
- Multiple vehicles if supported.
- Vehicle with no alerts.
- Unauthorized vehicle.
- Combination with Alert Type and Notification filters.

The report rows must correspond to the selected vehicle criteria.

---

# 30. Alert Type Filter

The screenshot shows:

**All Alerts**

Testing should include:

- All Alerts.
- Individual alert type.
- ADAS alerts.
- DMS alerts if configured.
- Alert type with no records.
- Combination with date and vehicle filters.

---

# 31. Notification Filter

The Report page contains a Notification filter.

The screenshots show notification states such as:

- **SENT**
- **SKIPPED**

Testing should verify that filtering by notification state returns only records matching the selected notification condition.

---

# 32. Report Data / Evidence Filter

The Report page contains a Report Data filter.

The screenshot shows **Evidence** as a selected report-data context.

Rows may show:

- Evidence available.
- No Evidence.

This distinction is important because an alert record can exist even when evidence is unavailable.

---

# 33. Generate Report

The **Generate Report** button applies the selected criteria and retrieves/builds the report.

Testing should cover:

- Default filters.
- One filter.
- Multiple filters.
- Clear All → Generate.
- Valid date range.
- Invalid date range.
- No matching records.
- Large result set.
- Repeated generation.
- API failure.
- Slow response/loading state.

The displayed record count must update consistently after generation.

---

# 34. Report Table

The observed report columns are:

| Column | Purpose |
|---|---|
| Sr No | Sequential record number |
| Vehicle | Vehicle number and device/IMEI |
| Date / Time | Time of alert event |
| Category | ADAS/DMS category |
| Alert | Specific safety event |
| Location | Alert location/address |
| Notification | Delivery status |
| Evidence | Available evidence/actions |

Examples visible in the screenshots include:

- Forward Collision Warning (L1)
- Following Too Close (L1)
- Speeding
- Lane Departure (L1)

The category is shown as **ADAS** in the provided records.

---

# 35. Vehicle Information in Report

Each row displays:

- Vehicle identifier.
- Device/IMEI beneath it.

Testing should verify:

- Correct vehicle.
- Correct associated IMEI/device.
- No mismatch between vehicle and device.
- Correct filtering.
- Correct sorting if sorting is supported.

---

# 36. Date / Time

Each alert row contains a date/time value.

Examples visible include timestamps around:

- 04/09/26 20:17:29
- 04/09/26 20:18:07
- 04/09/26 20:19:03

Testing should verify:

- Correct event timestamp.
- Correct date formatting.
- Chronological ordering if intended.
- Timezone consistency.
- Boundary events around midnight.
- Correct timestamp in exported report/evidence metadata.

---

# 37. Location

The Location column shows a map-pin icon and text such as:

**Load address...**

This suggests address information may be loaded/resolved separately from the event coordinates.

Testing should cover:

- Location loads correctly.
- Loading state.
- Valid address.
- Missing address.
- Coordinate with no address.
- Invalid coordinate.
- Location click behavior if implemented.
- Correct vehicle/event location.

---

# 38. Notification Status

The screenshots show:

### SENT

A green status indicating notification activity has been sent.

### SKIPPED

A neutral status indicating notification delivery was skipped.

Testing should verify:

- Status matches backend notification state.
- SENT appears only when notification was actually sent.
- SKIPPED is shown for the correct reason/state.
- Filter results match the status.
- Status does not change incorrectly after refresh.

---

# 39. Evidence Actions

This is one of the most important parts of the Report module.

In the first report screenshot, the Evidence column displays **three action icons** for records with evidence:

1. **View all evidence**
2. **View all snapshots**
3. **Play video**

These provide different ways to inspect the evidence associated with the alert.

---

# 40. View All Evidence

The eye icon represents the ability to view the available evidence for the selected alert.

Testing should verify:

- Correct alert evidence opens.
- Evidence belongs to the correct vehicle.
- Evidence belongs to the correct timestamp/event.
- Multiple evidence items are displayed correctly.
- Missing evidence is handled gracefully.
- Unauthorized evidence cannot be accessed.

---

# 41. View All Snapshots

The image/picture icon represents snapshot evidence.

Testing should verify:

- Correct snapshots are displayed.
- Snapshot corresponds to the selected alert.
- Multiple snapshots are shown where available.
- Image loading errors are handled.
- Full-size image behavior works if implemented.
- Download behavior works if supported.
- Unauthorized snapshots cannot be accessed.

---

# 42. Play Video

The play icon represents video evidence/playback.

Testing should verify:

- Correct video is opened.
- Video corresponds to the alert event.
- Correct vehicle is shown.
- Correct timestamp/event is represented.
- Video loads successfully.
- Play/pause works.
- Seek/fullscreen work if supported.
- Missing video is handled.
- Unauthorized video access is prevented.

---

# 43. No Evidence State

The later screenshot shows rows where:

**Notification: SKIPPED**

and:

**Evidence: No Evidence**

are displayed as text/status rather than the three evidence-action icons.

This is an important functional state.

The application must distinguish between:

- Alert with evidence.
- Alert without evidence.

It must not display broken evidence controls for records that have no evidence.

---

# 44. Report Search

The Report page contains:

**Search report...**

Testing should cover:

- Exact vehicle.
- Partial vehicle.
- Alert name.
- Category.
- Device/IMEI.
- No-result search.
- Case handling.
- Special characters.
- Search after filters.
- Search combined with pagination.

---

# 45. Pagination & Rows

The screenshots show:

**Rows 50**

and:

**1–50 / 89**

or:

**1–50 / 98**

Testing should verify:

- Default page size.
- Changing page size.
- Next page.
- Previous page.
- First page.
- Last page.
- Correct record count.
- Pagination after filtering.
- Pagination after searching.
- Pagination after generating a new report.

Boundary conditions:

- 0 records.
- 1 record.
- Exactly page-size records.
- Page-size + 1.
- Large datasets.

---

# 46. Report Export

The Report toolbar contains multiple export/utility controls.

Testing should verify each available export action independently.

General checks:

- Export contains correct filtered data.
- Export does not expose unauthorized data.
- Headers match the selected report.
- Date/time values are correct.
- Vehicle/device values are correct.
- Notification state is correct.
- Evidence-related information is represented appropriately.
- Empty reports export safely or show the intended message.

---

# 47. Clear All

**Clear All** should remove the currently applied report filters.

Verify:

- Date filters reset.
- Vehicle resets to all/default.
- Alert type resets.
- Notification resets.
- Report data resets.
- Active filter chips disappear/update.
- Results return to the intended default state only when the application requires regeneration.

Do not assume that clearing controls automatically regenerates data unless that behavior is actually implemented.

---

# 48. Live Fleet Map

A floating **Live Fleet Map** widget is visible at the bottom-left of the Video Telematics UI.

The provided screenshot shows:

- Map/Live Fleet Map title.
- LIVE indicator.
- Vehicle count.
- Map view.
- Map/Hybrid controls.
- Map interaction tools.
- A vehicle cluster/marker.
- Fullscreen control.

The map provides geographic context alongside video telematics monitoring.

Testing should include:

- Map loads.
- Vehicle markers load.
- Marker count is accurate.
- Vehicle selection.
- Map/Hybrid switching.
- Zoom.
- Pan.
- Fullscreen.
- No-location state.
- Multiple vehicle clustering.
- Offline vehicle representation.
- Map API failure.
- Slow map loading.

---

# 49. Cross-Module Workflows

The strongest testing approach should not treat Dashboard, Alert, Playback and Report as isolated pages.

## Workflow 1 — Alert → Dashboard

1. Create an alert rule.
2. Ensure it is enabled.
3. Trigger/receive a matching event.
4. Verify dashboard alert count/state.
5. Verify notification state.
6. Verify report entry.

## Workflow 2 — Alert → Report → Evidence

1. Trigger an ADAS/DMS alert.
2. Confirm alert configuration.
3. Generate report.
4. Locate the alert.
5. Open evidence.
6. Open snapshots.
7. Play video.
8. Verify all evidence belongs to the same event.

## Workflow 3 — Vehicle → Playback

1. Select vehicle.
2. Select date/time.
3. Search files.
4. Select recording.
5. Play recording.
6. Verify correct vehicle/channel/time.

## Workflow 4 — Report → Playback/Evidence

Where the implementation links report evidence to playback:

1. Open alert report.
2. Select video evidence.
3. Verify the correct recording opens.
4. Compare event timestamp with report timestamp.

---

# 50. Security Testing

Video Telematics contains sensitive operational data and video evidence, so security testing is high priority.

## Authorization

Verify that a user cannot:

- View another customer's vehicle.
- View another customer's video.
- View another customer's snapshots.
- View another customer's alert configurations.
- Edit another customer's alert.
- Delete another customer's alert.
- Download another customer's report.

## Direct URL/API access

Attempt to access:

- Alert records by ID.
- Evidence by ID.
- Video by ID/path.
- Snapshot by ID/path.
- Playback files.
- Report data.

The server must enforce authorization rather than relying only on UI visibility.

## Input security

Test:

- XSS in search.
- XSS in alert-related fields where text input exists.
- SQL injection in search/filter parameters.
- Parameter tampering.
- IDOR/BOLA against vehicle, alert, report and evidence identifiers.

## Video/file security

Verify:

- Unauthorized stream URLs are inaccessible.
- Evidence URLs are not publicly accessible without authorization.
- Expired/invalid evidence URLs fail safely.
- Predictable file identifiers cannot be abused to retrieve another account's files.

---

# 51. Performance Testing Areas

The module has several performance-sensitive operations.

### Dashboard

- Initial dashboard load.
- Multiple simultaneous camera streams.
- Vehicle switching.
- Refreshing KPI/alerts.
- Long-running monitoring session.

### Alert

- Loading 100+ configurations.
- Searching.
- Filtering.
- Creating/editing.
- Pagination.

### Playback

- Searching large recording ranges.
- Loading large recordings.
- Switching recordings.
- Video buffering.

### Report

- Large alert datasets.
- Report generation.
- Filtering.
- Exporting.
- Evidence loading.

---

# 52. Reliability & Failure Scenarios

Test behavior when:

- Video device goes offline.
- Camera stream disconnects.
- Internet connection drops.
- API request times out.
- Report generation fails.
- Evidence service fails.
- Snapshot fails.
- Video file is unavailable.
- Map service fails.
- Notification service fails.
- User session expires during an operation.

The application should provide useful error states without corrupting existing data or reporting false success.

---

# 53. Accessibility & UX

Verify:

- Keyboard navigation.
- Visible focus.
- Accessible dropdowns.
- Accessible checkboxes/radio controls.
- Meaningful labels for icons.
- Tooltips for icon-only actions.
- Sufficient contrast.
- Readable status badges.
- Dialog keyboard handling.
- Screen-reader-friendly labels where supported.
- Responsive behavior.

Particular attention should be given to the evidence icons because they are icon-only actions and can be ambiguous without accessible labels/tooltips.

---

# 54. Test Data Requirements

Prepare:

- Online vehicle.
- Offline vehicle.
- Vehicle with four cameras.
- Vehicle with unavailable camera.
- Vehicle with recorded playback.
- Vehicle without playback.
- Vehicle with ADAS alerts.
- Vehicle with DMS alerts if configured.
- Alert with evidence.
- Alert without evidence.
- Alert with snapshots.
- Alert with video.
- Alert with notification SENT.
- Alert with notification SKIPPED.
- Critical alert.
- Warning alert.
- Enabled alert rule.
- Disabled alert rule.
- Multiple vehicles.
- Large alert/report dataset.

---

# 55. Recommended Priority

| Priority | Coverage |
|---|---|
| Critical | Authorization, evidence access, video access, alert deletion, alert creation integrity, session/security |
| High | Live monitoring, alert CRUD, playback search/playback, report generation, evidence actions |
| Medium | Search, pagination, exports, map interactions, UI validation |
| Low | Minor visual inconsistencies and non-blocking presentation issues |

---

# 56. Definition of Done

Video Telematics should be considered adequately tested only after:

- Dashboard navigation works.
- KPI values are accurate.
- Live video vehicle/channel selection works.
- All four camera panels behave correctly.
- Video controls work.
- Dashboard alerts update correctly.
- Alert configurations can be created.
- Alert configurations can be edited.
- Alert configurations can be deleted safely.
- Priority and vehicle filters work.
- Delivery channels work correctly.
- Real-time/interval delivery behavior is correct.
- Cooldown configuration is validated.
- Enabled/disabled status works.
- Playback filters work.
- Playback files are correctly retrieved.
- Correct playback video is selected and played.
- Reports generate correctly.
- Report filters work independently and in combination.
- Pagination/search work correctly.
- Export functions produce correct data.
- Evidence actions open the correct evidence.
- Snapshot actions display correct snapshots.
- Video evidence plays the correct recording.
- No-evidence states are handled correctly.
- Live Fleet Map works correctly.
- Cross-module workflows are validated.
- Cross-account access is blocked.
- Evidence/video/file authorization is verified server-side.
- XSS/SQL injection/IDOR/BOLA tests are performed.
- Failure and timeout scenarios are covered.
- Responsive and accessibility checks are completed.
