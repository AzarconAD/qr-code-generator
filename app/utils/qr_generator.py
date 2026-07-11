import os
from datetime import datetime
import qrcode
from qrcode import ERROR_CORRECT_L
from app.models.qr_data import QRData

TEMP_DIR = "assets/temp_qr"
os.makedirs(TEMP_DIR, exist_ok=True)


def generate_qr_image(data: QRData) -> str:
    """Generates a QR code image and saves it with a unique filename.

    Each call gets its own file (based on asset id + timestamp) so that
    older generated images aren't overwritten -- this matters now that
    every generated label is kept in the history/database view.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=data.box_size,
        border=4,
    )
    qr.add_data(data.to_qr_string())
    qr.make(fit=True)

    img = qr.make_image(fill_color=data.fill_color, back_color=data.bg_color)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_asset_id = data.asset_id.replace("/", "-").replace("\\", "-")
    filename = f"{safe_asset_id}_{timestamp}.png"
    file_path = os.path.join(TEMP_DIR, filename)
    img.save(file_path)

    return file_path