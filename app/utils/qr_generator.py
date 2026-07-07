import os
import qrcode
from qrcode import ERROR_CORRECT_L
from app.models.qr_data import QRData

TEMP_DIR = "assets/temp_qr"
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_qr_image(data: QRData) -> str:
    """Generates a QR code image and saves it to the temp folder."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=data.box_size,
        border=4,
    )
    # Use the structured string
    qr.add_data(data.to_qr_string())
    qr.make(fit=True)

    img = qr.make_image(fill_color=data.fill_color, back_color=data.bg_color)
    
    file_path = os.path.join(TEMP_DIR, "temp_qr_code.png")
    img.save(file_path)
    
    return file_path