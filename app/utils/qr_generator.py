import os
from pathlib import Path
from datetime import datetime
import qrcode
from qrcode import ERROR_CORRECT_L
from app.models.qr_data import QRData

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # app/utils -> app -> project root
TEMP_DIR = PROJECT_ROOT / "assets" / "temp_qr"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


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
    safe_asset_id = data.asset_id
    filename = f"{safe_asset_id}_{timestamp}.png"
    file_path = os.path.join(TEMP_DIR, filename)
    img.save(file_path)

    return file_path