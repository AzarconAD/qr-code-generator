import os
from datetime import datetime
from fpdf import FPDF
from app.models.qr_data import QRData

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compile_pdf(qr_image_path: str, data: QRData) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"asset_label_{timestamp}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 15, txt="ASSET LABEL", ln=True, align="C")
    pdf.ln(5)

    pdf.image(qr_image_path, x=55, y=30, w=100)
    pdf.ln(75)

    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, txt="ASSET DETAILS", ln=True, align="C", fill=True)
    
    pdf.set_font("Arial", size=11)
    pdf.ln(4)
    
    details = [
        ("Department", data.department),
        ("Asset ID", data.asset_id),
        ("Serial Number", data.serial_number),
        ("Description", data.description),
    ]
    
    for label, value in details:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(50, 10, txt=f"{label}:", border=0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(140, 10, txt=value, border=0, ln=True)

    pdf.set_y(270)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 5, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")

    pdf.output(pdf_path)
    return pdf_path