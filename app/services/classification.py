"""Operasi data klasifikasi arsip.

Data masukan berasal dari JSON request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.classification import Classification
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_classification(db: Session, data: dict[str, Any]) -> Classification:
    """Menyimpan klasifikasi baru.

    Args:
        db: Session database.
        data: Isian klasifikasi; `name` dan `code` wajib, retensi dan
            `final_action` memakai default bila kosong.

    Returns:
        Klasifikasi yang tersimpan.
    """
    new_cls = Classification(
        name=data['name'],
        code=data['code'],
        description=data.get('description'),
        retention_active_period=data.get('retention_active_period', 1),
        retention_inactive_period=data.get('retention_inactive_period', 2),
        final_action=data.get('final_action', 'destroy')
    )

    db.add(new_cls)
    db.commit()
    db.refresh(new_cls)
    return new_cls

def update_classification(db: Session, cls_id: int, data: dict[str, Any]) -> Classification | None:
    """Mengubah klasifikasi; kunci yang bukan kolom diabaikan.

    Args:
        db: Session database.
        cls_id: Id klasifikasi.
        data: Kolom yang diubah.

    Returns:
        Klasifikasi setelah diubah, atau None bila tidak ditemukan.
    """
    cls = db.query(Classification).filter(Classification.id == cls_id).first()
    if not cls:
        return None

    for key, value in data.items():
        if key == 'id': continue
        if hasattr(cls, key):
            setattr(cls, key, value)

    cls.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(cls)
    return cls

def delete_classification(db: Session, cls_id: int) -> Classification | None:
    """Menghapus klasifikasi.

    Args:
        db: Session database.
        cls_id: Id klasifikasi.

    Returns:
        Klasifikasi yang dihapus, atau None bila tidak ditemukan.
    """
    cls = db.query(Classification).filter(Classification.id == cls_id).first()
    if not cls:
        return None

    db.delete(cls)
    db.commit()
    return cls

def get_all_classifications(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[Classification]:
    """Mengambil klasifikasi, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(Classification).order_by(Classification.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_classifications_by_keys(db: Session, filters: dict[str, Any]) -> list[Classification]:
    """Mencari klasifikasi dengan pencocokan sebagian (`ILIKE`) per kolom.

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai; kunci yang bukan kolom diabaikan.

    Returns:
        Klasifikasi yang cocok.
    """
    query = db.query(Classification)
    for key, value in filters.items():
        if hasattr(Classification, key):
            col = getattr(Classification, key)
            query = query.filter(col.ilike(f"%{value}%"))
    return query.all()
