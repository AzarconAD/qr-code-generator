import os
import time
import qrcode
from qrcode import ERROR_CORRECT_L
from app.models.qr_data import QRData

TEMP_DIR = "assets/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_qr_image(data: QRData) -> str:
    """Generates a QR code image with a unique filename and returns its path."""

    # Clean up old temporary PNG files
    for f in os.listdir(TEMP_DIR):
        if f.endswith(".png"):
            try:
                os.remove(os.path.join(TEMP_DIR, f))
            except OSError:
                pass  # ignore if file is locked or already gone

    # Generate a unique filename using a timestamp
    timestamp = int(time.time() * 1000)  # milliseconds to reduce collision chance
    filename = f"qr_{timestamp}.png"
    file_path = os.path.join(TEMP_DIR, filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=data.box_size,
        border=4,
    )
    qr.add_data(data.to_qr_string())
    qr.make(fit=True)

    img = qr.make_image(fill_color=data.fill_color, back_color=data.bg_color)
    img.save(file_path)

    return file_path   # e.g., "assets/temp/qr_1712345678901.png"