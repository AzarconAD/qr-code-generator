import os
from pathlib import Path
from datetime import datetime
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DPI = 150
PAGE_WIDTH_IN, PAGE_HEIGHT_IN = 8.27, 11.69   # A4
PAGE_MARGIN_IN = 0.4
GAP_IN = 0.2

PAGE_WIDTH_PX = int(PAGE_WIDTH_IN * DPI)
PAGE_HEIGHT_PX = int(PAGE_HEIGHT_IN * DPI)
MARGIN_PX = int(PAGE_MARGIN_IN * DPI)
GAP_PX = int(GAP_IN * DPI)

MIN_LABEL_SIZE_IN = 1
MAX_LABEL_SIZE_IN = 5


def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _render_page(label_paths: list[str], label_px: int, columns: int) -> Image.Image:
    page = Image.new("RGB", (PAGE_WIDTH_PX, PAGE_HEIGHT_PX), "white")
    page.info["dpi"] = (DPI, DPI)

    for index, path in enumerate(label_paths):
        col = index % columns
        row = index // columns
        x = MARGIN_PX + col * (label_px + GAP_PX)
        y = MARGIN_PX + row * (label_px + GAP_PX)

        with Image.open(path) as label_img:
            label_img = label_img.convert("RGB").resize((label_px, label_px))
            page.paste(label_img, (x, y))

    return page


def compile_labels_to_pdf(label_paths: list[str], label_size_in: float = 2.0) -> str:
    """Paginate selected label PNGs into a grid across standard A4 page(s).

    label_size_in: printed size of each square label, in inches (clamped 1-5).
    """
    if not label_paths:
        raise ValueError("No labels selected to compile.")

    label_size_in = max(MIN_LABEL_SIZE_IN, min(MAX_LABEL_SIZE_IN, label_size_in))
    label_px = int(label_size_in * DPI)

    columns = max(1, (PAGE_WIDTH_PX - 2 * MARGIN_PX + GAP_PX) // (label_px + GAP_PX))
    rows = max(1, (PAGE_HEIGHT_PX - 2 * MARGIN_PX + GAP_PX) // (label_px + GAP_PX))
    labels_per_page = columns * rows

    page_chunks = _chunk(label_paths, labels_per_page)
    pages = [_render_page(chunk, label_px, columns) for chunk in page_chunks]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = str(OUTPUT_DIR / f"compiled_labels_{timestamp}.pdf")

    first_page, remaining_pages = pages[0], pages[1:]
    first_page.save(
        pdf_path, "PDF", dpi=(DPI, DPI),
        save_all=True, append_images=remaining_pages,
    )

    return pdf_path