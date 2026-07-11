from app.models.qr_data import QRData
from app.utils.qr_generator import generate_qr_image
from app.utils.pdf_compiler import compile_pdf
from app.data.database import insert_label


def generate_and_compile(
    department: str,
    asset_code: str,
    asset_number: str,
    serial_number: str,
    description: str,
) -> tuple[str, str, int]:
    """Generate the QR image + PDF label, and record it in the database.

    Returns (pdf_path, img_path, record_id).
    """
    if not department or not asset_code or not asset_number:
        raise ValueError("Department, Asset Code, and Asset Number are required.")

    data = QRData(
        department=department,
        asset_code=asset_code,
        asset_number=asset_number,
        serial_number=serial_number,
        description=description,
    )

    img_path = generate_qr_image(data)
    pdf_path = compile_pdf(img_path, data)

    record_id = insert_label(
        department=department,
        asset_code=asset_code,
        asset_number=asset_number,
        serial_number=serial_number,
        description=description,
        qr_image_path=img_path,
        pdf_path=pdf_path,
    )

    return pdf_path, img_path, record_id