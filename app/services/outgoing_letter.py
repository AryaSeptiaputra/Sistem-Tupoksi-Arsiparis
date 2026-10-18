"""Operasi data surat keluar.

Data masukan berasal dari form atau JSON request yang bentuknya bebas, jadi
diberi tipe `dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.outgoing_letter import OutgoingLetter
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_outgoing_letter(db: Session, letter_data: dict[str, Any]) -> OutgoingLetter:
    """Menyimpan surat keluar baru dengan status persetujuan awal `pending`.

    Args:
        db: Session database.
        letter_data: Isian surat; `number`, `letter_date`, `sent_date`,
            `destination`, `subject`, `is_decree`, dan `classification_id` wajib.

    Returns:
        Surat keluar yang tersimpan.
    """
    new_letter = OutgoingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'],
        sent_date=letter_data['sent_date'],
        destination=letter_data['destination'],
        subject=letter_data['subject'],
        is_decree=letter_data['is_decree'],
        attachment_path=letter_data.get('attachment_path'),
        classification_id=letter_data['classification_id'],
        storage_location_id=letter_data.get('storage_location_id'),

        archive_status=letter_data.get('archive_status', 'active'),
        approval_status=letter_data.get('approval_status', 'pending'),

        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return new_letter

def update_outgoing_letter(db: Session, letter_id: int, update_data: dict[str, Any]) -> OutgoingLetter | None:
    """Mengubah surat keluar; kunci yang bukan kolom diabaikan.

    Args:
        db: Session database.
        letter_id: Id surat.
        update_data: Kolom yang diubah.

    Returns:
        Surat setelah diubah, atau None bila tidak ditemukan.
    """
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']:
            continue

        if hasattr(existing_letter, key):
            setattr(existing_letter, key, value)

    existing_letter.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(existing_letter)
    return existing_letter

def delete_outgoing_letter(db: Session, letter_id: int) -> OutgoingLetter | None:
    """Menghapus surat keluar.

    Args:
        db: Session database.
        letter_id: Id surat.

    Returns:
        Surat yang dihapus, atau None bila tidak ditemukan.
    """
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_outgoing_letters(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[OutgoingLetter]:
    """Mengambil surat keluar, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(OutgoingLetter).order_by(OutgoingLetter.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_outgoing_letters_by_keys(db: Session, filters: dict[str, Any]) -> list[OutgoingLetter]:
    """Mencari surat keluar per kolom.

    `archive_status`, `is_decree`, dan kolom `*_id` dicocokkan persis; kolom
    lain dicocokkan sebagian (`ILIKE`).

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai; kunci yang bukan kolom diabaikan.

    Returns:
        Surat keluar yang cocok.
    """
    query = db.query(OutgoingLetter)

    for key, value in filters.items():
        if not hasattr(OutgoingLetter, key):
            continue

        column_to_filter = getattr(OutgoingLetter, key)
        if key == 'archive_status' or key == 'is_decree' or key.endswith('_id'):
            query = query.filter(column_to_filter == value)
        else:
            query = query.filter(column_to_filter.ilike(f"%{value}%"))

    return query.all()
