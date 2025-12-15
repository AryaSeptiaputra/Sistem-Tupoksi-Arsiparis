from sqlalchemy.orm import Session
from app.models.master_reference import MasterReference, ReferenceCategory
from app.core.database import SessionLocal

class MasterReferenceService:
    def get_by_category(self, category: str, only_active: bool = True):
        """
        Mengambil list opsi berdasarkan kategori.
        Contoh: get_by_category('school_major')
        """
        db: Session = SessionLocal()
        try:
            query = db.query(MasterReference).filter(MasterReference.category == category)
            
            if only_active:
                query = query.filter(MasterReference.is_active == True)
            
            # Urutkan berdasarkan sort_order (kecil ke besar), lalu nama
            results = query.order_by(MasterReference.sort_order.asc(), MasterReference.name.asc()).all()
            return [item.to_dict() for item in results]
        finally:
            db.close()

    def create(self, data: dict):
        """
        Menambah opsi baru.
        Data harus berisi: category, code, name, dll.
        """
        db: Session = SessionLocal()
        try:
            # Validasi sederhana: Cek apakah kategori valid sesuai Enum
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
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def update(self, id: int, data: dict):
        """
        Mengubah data referensi (misal: ganti nama atau urutan).
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

    def delete(self, id: int):
        """
        Soft delete (hanya set is_active = False) agar data lama tidak rusak.
        Jika ingin hard delete, gunakan db.delete(ref).
        """
        db: Session = SessionLocal()
        try:
            ref = db.query(MasterReference).filter(MasterReference.id == id).first()
            if not ref:
                return False
            
            # Soft Delete
            ref.is_active = False
            db.commit()
            return True
        finally:
            db.close()

    def get_all_categories(self):
        """
        Helper untuk melihat daftar kategori apa saja yang tersedia di sistem.
        """
        return [e.value for e in ReferenceCategory]