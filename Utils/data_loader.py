import json
from pathlib import Path
from typing import Any

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
