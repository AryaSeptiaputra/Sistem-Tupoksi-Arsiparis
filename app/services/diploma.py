"""Operasi data ijazah.

Data masukan berasal dari form atau JSON request yang bentuknya bebas, jadi
diberi tipe `dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.diploma import Diploma
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_diploma(db: Session, data: dict[str, Any]) -> Diploma:
    """Menyimpan data ijazah baru.

    Args:
        db: Session database.
        data: Isian ijazah; `number`, `student_name`, `major`, dan
            `academic_year` wajib.

    Returns:
        Ijazah yang tersimpan.
    """
    new_diploma = Diploma(
        number=data['number'],
        student_name=data['student_name'],
        major=data['major'],
        academic_year=data['academic_year'],

        is_collected=data.get('is_collected', False),
        collected_at=data.get('collected_at'),

        attachment_path=data.get('attachment_path'),
        storage_location_id=data.get('storage_location_id'),

        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_diploma)
    db.commit()
    db.refresh(new_diploma)
    return new_diploma

def update_diploma(db: Session, diploma_id: int, update_data: dict[str, Any]) -> Diploma | None:
    """Mengubah data ijazah dan menyesuaikan tanggal pengambilan.

    Saat ditandai sudah diambil tanpa tanggal, tanggal diisi waktu sekarang;
    saat ditandai belum diambil, tanggal dikosongkan.

    Args:
        db: Session database.
        diploma_id: Id ijazah.
        update_data: Kolom yang diubah; kunci yang bukan kolom diabaikan.

    Returns:
        Ijazah setelah diubah, atau None bila tidak ditemukan.
    """
    existing = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing:
        return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']:
            continue

        if key == 'is_collected' and value is True:
            if not existing.collected_at and not update_data.get('collected_at'):
                existing.collected_at = datetime.datetime.now()

        if key == 'is_collected' and value is False:
            existing.collected_at = None

        if hasattr(existing, key):
            setattr(existing, key, value)

    existing.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(existing)
    return existing

def delete_diploma(db: Session, diploma_id: int) -> Diploma | None:
    """Menghapus data ijazah.

    Args:
        db: Session database.
        diploma_id: Id ijazah.

    Returns:
        Ijazah yang dihapus, atau None bila tidak ditemukan.
    """
    existing = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing:
        return None

    db.delete(existing)
    db.commit()
    return existing

def get_all_diplomas(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[Diploma]:
    """Mengambil data ijazah, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(Diploma).order_by(Diploma.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_diplomas_by_keys(db: Session, filters: dict[str, Any]) -> list[Diploma]:
    """Mencari ijazah per kolom.

    `storage_location_id` dan nilai boolean dicocokkan persis; kolom lain
    dicocokkan sebagian (`ILIKE`).

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai; kunci yang bukan kolom diabaikan.

    Returns:
        Ijazah yang cocok.
    """
    query = db.query(Diploma)

    for key, value in filters.items():
        if not hasattr(Diploma, key): continue

        col = getattr(Diploma, key)

        if key == 'storage_location_id' or isinstance(value, bool):
            query = query.filter(col == value)
        else:
            query = query.filter(col.ilike(f"%{value}%"))

    return query.all()
