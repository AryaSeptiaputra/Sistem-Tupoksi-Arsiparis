from sqlalchemy.orm import Session
from app.models.employee_archive import EmployeeArchive
import datetime

# [UBAH] create menerima owner_id (ID Teacher), bukan user_id/uploader
def create_employee_archive(db: Session, data: dict) -> EmployeeArchive:
    new_archive = EmployeeArchive(
        document_name=data['document_name'],
        document_type=data.get('document_type', 'lainnya'), # String
        document_year=int(data['document_year']) if data.get('document_year') else None,
        description=data.get('description'),
        attachment_path=data.get('attachment_path'),
        
        # Relasi ke Teacher (Owner)
        owner_id=int(data['owner_id']), 
        
        storage_location_id=int(data['storage_location_id']) if data.get('storage_location_id') else None,
        
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
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
            # Konversi Integer
            if key == 'owner_id' or key == 'storage_location_id' or key == 'document_year':
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

# Cari berdasarkan ID Guru (Owner)
def get_archives_by_owner(db: Session, owner_id: int) -> list[EmployeeArchive]:
    return db.query(EmployeeArchive).filter(EmployeeArchive.owner_id == owner_id).all()