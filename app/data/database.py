import sqlite3
import os
from datetime import datetime

DB_DIR = "app/data"
DB_PATH = os.path.join(DB_DIR, "labels.db")
os.makedirs(DB_DIR, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the labels table if it doesn't exist yet. Call once at app startup."""
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                asset_code TEXT NOT NULL,
                asset_number TEXT NOT NULL,
                serial_number TEXT,
                description TEXT,
                qr_image_path TEXT,
                pdf_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def insert_label(
    department: str,
    asset_code: str,
    asset_number: str,
    serial_number: str,
    description: str,
    qr_image_path: str,
    pdf_path: str,
) -> int:
    """Insert a new label record and return its id."""
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO labels
                (department, asset_code, asset_number, serial_number,
                 description, qr_image_path, pdf_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                department,
                asset_code,
                asset_number,
                serial_number,
                description,
                qr_image_path,
                pdf_path,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        return cursor.lastrowid


def get_all_labels() -> list[dict]:
    """Return all label records, most recently generated first."""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM labels ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]


def get_label(label_id: int) -> dict | None:
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM labels WHERE id = ?", (label_id,)).fetchone()
        return dict(row) if row else None