# Department options
DEPARTMENTS = [
    "Admitting",
    "Administration",
    "Accounting",
    "Billing",
    "Cashier",
    "Cafeteria",
    "Chief Nurse",
    "Dietary",
    "Emergency Room",
    "Human Resources",
    "Housekeeping",
    "HMO",
    "IT",
    "Laboratory",
    "Maintenance",
    "Medical Records",
    "NSD2",
    "NSD3",
    "OPD",
    "Pharmacy",
    "Philhealth",
    "Radiology",
    "Security",
    "Warehouse",
]

# Asset Code mappings
ASSET_CODE_MAPPING = {
    "ASST": "Asset",
    "SUPP": "Supply",
    "EQP": "Equipment",
}

# Get just the codes for dropdown
ASSET_CODE = list(ASSET_CODE_MAPPING.keys())