import os
from pathlib import Path
from datetime import datetime
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Standard A4 page setup at 150 DPI --- #
DPI = 150
PAGE_WIDTH_IN, PAGE_HEIGHT_IN = 8.27, 11.69   # A4
PAGE_MARGIN_IN = 0.4
LABEL_SIZE_IN = 2.0                            
GAP_IN = 0.2

PAGE_WIDTH_PX = int(PAGE_WIDTH_IN * DPI)
PAGE_HEIGHT_PX = int(PAGE_HEIGHT_IN * DPI)
MARGIN_PX = int(PAGE_MARGIN_IN * DPI)
LABEL_PX = int(LABEL_SIZE_IN * DPI)
GAP_PX = int(GAP_IN * DPI)

COLUMNS = max(1, (PAGE_WIDTH_PX - 2 * MARGIN_PX + GAP_PX) // (LABEL_PX + GAP_PX))
ROWS = max(1, (PAGE_HEIGHT_PX - 2 * MARGIN_PX + GAP_PX) // (LABEL_PX + GAP_PX))
LABELS_PER_PAGE = COLUMNS * ROWS


def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _render_page(label_paths: list[str]) -> Image.Image:
    page = Image.new("RGB", (PAGE_WIDTH_PX, PAGE_HEIGHT_PX), "white")

    for index, path in enumerate(label_paths):
        col = index % COLUMNS
        row = index // COLUMNS
        x = MARGIN_PX + col * (LABEL_PX + GAP_PX)
        y = MARGIN_PX + row * (LABEL_PX + GAP_PX)

        with Image.open(path) as label_img:
            label_img = label_img.convert("RGB").resize((LABEL_PX, LABEL_PX))
            page.paste(label_img, (x, y))

    return page


def compile_labels_to_pdf(label_paths: list[str]) -> str:
    """Paginate selected label PNGs into a grid across standard A4 page(s), saved as one PDF."""
    if not label_paths:
        raise ValueError("No labels selected to compile.")

    page_chunks = _chunk(label_paths, LABELS_PER_PAGE)
    pages = [_render_page(chunk) for chunk in page_chunks]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = str(OUTPUT_DIR / f"compiled_labels_{timestamp}.pdf")

    first_page, remaining_pages = pages[0], pages[1:]
    first_page.save(
        pdf_path, "PDF", resolution=DPI,
        save_all=True, append_images=remaining_pages,
    )

    return pdf_path