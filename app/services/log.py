"""Operasi log aktivitas.

Filter berasal dari JSON request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.log import Log
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_log(db: Session, user_id: int | None, action: str) -> Log:
    """Mencatat satu aktivitas.

    Args:
        db: Session database.
        user_id: Akun pelaku, atau None untuk proses otomatis sistem.
        action: Uraian aktivitas.

    Returns:
        Entri log yang tersimpan.
    """
    new_log = Log(
        user_id=user_id,
        action=action,
        timestamp=datetime.datetime.now()
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_all_logs(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[Log]:
    """Mengambil log aktivitas, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(Log).order_by(Log.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_logs_by_keys(db: Session, filters: dict[str, Any]) -> list[Log]:
    """Mencari log dengan pencocokan sebagian (`ILIKE`) per kolom.

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai, misalnya `{"action": "login"}`.

    Returns:
        Log yang cocok.

    Raises:
        ValueError: Kalau ada kunci yang bukan kolom tabel log.
    """
    query = db.query(Log)

    for key, value in filters.items():
        if not hasattr(Log, key):
            raise ValueError(f"Invalid column '{key}' for Log.")

        column_to_filter = getattr(Log, key)
        query = query.filter(column_to_filter.ilike(f"%{value}%"))

    return query.all()
