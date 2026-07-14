# Department options
DEPARTMENTS = [
    "ADMITTING",
    "ADMINISTRATION",
    "ACCOUNTING",
    "BILLING",
    "CASHIER",
    "CAFETERIA",
    "CHIEF NURSE",
    "DIETARY",
    "EMERGENCY ROOM",
    "HUMAN RESOURCES",
    "HOUSEKEEPING",
    "HMO",
    "IT",
    "LABORATORY",
    "MAINTENANCE",
    "MEDICAL RECORDS",
    "NSD2",
    "NSD3",
    "OPD",
    "PHARMACY",
    "PHILHEALTH",
    "RADIOLOGY",
    "SECURITY",
    "WAREHOUSE",
]

# Asset Code mappings
ASSET_CODE_MAPPING = {
    "ASST": "Asset",
    "SUPP": "Supply",
    "EQP": "Equipment",
}

# Get just the codes for dropdown
ASSET_CODE = list(ASSET_CODE_MAPPING.keys())