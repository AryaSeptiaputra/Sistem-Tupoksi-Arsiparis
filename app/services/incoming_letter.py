"""Operasi data surat masuk.

Data masukan berasal dari form atau JSON request yang bentuknya bebas, jadi
diberi tipe `dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.incoming_letter import IncomingLetter
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_incoming_letter(db: Session, letter_data: dict[str, Any]) -> IncomingLetter:
    """Menyimpan surat masuk baru dengan status arsip awal `active`.

    Args:
        db: Session database.
        letter_data: Isian surat; `number`, `letter_date`, `received_date`,
            `sender`, `subject`, dan `classification_id` wajib.

    Returns:
        Surat masuk yang tersimpan.
    """
    new_letter = IncomingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'],
        received_date=letter_data['received_date'],
        sender=letter_data['sender'],
        subject=letter_data['subject'],
        attachment_path=letter_data.get('attachment_path'),
        classification_id=letter_data['classification_id'],
        storage_location_id=letter_data.get('storage_location_id'),
        archive_status=letter_data.get('archive_status', 'active'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return new_letter

def update_incoming_letter(db: Session, letter_id: int, update_data: dict[str, Any]) -> IncomingLetter | None:
    """Mengubah surat masuk; kunci yang bukan kolom diabaikan.

    Args:
        db: Session database.
        letter_id: Id surat.
        update_data: Kolom yang diubah. `storage_location_id` kosong berarti
            lokasi dilepas.

    Returns:
        Surat setelah diubah, atau None bila tidak ditemukan.
    """
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']:
            continue

        if hasattr(existing_letter, key):
            # Pilihan "kosong" di dropdown lokasi dikirim sebagai string kosong
            if key == 'storage_location_id' and (value == "" or value is None):
                setattr(existing_letter, key, None)
            else:
                setattr(existing_letter, key, value)

    existing_letter.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(existing_letter)
    return existing_letter

def delete_incoming_letter(db: Session, letter_id: int) -> IncomingLetter | None:
    """Menghapus surat masuk.

    Args:
        db: Session database.
        letter_id: Id surat.

    Returns:
        Surat yang dihapus, atau None bila tidak ditemukan.
    """
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_incoming_letters(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[IncomingLetter]:
    """Mengambil surat masuk, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil dengan item sudah berupa dict, atau seluruh baris
        sebagai object model bila tanpa pagination.
    """
    query = db.query(IncomingLetter).order_by(desc(IncomingLetter.id))

    if pagination:
        result = paginate_query(query, pagination)
        items_dict = [letter.to_dict() for letter in result.items]
        result.items = items_dict
        return result
    else:
        return query.all()

def get_incoming_letters_by_keys(db: Session, filters: dict[str, Any],
                                 pagination: PaginationParams | None = None) -> PaginatedResult | list[IncomingLetter]:
    """Mencari surat masuk per kolom, terbaru lebih dulu.

    `id`, `archive_status`, dan kolom `*_id` dicocokkan persis; kolom lain
    dicocokkan sebagian (`ILIKE`).

    Args:
        db: Session database.
        filters: Pasangan kolom dan nilai; kunci yang bukan kolom diabaikan.
        pagination: Parameter halaman; tanpa ini semua hasil dikembalikan.

    Returns:
        Satu halaman hasil dengan item sudah berupa dict, atau seluruh hasil
        sebagai object model bila tanpa pagination.
    """
    query = db.query(IncomingLetter).order_by(desc(IncomingLetter.created_at))

    for key, value in filters.items():
        if not hasattr(IncomingLetter, key):
            continue

        column_to_filter = getattr(IncomingLetter, key)

        if key.endswith('_id') or key == 'archive_status' or key == 'id':
            query = query.filter(column_to_filter == value)
        else:
            query = query.filter(column_to_filter.ilike(f"%{value}%"))

    if pagination:
        result = paginate_query(query, pagination)
        items_dict = [letter.to_dict() for letter in result.items]
        result.items = items_dict
        return result
    else:
        return query.all()

