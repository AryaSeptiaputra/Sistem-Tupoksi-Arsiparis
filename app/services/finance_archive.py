"""Operasi data arsip keuangan.

Data masukan berasal dari form request yang bentuknya bebas, jadi diberi tipe
`dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.orm import Session
from app.models.finance_archive import FinanceArchive
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

def create_finance_archive(db: Session, data: dict[str, Any]) -> FinanceArchive:
    """Menyimpan arsip keuangan baru.

    Args:
        db: Session database.
        data: Isian arsip; `title`, `fiscal_year`, dan `classification_id`
            wajib. Nilai angka berbentuk teks diubah ke integer.

    Returns:
        Arsip yang tersimpan.
    """
    new_archive = FinanceArchive(
        title=data['title'],
        fiscal_year=int(data['fiscal_year']),
        period_month=int(data['period_month']) if data.get('period_month') else None,

        category=data.get('category', 'bos_reguler'),
        amount=int(data['amount']) if data.get('amount') else 0,
        description=data.get('description'),
        attachment_path=data.get('attachment_path'),

        classification_id=int(data['classification_id']),
        storage_location_id=int(data['storage_location_id']) if data.get('storage_location_id') else None,

        archive_status=data.get('archive_status', 'active'),

        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_archive)
    db.commit()
    db.refresh(new_archive)
    return new_archive

def update_finance_archive(db: Session, archive_id: int, update_data: dict[str, Any]) -> FinanceArchive | None:
    """Mengubah arsip keuangan; kolom angka diubah ke integer.

    Args:
        db: Session database.
        archive_id: Id arsip.
        update_data: Kolom yang diubah; kunci yang bukan kolom diabaikan.

    Returns:
        Arsip setelah diubah, atau None bila tidak ditemukan.
    """
    archive = db.query(FinanceArchive).filter(FinanceArchive.id == archive_id).first()
    if not archive: return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: continue

        if hasattr(archive, key):
            if key == 'amount' or key == 'fiscal_year':
                setattr(archive, key, int(value) if value else 0)
            elif key == 'period_month':
                setattr(archive, key, int(value) if value else None)
            elif key == 'storage_location_id':
                setattr(archive, key, int(value) if value else None)
            else:
                setattr(archive, key, value)

    archive.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(archive)
    return archive

def delete_finance_archive(db: Session, archive_id: int) -> FinanceArchive | None:
    """Menghapus arsip keuangan.

    Args:
        db: Session database.
        archive_id: Id arsip.

    Returns:
        Arsip yang dihapus, atau None bila tidak ditemukan.
    """
    archive = db.query(FinanceArchive).filter(FinanceArchive.id == archive_id).first()
    if not archive: return None
    db.delete(archive)
    db.commit()
    return archive

def get_all_finance_archives(db: Session, pagination: PaginationParams | None = None) -> PaginatedResult | list[FinanceArchive]:
    """Mengambil arsip keuangan, urut tahun anggaran lalu waktu dibuat (terbaru dulu).

    Args:
        db: Session database.
        pagination: Parameter halaman; tanpa ini semua baris dikembalikan.

    Returns:
        Satu halaman hasil, atau seluruh baris bila tanpa pagination.
    """
    query = db.query(FinanceArchive).order_by(FinanceArchive.fiscal_year.desc(), FinanceArchive.created_at.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()
