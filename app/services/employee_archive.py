"""Operasi data arsip pegawai.

Data masukan berasal dari form request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.employee_archive import EmployeeArchive
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_employee_archive(db: Session, data: dict[str, Any]) -> EmployeeArchive:
    """Menyimpan arsip pegawai baru.

    Args:
        db: Session database.
        data: Isian arsip; `document_name` dan `owner_id` wajib. Nilai id dan
            tahun berbentuk teks diubah ke integer.

    Returns:
        Arsip yang tersimpan.
    """
    new_archive = EmployeeArchive(
        document_name=data['document_name'],
        document_type=data.get('document_type', 'lainnya'),
        archive_status=data.get('archive_status', 'active'),
        document_year=int(data['document_year']) if data.get('document_year') else None,
        description=data.get('description'),
        attachment_path=data.get('attachment_path'),
        owner_id=int(data['owner_id']),
        classification_id=int(data['classification_id']) if data.get('classification_id') else None,
        storage_location_id=int(data['storage_location_id']) if data.get('storage_location_id') else None
    )

    db.add(new_archive)
    db.commit()
    db.refresh(new_archive)
    return new_archive

def update_employee_archive(db: Session, archive_id: int, update_data: dict[str, Any]) -> EmployeeArchive | None:
    """Mengubah arsip pegawai; kolom id dan tahun diubah ke integer.

    Args:
        db: Session database.
        archive_id: Id arsip.
        update_data: Kolom yang diubah; kunci yang bukan kolom diabaikan.

    Returns:
        Arsip setelah diubah, atau None bila tidak ditemukan.
    """
    archive = db.query(EmployeeArchive).filter(EmployeeArchive.id == archive_id).first()
    if not archive: return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: continue

        if hasattr(archive, key):
            if key in ['owner_id', 'storage_location_id', 'document_year', 'classification_id']:
                setattr(archive, key, int(value) if value else None)
            else:
                setattr(archive, key, value)

    archive.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(archive)
    return archive

def delete_employee_archive(db: Session, archive_id: int) -> EmployeeArchive | None:
    """Menghapus arsip pegawai.

    Args:
        db: Session database.
        archive_id: Id arsip.

    Returns:
        Arsip yang dihapus, atau None bila tidak ditemukan.
    """
    archive = db.query(EmployeeArchive).filter(EmployeeArchive.id == archive_id).first()
    if not archive: return None
    db.delete(archive)
    db.commit()
    return archive

def get_all_employee_archives(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[EmployeeArchive]:
    """Mengambil arsip pegawai, terbaru lebih dulu.

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(EmployeeArchive).order_by(EmployeeArchive.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()
