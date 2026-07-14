import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.models.qr_data import QRData

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANVAS_SIZE = 400
QR_SIZE = 300 
TOP_MARGIN = 20
LINE_HEIGHT = 32
TEXT_SIDE_MARGIN = 16
BG_COLOR = "white"
TEXT_COLOR = "black"

_RESAMPLE_NEAREST = getattr(Image, "Resampling", Image).NEAREST

_FONT_CANDIDATES = [
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _fit_line(draw: ImageDraw.ImageDraw, text: str, max_width: int,
              start_size: int = 20, min_size: int = 12):
    """Shrink font until text fits max_width; truncate with '...' if still too wide at min_size."""
    size = start_size
    while size >= min_size:
        font = _load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return text, font
        size -= 1

    font = _load_font(min_size)
    truncated = text
    while truncated and draw.textlength(truncated + "...", font=font) > max_width:
        truncated = truncated[:-1]
    return (truncated + "...") if truncated != text else text, font


def compile_label_png(qr_image_path: str, data: QRData) -> str:
    """Compose a compact square PNG: QR on top, 2 lines of text below.

    Line 1: department-asset_id
    Line 2: description
    """
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    with Image.open(qr_image_path) as qr_img:
        qr_img = qr_img.convert("RGB").resize((QR_SIZE, QR_SIZE), resample=_RESAMPLE_NEAREST)
        qr_x = (CANVAS_SIZE - QR_SIZE) // 2
        canvas.paste(qr_img, (qr_x, TOP_MARGIN))

    max_text_width = CANVAS_SIZE - (2 * TEXT_SIDE_MARGIN)
    line1_text = f"{data.department}-{data.asset_id}"
    line2_text = f"{data.reference_no}-{data.description}"

    line1, font1 = _fit_line(draw, line1_text, max_text_width, start_size=22, min_size=14)
    line2, font2 = _fit_line(draw, line2_text, max_text_width, start_size=18, min_size=12)

    line1_y = TOP_MARGIN + QR_SIZE + 12
    line2_y = line1_y + LINE_HEIGHT

    for text, font, y in ((line1, font1, line1_y), (line2, font2, line2_y)):
        text_width = draw.textlength(text, font=font)
        x = (CANVAS_SIZE - text_width) // 2
        draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(OUTPUT_DIR / f"asset_label_{timestamp}.png")
    canvas.save(output_path, format="PNG")

    return output_path