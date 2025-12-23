from sqlalchemy.orm import Session
from app.models.employee_archive import EmployeeArchive
import datetime

def create_employee_archive(db: Session, data: dict) -> EmployeeArchive:
    new_archive = EmployeeArchive(
        document_name=data['document_name'],
        document_type=data.get('document_type', 'lainnya'),
        archive_status=data.get('archive_status', 'active'),
        document_year=int(data['document_year']) if data.get('document_year') else None,
        description=data.get('description'),
        attachment_path=data.get('attachment_path'),
        owner_id=int(data['owner_id']),
        
        # Simpan Classification ID
        classification_id=int(data['classification_id']) if data.get('classification_id') else None,
        
        storage_location_id=int(data['storage_location_id']) if data.get('storage_location_id') else None
    )
    
    db.add(new_archive)
    db.commit()
    db.refresh(new_archive)
    return new_archive

def update_employee_archive(db: Session, archive_id: int, update_data: dict) -> EmployeeArchive | None:
    archive = db.query(EmployeeArchive).filter(EmployeeArchive.id == archive_id).first()
    if not archive: return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: continue
        
        if hasattr(archive, key):
            # Konversi Integer untuk Foreign Keys
            if key in ['owner_id', 'storage_location_id', 'document_year', 'classification_id']:
                setattr(archive, key, int(value) if value else None)
            else:
                setattr(archive, key, value)
            
    archive.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(archive)
    return archive

def delete_employee_archive(db: Session, archive_id: int) -> EmployeeArchive | None:
    archive = db.query(EmployeeArchive).filter(EmployeeArchive.id == archive_id).first()
    if not archive: return None
    db.delete(archive)
    db.commit()
    return archive

def get_all_employee_archives(db: Session) -> list[EmployeeArchive]:
    return db.query(EmployeeArchive).all()

def get_employee_archives_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data employee archive dengan pagination.
    Mengembalikan dict dengan keys: 'employee_archives', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(EmployeeArchive)
    total = query.count()
    employee_archives = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'employee_archives': employee_archives,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }