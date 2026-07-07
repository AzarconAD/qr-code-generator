from dataclasses import dataclass

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