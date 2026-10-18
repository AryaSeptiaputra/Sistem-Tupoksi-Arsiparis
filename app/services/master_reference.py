"""Operasi opsi referensi (isi dropdown).

Data masukan dan keluaran berbentuk dict JSON yang bentuknya bebas, jadi
diberi tipe `dict[str, Any]`.
"""

from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.master_reference import MasterReference, ReferenceCategory
from app.core.database import SessionLocal

class MasterReferenceService:
    """Mengelola opsi referensi; setiap method membuka session sendiri."""

    def get_by_category(self, category: str, only_active: bool = True) -> list[dict[str, Any]]:
        """Mengambil opsi satu kategori, urut `sort_order` lalu nama.

        Args:
            category: Nilai kategori, misalnya `school_major`.
            only_active: Hanya opsi yang aktif bila True.

        Returns:
            Opsi dalam bentuk dict.
        """
        db: Session = SessionLocal()
        try:
            query = db.query(MasterReference).filter(MasterReference.category == category)

            if only_active:
                query = query.filter(MasterReference.is_active == True)

            results = query.order_by(MasterReference.sort_order.asc(), MasterReference.name.asc()).all()
            return [item.to_dict() for item in results]
        finally:
            db.close()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Menambah opsi baru dalam keadaan aktif.

        Args:
            data: Isian opsi; `category`, `code`, dan `name` wajib.

        Returns:
            Opsi yang tersimpan dalam bentuk dict.

        Raises:
            ValueError: Kalau kategori tidak ada di `ReferenceCategory`.
        """
        db: Session = SessionLocal()
        try:
            if data['category'] not in ReferenceCategory.__members__.values():
                raise ValueError(f"Kategori '{data['category']}' tidak valid.")

            new_ref = MasterReference(
                category=data['category'],
                code=data['code'],
                name=data['name'],
                sort_order=data.get('sort_order', 0),
                description=data.get('description', ""),
                is_active=True
            )
            db.add(new_ref)
            db.commit()
            db.refresh(new_ref)
            return new_ref.to_dict()
        except SQLAlchemyError:
            db.rollback()
            raise
        finally:
            db.close()

    def update(self, id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Mengubah nama, kode, urutan, keterangan, atau status aktif opsi.

        Args:
            id: Id opsi.
            data: Kolom yang diubah.

        Returns:
            Opsi setelah diubah, atau None bila tidak ditemukan.
        """
        db: Session = SessionLocal()
        try:
            ref = db.query(MasterReference).filter(MasterReference.id == id).first()
            if not ref:
                return None

            if 'name' in data: ref.name = data['name']
            if 'code' in data: ref.code = data['code']
            if 'sort_order' in data: ref.sort_order = data['sort_order']
            if 'description' in data: ref.description = data['description']
            if 'is_active' in data: ref.is_active = data['is_active']

            db.commit()
            db.refresh(ref)
            return ref.to_dict()
        finally:
            db.close()

    def delete(self, id: int) -> bool:
        """Menonaktifkan opsi tanpa menghapus barisnya.

        Baris dipertahankan karena data lama masih bisa merujuk nilainya.

        Args:
            id: Id opsi.

        Returns:
            True bila opsi ditemukan dan dinonaktifkan.
        """
        db: Session = SessionLocal()
        try:
            ref = db.query(MasterReference).filter(MasterReference.id == id).first()
            if not ref:
                return False

            ref.is_active = False
            db.commit()
            return True
        finally:
            db.close()
