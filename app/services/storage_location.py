"""Operasi data lokasi simpan arsip.

Data masukan berasal dari JSON request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.storage_location import StorageLocation
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_storage_location(db: Session, data: dict[str, Any]) -> StorageLocation:
    """Menyimpan lokasi simpan baru, misalnya lemari atau rak.

    Args:
        db: Session database.
        data: Isian lokasi; `name` wajib.

    Returns:
        Lokasi yang tersimpan.
    """
    new_location = StorageLocation(
        name=data['name'],
        description=data.get('description'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

def update_storage_location(db: Session, location_id: int, update_data: dict[str, Any]) -> StorageLocation | None:
    """Mengubah nama atau keterangan lokasi simpan.

    Args:
        db: Session database.
        location_id: Id lokasi.
        update_data: Nilai `name` dan/atau `description` baru.

    Returns:
        Lokasi setelah diubah, atau None bila tidak ditemukan.
    """
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        return None

    if 'name' in update_data:
        location.name = update_data['name']
    if 'description' in update_data:
        location.description = update_data['description']

    location.updated_at = datetime.datetime.now()

    db.commit()
    db.refresh(location)
    return location

def delete_storage_location(db: Session, location_id: int) -> StorageLocation | None:
    """Menghapus lokasi simpan.

    Args:
        db: Session database.
        location_id: Id lokasi.

    Returns:
        Lokasi yang dihapus, atau None bila tidak ditemukan.
    """
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        return None

    db.delete(location)
    db.commit()
    return location

def get_all_storage_locations(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[StorageLocation]:
    """Mengambil lokasi simpan, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(StorageLocation).order_by(StorageLocation.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()
