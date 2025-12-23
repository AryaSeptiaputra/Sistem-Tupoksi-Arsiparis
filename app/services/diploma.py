from sqlalchemy.orm import Session
from app.models.diploma import Diploma
import datetime

# [UBAH] Hapus parameter user_id
def create_diploma(db: Session, data: dict) -> Diploma:
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

def update_diploma(db: Session, diploma_id: int, update_data: dict) -> Diploma | None:
    existing = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing:
        return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: 
            continue
        
        # Logika: Jika diubah jadi 'Sudah Diambil' tapi tidak ada tanggal, set tanggal sekarang
        if key == 'is_collected' and value is True:
            if not existing.collected_at and not update_data.get('collected_at'):
                existing.collected_at = datetime.datetime.now()
        
        # Logika: Jika diubah jadi 'Belum Diambil', hapus tanggal
        if key == 'is_collected' and value is False:
            existing.collected_at = None

        if hasattr(existing, key):
            setattr(existing, key, value)

    existing.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing)
    return existing

def delete_diploma(db: Session, diploma_id: int) -> Diploma | None:
    existing = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing: 
        return None
    
    db.delete(existing)
    db.commit()
    return existing

def get_all_diplomas(db: Session) -> list[Diploma]:
    return db.query(Diploma).all()

def get_diplomas_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data diploma dengan pagination.
    Mengembalikan dict dengan keys: 'diplomas', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(Diploma)
    total = query.count()
    diplomas = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'diplomas': diplomas,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_diplomas_by_keys(db: Session, filters: dict) -> list[Diploma]:
    query = db.query(Diploma)
    
    for key, value in filters.items():
        if not hasattr(Diploma, key): continue
        
        col = getattr(Diploma, key)
        
        if key == 'storage_location_id' or isinstance(value, bool):
            query = query.filter(col == value)
        else:
            query = query.filter(col.ilike(f"%{value}%"))
            
    return query.all()