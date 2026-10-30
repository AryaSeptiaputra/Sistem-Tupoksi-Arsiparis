"""Pengubah tanggal dari isian form menjadi `datetime` untuk kolom DateTime."""

from __future__ import annotations

from datetime import datetime
from typing import Any

# Format nilai input type="date" di browser, contoh: "2026-10-20"
FORM_DATE_FORMAT = "%Y-%m-%d"


def parse_date(value: str | datetime | None, label: str) -> datetime | None:
    """Mengubah tanggal dari form menjadi `datetime`.

    SQLite lewat SQLAlchemy hanya menerima objek `datetime` untuk kolom
    DateTime, sedangkan form mengirim teks.

    Args:
        value: Teks `YYYY-MM-DD`, objek `datetime`, atau kosong.
        label: Nama isian untuk pesan error, misalnya "Tanggal Surat".

    Returns:
        Tanggal sebagai `datetime`, atau None bila kosong.

    Raises:
        ValueError: Kalau teks tidak berformat YYYY-MM-DD.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(value, FORM_DATE_FORMAT)
    except ValueError as e:
        raise ValueError(f"{label} harus berformat YYYY-MM-DD") from e


def parse_dates(data: dict[str, Any], labels: dict[str, str]) -> dict[str, datetime | None]:
    """Mengubah kolom tanggal yang ada di `data` menjadi `datetime`.

    Args:
        data: Isian form atau JSON.
        labels: Nama kolom tanggal dan labelnya untuk pesan error.

    Returns:
        Kolom tanggal yang ada di `data` beserta nilai `datetime`-nya; kolom
        yang tidak dikirim tidak ikut.

    Raises:
        ValueError: Kalau salah satu tanggal tidak berformat YYYY-MM-DD.
    """
    return {field: parse_date(data[field], label) for field, label in labels.items() if field in data}
