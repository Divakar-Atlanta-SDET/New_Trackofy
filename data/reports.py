STANDARD_REPORTS = [
    {
        "name": "Fleet Summary",
        "fields": ["Select Vehicles *", "Filter By", "Report columns", "Vehicle No", "Distance"],
    },
    {
        "name": "Work Hour",
        "fields": ["Select Vehicles *", "Start Date", "From Time (HH:mm)", "End Date", "To Time (HH:mm)"],
    },
    {
        "name": "Distance Chart",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Minimum Distance (km)", "Maximum Distance (km)"],
    },
    {
        "name": "Cumulative Distance",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Total Distance(KM)"],
    },
    {
        "name": "Idle",
        "fields": ["Select Vehicles *", "Time Interval Hour", "Time Interval Minute", "Ignition Off", "Ignition On"],
    },
    {
        "name": "Vehicle Summary",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Total Distance", "Playback"],
    },
    {
        "name": "Maxspeed Chart",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Units", "Dates"],
    },
    {
        "name": "Stoppage Summary",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Total halt", "Max halt"],
    },
    {
        "name": "Running Summary",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Total running time"],
    },
    {
        "name": "Alert",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Alert Name", "Count"],
    },
    {
        "name": "Driver Report",
        "fields": ["Select Driver", "Start Date", "End Date", "Fuel consume", "Mileage"],
    },
    {
        "name": "Temperature",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Temperature(°C)"],
    },
    {
        "name": "Driver Performance",
        "fields": ["Start Date", "End Date", "Driver", "Rating", "No of trips"],
    },
    {
        "name": "Battery Charging Summary",
        "fields": ["Select Vehicles *", "Start Date", "End Date"],
    },
    {
        "name": "Engine Hour",
        "fields": ["Select Vehicles *", "Start Date", "End Date", "Total time /engine duration"],
    },
    {
        "name": "Trip Report",
        "fields": [
            "Select Trip Type",
            "Select Vehicles *",
            "Start Date",
            "End Date",
            "Enable Config",
            "No of trip",
        ],
    },
    {
        "name": "Sensor Report",
        "fields": ["Select Sensor", "Select Vehicles *", "Start Date", "End Date"],
    },
    {
        "name": "BMS Summary Report",
        "fields": ["Select Vehicle", "Start Date", "End Date", "Select Parameter"],
    },
    {
        "name": "BMS Cell Report",
        "fields": ["Select Vehicle", "Start Date", "End Date", "Select Report Type"],
    },
    {
        "name": "ADAS Alarm Report",
        "fields": ["Select Alert Type", "Select Vehicle", "Start Date", "End Date"],
    },
]

STANDARD_REPORT_NAMES = [report["name"] for report in STANDARD_REPORTS]

CUSTOM_REPORT_FIELDS = [
    "Create Custom Report",
    "General",
    "Components",
    "General Information",
    "Name",
    "Description:",
    "Next Step",
]

SCHEDULE_REPORT_FIELDS = [
    "Schedule Report",
    "Select Vehicles",
    "Select Report Type",
    "Select Frequency",
    "Schedule Till",
    "Schedule Time",
    "Email 1",
    "Export Type",
    "Excel",
    "CSV",
]
