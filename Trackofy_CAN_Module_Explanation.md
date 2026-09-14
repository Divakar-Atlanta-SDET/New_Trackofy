# Trackofy CAN Module — Functional Explanation

## 1. Overview

The **CAN (Controller Area Network)** module provides vehicle-bus insights, fleet monitoring, trend analysis, reporting, alert history, and alert configuration.

### Side Menu

1. Dashboard
2. Unit
3. Trends
4. Reports
5. Alerts
6. Settings

The screenshots also show a persistent **Live Fleet Map** that can remain minimized or be expanded.

---

## 2. Dashboard

The CAN Dashboard gives a fleet-level overview of CAN-enabled assets.

### KPI Cards

The dashboard displays summary KPIs including:

- Total Assets
- Online / Reporting
- Offline / Stale
- Protocols
- Active Alerts

The provided screenshot shows an example of **14 total assets**, **4 online/reporting**, **10 offline/stale**, **5 protocols**, and **1810 active alerts**.

### Protocol Wise Assets

A bar chart shows the distribution of assets across CAN protocols.

### Online vs Offline

A donut chart compares online and offline/stale assets and shows the total fleet count.

### Recent Alerts

A Recent Alerts panel displays recent CAN events with information such as:

- Metric/alert name
- Unit
- Protocol
- Timestamp
- Warning/Critical level
- Actual value
- Limit
- Message

A **View All** action opens the complete alert list.

### CAN Unit Table

A CAN unit table is available below the dashboard and follows the module's common table pattern, including export, search, and pagination capabilities.

---

## 3. AI Fleet Summary

The Dashboard contains an **AI Summary** action.

The screenshot shows an AI Fleet Summary panel containing:

- Vehicles requiring urgent attention
- Total CAN-enabled units
- Units reporting within 24 hours
- Offline/stale units
- Open alerts
- Critical and warning alert counts
- Frequently occurring alert information
- Fleet vital metrics
- Highlights

Example fleet vital metrics visible in the screenshot include:

- B2T Battery Average Temperature
- Cool Set Temp
- T2B Ambient Temperature
- B2T Battery Max Temperature
- Heat Set Temp

The AI panel provides a concise interpretation of the dashboard data.

---

## 4. Unit

The **Unit** page contains the CAN-enabled unit list.

### Table Information

The screenshot shows columns for:

- S.No
- Unit
- IMEI
- Protocol
- Type
- Last Contact
- Params (Live / Total)
- Values
- Status
- Action

### Functions

The page supports:

- Search
- Refresh
- Apply Filter
- Export
- Pagination
- Sorting
- Opening/viewing an individual unit

### Filter Panel

The Unit filter panel contains:

- Protocol
- Status
- Search

It provides **Reset** and **Apply** controls.

---

## 5. Trends

The **Trends** page is used to compare CAN metric trends across selected units.

### Data & Chart Settings

The configuration area contains:

- Protocol
- Units
- From Date
- From Time
- To Date
- To Time
- Chart Type
- Show Markers
- Normalize (mixed units)

The screenshot shows **Line** as the selected chart type.

### Metric Trend

After the configuration is applied, the page generates a Metric Trend section containing the selected metric data for the selected units.

The screen indicates that one metric can be plotted for each selected unit, with each unit represented separately.

### Important Functional Areas

Testing should cover:

- Protocol and unit dependency
- Valid/invalid date ranges
- Time validation
- Multiple unit selection
- Metric selection
- Chart type changes
- Marker enable/disable
- Mixed-unit normalization
- No-data scenarios
- Large date ranges
- Chart and tooltip accuracy

---

## 6. Reports

The **Reports** section generates CAN reports for one or more devices.

### Report Settings

The form contains:

- Protocol
- Units / Devices
- From Date
- From Time
- To Date
- To Time

The screenshot shows an **All selected (14)** device selection state.

### Generate Report

After the required settings are supplied, the user selects **Generate Report** to generate the requested CAN data.

### Report Functions

The generated report follows the common table pattern and supports:

- Export
- Search
- Pagination

---

## 7. Alerts

The **Alerts** page provides the CAN warning and critical alert log.

The screenshot shows an example of **1810 alerts**.

### Alert Table

Visible columns include:

- S.No
- Level
- Unit
- IMEI
- Protocol
- Metric
- Actual
- Limit
- Message
- Last Contact

### Alert Levels

The interface uses:

- Warning
- Critical

### Functions

The alert table supports:

- Search
- Refresh
- Apply Filter
- Export
- Sorting
- Pagination

### Filter Panel

The filter panel contains:

- Protocol
- Level
- Unit

with **Reset** and **Apply Filter** actions.

---

## 8. Settings

The **Settings** section is used to create and manage CAN alert rules.

The screenshot shows **13 configured rules**.

### Alert Configuration Form

Fields include:

- Protocol
- Unit
- Metric
- Mode
- Warning Limit
- Critical Limit
- Notification method

The visible notification channels are:

- Application
- Email

The form provides **Reset** and **Save**.

### Configured Alert Rules

The rules table contains:

- S.No
- Unit
- Metric
- Mode
- Warning
- Critical
- Notify
- Status
- Actions

Configured rules can be:

- Activated/deactivated using a toggle
- Deleted using the red trash icon
- Searched
- Exported
- Navigated using pagination

---

## 9. Live Fleet Map

A minimized **Live Fleet Map** is available throughout the CAN module.

It can be expanded in two ways.

### A. Drag and Reposition

The floating map can be dragged from one position to another.

### B. Maximize

The map can be maximized into a larger fleet-monitoring view.

The expanded map contains:

- Vehicle status categories
- Google map
- Vehicle markers/clusters
- Alerts & Notifications panel
- Map controls
- Vehicle selection

The screenshots show status categories such as:

- Active
- Running
- Idle
- Stopped
- No Data
- BMS
- Video

---

## 10. Vehicle Popup

When a vehicle is selected on the map, a popup appears with vehicle information.

The screenshot shows:

- Vehicle/unit name
- Current status
- Speed
- Last Contact
- Location

The popup provides:

- Playback
- Alerts
- Tracking
- Details
- Focus on map

This provides a direct path from fleet visualization to vehicle-specific functions.

---

## 11. Alerts & Notifications on Map

The maximized map includes an **Alerts & Notifications** panel.

The panel provides:

- Alerts tab
- Acknowledged tab
- Notification/alert filtering
- View all alerts
- Live status

When there are no alerts, the interface displays an empty state such as:

> No Alerts Today

---

## 12. Common UI/UX Patterns

Across the screenshots, the CAN module consistently uses:

### Tables

- Search
- Export
- Pagination
- Sorting where applicable
- Refresh
- Filters
- Row actions

### Filters

Filter drawers/panels generally contain dropdowns and provide:

- Reset
- Apply
- Close

### Status Badges

The UI uses badges for states such as:

- Online
- Offline
- Active
- Warning
- Critical

### Empty States

Screens with no applicable data use dedicated empty-state messaging rather than leaving the area blank.

---

## 13. Functional Flow

```text
CAN
│
├── Dashboard
│   ├── KPI Cards
│   ├── Protocol Wise Assets
│   ├── Online vs Offline
│   ├── Recent Alerts
│   ├── CAN Unit Table
│   └── AI Fleet Summary
│
├── Unit
│   ├── Unit List
│   ├── Search
│   ├── Filters
│   ├── Export
│   ├── Pagination
│   └── Unit View
│
├── Trends
│   ├── Protocol
│   ├── Units
│   ├── Date/Time
│   ├── Chart Settings
│   └── Metric Trend
│
├── Reports
│   ├── Protocol
│   ├── Units/Devices
│   ├── Date/Time
│   ├── Generate Report
│   ├── Search
│   ├── Export
│   └── Pagination
│
├── Alerts
│   ├── Alert Log
│   ├── Search
│   ├── Filters
│   ├── Export
│   ├── Sorting
│   └── Pagination
│
└── Settings
    ├── Alert Configuration
    │   ├── Protocol
    │   ├── Unit
    │   ├── Metric
    │   ├── Mode
    │   ├── Warning Limit
    │   ├── Critical Limit
    │   └── Notifications
    │
    └── Configured Rules
        ├── Search
        ├── Export
        ├── Pagination
        ├── Activate/Deactivate
        └── Delete
```

---

## 14. Overall Summary

The CAN module covers the complete CAN monitoring lifecycle:

**Fleet Overview → Unit Data → Trend Analysis → Reports → Alert History → Alert Configuration → Live Vehicle Monitoring**

| Section | Main Purpose |
|---|---|
| Dashboard | Fleet-level CAN health, KPIs, charts and recent alerts |
| Unit | View CAN-enabled units and their current data/status |
| Trends | Analyze CAN metrics across selected units |
| Reports | Generate CAN data reports |
| Alerts | View warning/critical CAN alert history |
| Settings | Configure CAN metric thresholds and notifications |
| Live Fleet Map | Track and interact with vehicles while using CAN |

## Screenshot Analysis

The supplied screenshots confirm a consistent Trackofy design language:

- Left-side module navigation remains persistent.
- Page headers clearly identify the active CAN function.
- Data-heavy pages use structured tables with search/export/pagination.
- Configuration pages use grouped form sections.
- Dashboard pages prioritize KPI cards and visual summaries.
- The AI Summary is presented as a dedicated side panel.
- The Live Fleet Map is implemented as a floating utility and can become a full monitoring workspace.
- Vehicle selection on the map exposes contextual actions such as Playback, Alerts, Tracking, Details, and Focus on map.
- Alert severity and operational status are communicated using compact visual badges.
