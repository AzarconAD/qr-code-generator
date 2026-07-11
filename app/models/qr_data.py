# qr_data.py
import re
from dataclasses import dataclass, field

_UNSAFE_CHARS = re.compile(r'[\\/:*?"<>|]')

def _clean(value: str) -> str:
    return _UNSAFE_CHARS.sub("-", value.strip()) if value else value

@dataclass
class QRData:
    department: str
    asset_code: str
    asset_number: str
    serial_number: str
    description: str
    fill_color: str = "black"
    bg_color: str = "white"
    box_size: int = 10

    def __post_init__(self):
        self.department = _clean(self.department)
        self.asset_code = _clean(self.asset_code)
        self.asset_number = _clean(self.asset_number)
        self.serial_number = _clean(self.serial_number) if self.serial_number else self.serial_number
        self.description = self.description.strip() if self.description else self.description

    @property
    def asset_id(self) -> str:
        return f"{self.asset_code}-{self.asset_number}"

    def to_qr_string(self) -> str:
        return (
            f"Department: {self.department}\n"
            f"Asset ID: {self.asset_id}\n"
            f"Serial No: {self.serial_number}\n"
            f"Description: {self.description}"
        )