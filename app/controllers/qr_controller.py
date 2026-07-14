import os
from app.models.qr_data import QRData
from app.utils.qr_generator import generate_qr_image
from app.utils.label_compiler import compile_label_png
from app.data.database import insert_label
from app.data.database import delete_label as _delete_label_record


def generate_and_compile(
    department: str,
    reference_no: str,
    asset_code: str,
    asset_number: str,
    serial_number: str,
    description: str,
) -> tuple:
    """
    Generate a QR label, save it to the database, and return paths + record ID.

    All empty strings for optional fields are defaulted to 'N/A' or 'No description provided'.
    """
    reference_no = reference_no.strip() if reference_no else "N/A"
    serial_number = serial_number.strip() if serial_number else "N/A"
    description = description.strip() if description else "No description provided"

    if not department or not reference_no or not asset_code or not asset_number:
        raise ValueError("Department, Reference Number, Asset Code, and Asset Number are required.")

    data = QRData(
        department=department,
        reference_no=reference_no,
        asset_code=asset_code,
        asset_number=asset_number,
        serial_number=serial_number,
        description=description,
    )

    img_path = generate_qr_image(data)
    label_path = compile_label_png(img_path, data)

    try:
        record_id = insert_label(
            department=department,
            reference_no=reference_no,
            asset_code=asset_code,
            asset_number=asset_number,
            serial_number=serial_number,
            description=description,
            qr_image_path=img_path,
            label_path=label_path,
        )
    except Exception:
        for path in (img_path, label_path):
            if os.path.exists(path):
                os.remove(path)
        raise

    return label_path, img_path, record_id

def delete_qr_code(label_id: int) -> bool:
    """Delete a QR code's DB record and its associated files. Returns True if a record was found."""
    record = _delete_label_record(label_id)
    if record is None:
        return False

    for path in (record.get("qr_image_path"), record.get("label_path")):
        if path and os.path.exists(path):
            os.remove(path)

    return True