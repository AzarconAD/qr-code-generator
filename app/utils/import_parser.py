import os
import pandas as pd

REQUIRED_FIELDS = ["department", "reference_no", "asset_code", "asset_number", "serial_number", "description"]
DEFAULT_ASSET_CODE = "ASST"

HEADER_ALIASES = {
    # Department
    "department": "department",
    "dept": "department",
    # Reference No
    "reference no": "reference_no",
    "reference no.": "reference_no",
    "reference number": "reference_no",
    "ref no": "reference_no",
    "ref. no": "reference_no",
    "ref. no.": "reference_no",
    "ref number": "reference_no",
    "ref. number": "reference_no",
    "ref.": "reference_no",
    "ref": "reference_no",
    # Asset Code
    "asset code": "asset_code_original",
    "asset type": "asset_code",
    "assetcode": "asset_code_original",
    # Asset Number
    "asset number": "asset_number",
    "asset no": "asset_number",
    "asset no.": "asset_number",
    "asset id": "asset_number",
    # Serial Number
    "serial number": "serial_number",
    "serial no": "serial_number",
    "serial no.": "serial_number",
    "serial": "serial_number",
    # Description
    "description": "description",
    "desc": "description",
    "item description": "description",
}

HEADER_KEYWORDS = list(HEADER_ALIASES.keys())


def _normalize_header(header) -> str:
    if not header:
        return ""
    return str(header).strip().lower()


def _find_header_row(lines: list[str]) -> int:
    """Find the line that contains typical header keywords."""
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        lower = line.lower()
        score = sum(1 for kw in HEADER_KEYWORDS if kw in lower)
        if score >= 2:
            return i
    # Fallback: first non-empty line
    for i, line in enumerate(lines):
        if line.strip():
            return i
    return 0


def parse_import_file(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()

    # Read raw lines to find header
    with open(file_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    header_row_index = _find_header_row(lines)

    if ext == ".csv":
        df = pd.read_csv(
            file_path,
            skiprows=header_row_index,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )
    elif ext in (".xlsx", ".xls"):
        # For Excel, find best row by keyword count
        df_raw = pd.read_excel(file_path, dtype=str, header=None)
        best_score = 0
        best_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(row.astype(str)).lower()
            score = sum(1 for kw in HEADER_KEYWORDS if kw in row_str)
            if score > best_score:
                best_score = score
                best_row = i
        df = pd.read_excel(file_path, header=best_row, dtype=str)
        df = df.fillna("")
    else:
        raise ValueError(f"Unsupported file type '{ext}'. Please upload a .csv or .xlsx file.")

    # Rename columns using alias mapping
    column_map = {}
    asset_code_col = None
    for col in df.columns:
        normalized = _normalize_header(col)
        canonical = HEADER_ALIASES.get(normalized)
        if canonical:
            column_map[col] = canonical
            if canonical == "asset_code_original":
                asset_code_col = col

    if asset_code_col and "asset_number" not in column_map.values():
        # Map that column to asset_number instead
        column_map[asset_code_col] = "asset_number"

    # If there is still no asset_number column, we cannot proceed.
    if "asset_number" not in column_map.values():
        raise ValueError("No 'Asset Number' or 'Asset Code' column found. Please ensure your file has a column for asset number.")

    df = df.rename(columns=column_map)

    rows = []
    for i, row in df.iterrows():
        record = {
            field: str(row[field]).strip() if field in df.columns else ""
            for field in REQUIRED_FIELDS
        }

        # Skip completely blank rows
        if not any(record.values()):
            continue

        # If asset_code is missing, set default
        if not record["asset_code"]:
            record["asset_code"] = DEFAULT_ASSET_CODE

        # If asset_number is still missing, skip this row
        if not record["asset_number"]:
            continue

        record["row_number"] = i + 2  # approximate original row
        record["missing_fields"] = [
            f for f in ("department", "asset_code", "asset_number") if not record[f]
        ]
        rows.append(record)

    return rows