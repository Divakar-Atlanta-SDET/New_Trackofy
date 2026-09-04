import json
from pathlib import Path
from typing import Any

from config.config import REPORT_TEST_DRIVER_NAME, REPORT_TEST_VEHICLE_NAME

DATA_DIR = Path(__file__).parent.parent / "test_data"

DEFAULT_DATASETS = {
    "unit_positive.json": {
        "valid_speed_limits": [
            {"value": "50", "description": "Standard city speed limit"},
            {"value": "60", "description": "Expressway speed limit"},
            {"value": "80", "description": "Highway speed limit"}
        ],
        "valid_fuel_avg": [
            {"value": "10.0", "description": "Standard heavy vehicle fuel average"},
            {"value": "12.5", "description": "Light commercial vehicle fuel average"}
        ],
        "valid_fuel_idle": [
            {"value": "0.5", "description": "Standard idling fuel consumption"},
            {"value": "1.2", "description": "Heavy idling fuel consumption"}
        ],
        "valid_fitness_certificates": [
            {"cost": "1500", "reminder": "15", "description": "Standard fitness certificate update"}
        ],
        "valid_pollution_certificates": [
            {"cost": "500", "cert_no": "PUC-2026-99", "description": "Standard pollution certificate update"}
        ]
    },
    "unit_negative.json": {
        "invalid_speed_limits": [
            {"value": "-10", "description": "Negative integer speed limit"},
            {"value": "-50", "description": "Large negative speed limit"},
            {"value": "abc", "description": "Alphabetic non-numeric speed limit"},
            {"value": "!@#$", "description": "Special characters speed limit"}
        ],
        "invalid_fuel_inputs": [
            {"value": "-5", "description": "Negative fuel consumption"},
            {"value": "xyz", "description": "Non-numeric fuel average"}
        ],
        "blank_form_submissions": [
            {"form_type": "Fitness", "description": "Blank fitness form submission"},
            {"form_type": "Pollution", "description": "Blank pollution certificate submission"}
        ]
    },
    "unit_functional.json": {
        "unit_type_filters": [
            {"unit_type": "Car", "description": "Filter by Car unit type"},
            {"unit_type": "Bus", "description": "Filter by Bus unit type"},
            {"unit_type": "Truck", "description": "Filter by Truck unit type"},
            {"unit_type": "Scooty", "description": "Filter by Scooty unit type"}
        ],
        "search_keywords": [
            {"keyword": "Bus", "description": "Search by Bus keyword"},
            {"keyword": "Truck", "description": "Search by Truck keyword"}
        ],
        "settings_tabs": [
            {"tab": "General"},
            {"tab": "Icon"},
            {"tab": "Sensors"},
            {"tab": "Service"},
            {"tab": "Alert"}
        ]
    },
    "unit_edgecase.json": {
        "boundary_speed_limits": [
            {"value": "0", "description": "Zero speed limit boundary"},
            {"value": "50.5", "description": "Decimal speed limit boundary"}
        ],
        "whitespace_padded_inputs": [
            {"value": "  50  ", "expected_trimmed": "50", "description": "Leading and trailing whitespace"}
        ],
        "duplicate_sensor_names": [
            {"sensor_name": "Fuel Sensor 1", "description": "Duplicate sensor name submission"}
        ]
    },
    "tracking_positive.json": {
        "valid_split_screens": [
            {"option": "No", "description": "Default single screen view"},
            {"option": "2 Screens", "description": "Dual split screen layout"},
            {"option": "4 Screens", "description": "Quad split screen layout"}
        ],
        "valid_date_ranges": [
            {"from_date": "31/08/2026", "to_date": "31/08/2026", "description": "Same day playback range"},
            {"from_date": "30/08/2026", "to_date": "31/08/2026", "description": "Multi-day playback range"}
        ],
        "valid_hold_times": [
            {"option": "> 5 Minutes", "description": "Hold time greater than 5 minutes"},
            {"option": "> 10 Minutes", "description": "Hold time greater than 10 minutes"}
        ],
        "valid_overspeed_thresholds": [
            {"option": "> 50 KM/H", "description": "Overspeed threshold 50 km/h"},
            {"option": "> 60 KM/H", "description": "Overspeed threshold 60 km/h"}
        ]
    },
    "tracking_negative.json": {
        "invalid_date_ranges": [
            {"from_date": "31/08/2026", "to_date": "01/08/2026", "description": "From date later than To date"},
            {"from_date": "31/12/2026", "to_date": "31/08/2026", "description": "Future From date with past To date"}
        ],
        "invalid_time_ranges": [
            {"from_time": "18:00", "to_time": "09:00", "description": "From time later than To time on same date"}
        ]
    },
    "tracking_functional.json": {
        "view_presets": [
            {"preset": "Map Focus", "description": "Map-only view preset"},
            {"preset": "Playback View", "description": "Map + Bottom panel preset"}
        ],
        "trail_colors": [
            {"color": "#087EA4", "description": "Default cyan trail color"},
            {"color": "#FF0000", "description": "Red trail color"}
        ]
    },
    "tracking_edgecase.json": {
        "boundary_trail_thickness": [
            {"value": "1", "description": "Minimum trail thickness"},
            {"value": "10", "description": "Maximum trail thickness"}
        ],
        "boundary_times": [
            {"from_time": "00:00", "to_time": "23:59", "description": "Full 24-hour midnight-to-midnight boundary range"}
        ]
    },
    "reports_positive.json": {
        "valid_report_generation": [
            {"report_name": "Fleet Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "01/09/2026", "end_date": "01/09/2026", "description": "Generate Fleet Summary with valid single-day range"},
            {"report_name": "Work Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Work Hour with valid filters"},
            {"report_name": "Vehicle Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "08/20/2026", "end_date": "08/28/2026", "description": "Generate Vehicle Summary with valid multi-day range (entered as MM/DD -- see Bug_Report.md #6 -- and kept out of the broken Mar-2026 partition, see Bug_Report.md #17)"},
            {"report_name": "Maxspeed Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Maxspeed Chart with valid filters"},
            {"report_name": "Stoppage Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Stoppage Summary with valid filters"},
            {"report_name": "Running Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "01/09/2026", "end_date": "01/09/2026", "description": "Generate Running Summary with valid filters"},
            {"report_name": "Engine Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Engine Hour with valid filters"},
            {"report_name": "Trip Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "08/20/2026", "end_date": "08/28/2026", "description": "Generate Trip Report with valid filters (entered as MM/DD -- see Bug_Report.md #6 -- and kept out of the broken Mar-2026 partition, see Bug_Report.md #17)"},
            {"report_name": "Distance Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Distance Chart with valid filters"},
            {"report_name": "Cumulative Distance", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "08/20/2026", "end_date": "08/28/2026", "description": "Generate Cumulative Distance with valid filters (entered as MM/DD -- see Bug_Report.md #6 -- and kept out of the broken Mar-2026 partition, see Bug_Report.md #17)"},
            {"report_name": "Idle", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Idle with valid filters"},
            {"report_name": "Driver Report", "vehicle_name": "", "driver_name": REPORT_TEST_DRIVER_NAME, "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Driver Report with valid filters"},
            {"report_name": "Driver Performance", "vehicle_name": "", "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Driver Performance with valid filters"},
            {"report_name": "Alert", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Alert report with valid filters"},
            {"report_name": "ADAS Alarm Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate ADAS Alarm Report with valid filters"},
            {"report_name": "BMS Summary Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate BMS Summary Report with valid filters"},
            {"report_name": "BMS Cell Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate BMS Cell Report with valid filters"},
            {"report_name": "Battery Charging Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Battery Charging Summary with valid filters"},
            {"report_name": "Temperature", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Temperature report with valid filters"},
            {"report_name": "Humidity Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Humidity Report with valid filters"},
            {"report_name": "Sensor Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "03/01/2026", "end_date": "03/10/2026", "description": "Generate Sensor Report with valid filters"}
        ],
        "valid_vehicle_selection": [
            {"vehicle_name": REPORT_TEST_VEHICLE_NAME, "description": "Select valid single vehicle for report"}
        ],
        "valid_date_ranges": [
            {"start_date": "01/09/2026", "end_date": "01/09/2026", "description": "Same day range"},
            {"start_date": "25/08/2026", "end_date": "01/09/2026", "description": "One week range"}
        ],
        "valid_export_formats": [
            {"format": "Excel", "extension": ".xlsx", "description": "Export to Excel format"},
            {"format": "CSV", "extension": ".csv", "description": "Export to CSV format"},
            {"format": "PDF", "extension": ".pdf", "description": "Export to PDF format"}
        ],
        "valid_schedule_configs": [
            {"report_scope": "Standard Report", "report_name": "Fleet Summary", "frequency": "Daily", "schedule_time": "08:00", "email_1": "test@trackofy.com", "schedule_till_day_name": "15", "description": "Schedule Fleet Summary daily"}
        ],
        "valid_custom_report_templates": [
            {"template_name": "Automated Test Template", "template_description": "Template created by automation test suite", "description": "Create valid custom report template"}
        ]
    },
    "reports_negative.json": {
        "invalid_date_ranges": [
            {"start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"start_date": "", "end_date": "01/09/2026", "description": "Empty start date"}
        ],
        "invalid_date_range_per_report": [
            {"report_name": "Fleet Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Work Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Vehicle Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Maxspeed Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Stoppage Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Running Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Engine Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Trip Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Distance Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Cumulative Distance", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Idle", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Driver Report", "vehicle_name": "", "driver_name": REPORT_TEST_DRIVER_NAME, "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Driver Performance", "vehicle_name": "", "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Alert", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "ADAS Alarm Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "BMS Summary Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "BMS Cell Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Battery Charging Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Temperature", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Humidity Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"},
            {"report_name": "Sensor Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "driver_name": "", "start_date": "10/09/2026", "end_date": "01/09/2026", "description": "Start date after end date"}
        ],
        "missing_required_fields": [
            {"report_name": "Fleet Summary", "field_missing": "vehicle", "description": "Generate report without selecting any vehicle"},
            {"report_name": "Vehicle Summary", "field_missing": "vehicle", "description": "Generate report without selecting any vehicle"}
        ],
        "invalid_schedule_configs": [
            {"report_scope": "Standard Report", "report_name": "Fleet Summary", "frequency": "Daily", "schedule_time": "08:00", "email_1": "", "description": "Schedule with empty email address"},
            {"report_scope": "Standard Report", "report_name": "Fleet Summary", "frequency": "Daily", "schedule_time": "08:00", "email_1": "invalid-email-format", "description": "Schedule with invalid email format"}
        ],
        "reports_with_no_vehicle_selected": [
            {"report_name": "Fleet Summary", "description": "Attempt to generate Fleet Summary without vehicle"},
            {"report_name": "Vehicle Summary", "description": "Attempt to generate Vehicle Summary without vehicle"}
        ]
    },
    "reports_functional.json": {
        # standard_reports_with_config removed -- it drifted out of sync with the real
        # 21-report catalog (only 13 entries) and the one test using it never even read
        # its "expected_fields"; that test now parametrizes directly over
        # data.reports.STANDARD_REPORT_NAMES instead of maintaining a second, driftable list.
        "standard_report_categories": [
            {"category": "Fleet Performance", "report_count": 7, "description": "Fleet Performance category"},
            {"category": "Trips & Movement", "report_count": 4, "description": "Trips & Movement category"},
            {"category": "Driver & Safety", "report_count": 4, "description": "Driver & Safety category"},
            {"category": "BMS & Sensors", "report_count": 6, "description": "BMS & Sensors category"}
        ],
        "report_tabs": [
            {"tab_name": "Standard", "expected_path": "/reports/standard", "description": "Standard tab navigation"},
            {"tab_name": "Custom", "expected_path": "/reports/custom", "description": "Custom tab navigation"},
            {"tab_name": "Schedule", "expected_path": "/reports/scheduled", "description": "Schedule tab navigation"}
        ],
        "rows_per_page_options": [
            {"value": "10", "description": "10 rows per page"},
            {"value": "25", "description": "25 rows per page"},
            {"value": "50", "description": "50 rows per page"},
            {"value": "100", "description": "100 rows per page"}
        ],
        "kpi_card_names": [
            {"name": "Total Units", "description": "Total Units KPI card"},
            {"name": "Ignition On", "description": "Ignition On KPI card"},
            {"name": "Moving Units", "description": "Moving Units KPI card"},
            {"name": "Avg Utilization", "description": "Avg Utilization KPI card"},
            {"name": "Stale / Offline Units", "description": "Stale / Offline Units KPI card"},
            {"name": "Active Alerts", "description": "Active Alerts KPI card"}
        ]
    },
    "reports_edgecase.json": {
        "boundary_date_ranges": [
            {"start_date": "01/09/2026", "end_date": "01/09/2026", "description": "Same start and end date boundary"},
            {"start_date": "01/01/2026", "end_date": "01/09/2026", "description": "Very large date range spanning 8 months"}
        ],
        "empty_result_reports": [
            {"report_name": "Fleet Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Work Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Vehicle Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Maxspeed Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Stoppage Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Running Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Engine Hour", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Trip Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Distance Chart", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Cumulative Distance", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Idle", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Driver Report", "vehicle_name": "", "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": REPORT_TEST_DRIVER_NAME, "description": "Generate report for date range with no data"},
            {"report_name": "Driver Performance", "vehicle_name": "", "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Alert", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "ADAS Alarm Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "BMS Summary Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "BMS Cell Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Battery Charging Summary", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Temperature", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Humidity Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"},
            {"report_name": "Sensor Report", "vehicle_name": REPORT_TEST_VEHICLE_NAME, "start_date": "01/01/2020", "end_date": "02/01/2020", "driver_name": "", "description": "Generate report for date range with no data"}
        ],
        "custom_report_boundary_names": [
            {"template_name": "A", "template_description": "Minimum single character template name", "description": "Single character template name"}
        ],
        "large_vehicle_selection": [
            {"select_all": True, "description": "Select all vehicles for maximum data load"}
        ],
        "rapid_filter_changes": [
            {"report_name": "Fleet Summary", "rapid_clicks": 3, "description": "Rapidly toggle report selection multiple times"}
        ],
        "schedule_boundary_times": [
            {"schedule_time": "00:00", "description": "Schedule at midnight boundary"},
            {"schedule_time": "23:59", "description": "Schedule at end-of-day boundary"}
        ],
        "downloads_page_boundary": [
            {"search_query": "nonexistent_report_xyz", "description": "Search for non-existent report in downloads"}
        ]
    }
}


def load_test_data(file_name: str, key: str = None) -> Any:
    """Load JSON test data from test_data directory with self-healing fallback."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / file_name

    data = None
    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = None

    if not data and file_name in DEFAULT_DATASETS:
        data = DEFAULT_DATASETS[file_name]
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    if not data:
        raise FileNotFoundError(f"Test data file '{file_name}' not found or empty.")

    if key:
        if key not in data:
            raise KeyError(f"Key '{key}' not found in test data file '{file_name}'")
        return data[key]

    return data
