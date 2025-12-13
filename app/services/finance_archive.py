from sqlalchemy.orm import Session
from app.models.finance_archive import FinanceArchive
import datetime

# [UBAH] Hapus user_id dari parameter
def create_finance_archive(db: Session, data: dict) -> FinanceArchive:
    """
    Creates a new finance archive record.
    """
    new_archive = FinanceArchive(
        title=data['title'],
        fiscal_year=int(data['fiscal_year']),
        period_month=int(data['period_month']) if data.get('period_month') else None,
        
        category=data.get('category', 'bos_reguler'), # String
        amount=int(data['amount']) if data.get('amount') else 0,
        description=data.get('description'),
        attachment_path=data.get('attachment_path'),
        
        classification_id=int(data['classification_id']),
        storage_location_id=int(data['storage_location_id']) if data.get('storage_location_id') else None,
        
        archive_status=data.get('archive_status', 'active'), # String
        
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_archive)
    db.commit()
    db.refresh(new_archive)
    return new_archive

def update_finance_archive(db: Session, archive_id: int, update_data: dict) -> FinanceArchive | None:
    archive = db.query(FinanceArchive).filter(FinanceArchive.id == archive_id).first()
    if not archive: return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: continue
        
        if hasattr(archive, key):
            # Handle Numeric Conversions
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
    archive = db.query(FinanceArchive).filter(FinanceArchive.id == archive_id).first()
    if not archive: return None
    db.delete(archive)
    db.commit()
    return archive

def get_all_finance_archives(db: Session) -> list[FinanceArchive]:
    return db.query(FinanceArchive).order_by(FinanceArchive.fiscal_year.desc(), FinanceArchive.created_at.desc()).all()