# Asset QR Code Generator
Made by: Adam Daniel P. Azarcon

A desktop application built with **Flet** (Python) to generate QR code labels for assets, store them in a local database, and manage them through a history view. It creates a square label with the QR code and two lines of text (department/asset ID and description), and supports batch export to PDF.

---

## Features

- **Generate QR labels** – Fill in department, asset code, asset number, serial number, and description.
- **Local SQLite database** – Every generated QR code is stored with metadata and file paths.
- **History view** – See all generated QR code with thumbnails, select multiple, delete, or compile to PDF.
- **Batch PDF export** – Select any number of QR code and compile them into a grid on A4 pages (adjustable printed size).
- **Optional file save** – Choose to save a copy of the QR code PNG to any location (or keep it only in the library).
- **Lightweight** – Uses Flet for the GUI, QRCode and Pillow for image generation, and SQLite for persistence.

---

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

---

## Installation

1. Clone the repository or download the source code.
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the application from the project root:

```bash
python app.py
```

### Home View
- Fill in the asset details.
- Toggle **"Save a copy elsewhere"** if you want to save the generated label PNG to a custom location.
- Click **Generate QR Code**.
- The QR code is added to your library (database) and the preview is shown.

### History View (Library)
- Click the **Library** button in the app bar to see all generated QR codes.
- Select one or more QR codes using the checkboxes.
- Use **Compile to PDF** to export selected QR codes into a single PDF (choose the printed size).
- Use **Delete** to permanently remove selected records and their files (confirmation dialog).

---

## Project Structure

```
qr_generator_flet/
├── app.py                  
├── requirements.txt
├── README.md
├──.gitignore
├── assets/
│   ├── temp_qr/            # Temporary QR images
│   └── icons/              # App icons
├── outputs/                # Compiled PDFs
└── app/
   ├── main.py              # Entry point – Flet app with routing
   ├── data/
   │   ├── labels.db
   │   └── database.py      # SQLite operations (init, insert, select, delete)
   ├── models/
   │   ├── qr_data.py       # Data class for QR info, sanitization
   │   └── asset_config.py  # Department list and asset code mapping
   ├── controllers/
   │   └── qr_controller.py # Orchestrates generation, DB insertion, file cleanup
   ├── utils/
   │   ├── qr_generator.py  # Generates QR code image
   │   ├── label_compiler.py # Composes QR + text into a square PNG label
   │   └── batch_pdf_compiler.py # Compiles multiple labels into a PDF grid
   └── views/
      ├── home.py          # Main input form and generation UI
      └── history.py       # List view of all labels with selection actions
```

---

## Dependencies
- Python 3.10+
- All are listed in `requirements.txt`.

---

## License

This project is provided as is-for educational and personal use. Feel free to adapt it to your needs.