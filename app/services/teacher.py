"""Operasi data guru dan tenaga kependidikan.

Data masukan berasal dari JSON request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_teacher(db: Session, data: dict[str, Any]) -> Teacher:
    """Menyimpan data guru atau pegawai baru.

    Args:
        db: Session database.
        data: Isian data; `identity_number`, `full_name`, `gender`,
            `employment_status`, dan `status` wajib.

    Returns:
        Data guru yang tersimpan.
    """
    new_teacher = Teacher(
        identity_number=data['identity_number'],
        full_name=data['full_name'],
        gender=data['gender'],
        employment_status=data['employment_status'],
        rank=data.get('rank'),
        status=data['status'],
        address=data.get('address'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher

def update_teacher(db: Session, teacher_id: int, update_data: dict[str, Any]) -> Teacher | None:
    """Mengubah data guru; kunci yang bukan kolom diabaikan.

    Args:
        db: Session database.
        teacher_id: Id guru.
        update_data: Kolom yang diubah.

    Returns:
        Data guru setelah diubah, atau None bila tidak ditemukan.
    """
    existing_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()

    if not existing_teacher:
        return None

    for key, value in update_data.items():
        if key == 'id':
            continue

        if hasattr(existing_teacher, key):
            setattr(existing_teacher, key, value)

    existing_teacher.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(existing_teacher)
    return existing_teacher

def delete_teacher(db: Session, teacher_id: int) -> Teacher | None:
    """Menghapus data guru beserta arsip pegawai miliknya (cascade).

    Args:
        db: Session database.
        teacher_id: Id guru.

    Returns:
        Data guru yang dihapus, atau None bila tidak ditemukan.
    """
    existing_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()

    if not existing_teacher:
        return None

    db.delete(existing_teacher)
    db.commit()
    return existing_teacher

def get_all_teachers(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[Teacher]:
    """Mengambil data guru, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(Teacher).order_by(Teacher.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_teachers_by_keys(db: Session, filters: dict[str, Any]) -> list[Teacher]:
    """Mencari guru dengan pencocokan sebagian (`ILIKE`) per kolom.

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai; kunci yang bukan kolom diabaikan.

    Returns:
        Data guru yang cocok.
    """
    query = db.query(Teacher)

    for key, value in filters.items():
        if hasattr(Teacher, key):
            column_to_filter = getattr(Teacher, key)
            query = query.filter(column_to_filter.ilike(f"%{value}%"))

    return query.all()
