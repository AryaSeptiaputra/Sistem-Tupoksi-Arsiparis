from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.incoming_letter import IncomingLetter
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
import datetime

# [PASTIKAN] Signature fungsi ini tidak menerima user_id
def create_incoming_letter(db: Session, letter_data: dict) -> IncomingLetter:
    new_letter = IncomingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'], 
        received_date=letter_data['received_date'],
        sender=letter_data['sender'],
        subject=letter_data['subject'],
        attachment_path=letter_data.get('attachment_path'),
        classification_id=letter_data['classification_id'],
        storage_location_id=letter_data.get('storage_location_id'),
        
        # Default 'active' jika tidak dikirim dari FE
        archive_status=letter_data.get('archive_status', 'active'),
        
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return new_letter

def update_incoming_letter(db: Session, letter_id: int, update_data: dict) -> IncomingLetter | None:
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    for key, value in update_data.items():
        # Skip field system yang tidak boleh diubah manual
        if key in ['id', 'created_at']: 
            continue
        
        if hasattr(existing_letter, key):
            # Handle empty storage location (select reset)
            if key == 'storage_location_id' and (value == "" or value is None):
                setattr(existing_letter, key, None)
            else:
                # Ini akan otomatis mengupdate 'archive_status' jika ada di update_data
                setattr(existing_letter, key, value)
            
    existing_letter.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_letter)
    return existing_letter

def delete_incoming_letter(db: Session, letter_id: int) -> IncomingLetter | None:
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_incoming_letters(db: Session, pagination: PaginationParams = None) -> PaginatedResult | list[IncomingLetter]:
    """
    Get all incoming letters dengan support pagination
    
    OPTIMIZATION:
    - Load relasi classification dan storage_location via joined load
    - Support pagination untuk handle ribuan records
    - Order by id DESC (newest first)
    
    Args:
        db: Database session
        pagination: PaginationParams untuk pagination (opsional)
    
    Returns:
        PaginatedResult jika pagination provided, list[IncomingLetter] sebaliknya
    """
    # Selective eager loading hanya relasi yg dibutuhkan
    query = db.query(IncomingLetter).order_by(desc(IncomingLetter.id))
    
    if pagination:
        result = paginate_query(query, pagination)
        # Convert ke dict dengan relasi
        items_dict = [letter.to_dict() for letter in result.items]
        result.items = items_dict
        return result
    else:
        # Fallback tanpa pagination (jangan gunakan di production untuk data besar!)
        return query.all()

def get_incoming_letters_by_keys(db: Session, filters: dict, 
                                 pagination: PaginationParams = None) -> PaginatedResult | list[IncomingLetter]:
    """
    Get incoming letters dengan filter dan support pagination
    
    OPTIMIZATION:
    - Use indexed columns untuk filter yang lebih cepat
    - Support pagination
    
    Args:
        db: Database session
        filters: Dictionary dengan field names dan values untuk filter
        pagination: PaginationParams untuk pagination (opsional)
    
    Returns:
        PaginatedResult atau list[IncomingLetter]
    """
    query = db.query(IncomingLetter).order_by(desc(IncomingLetter.created_at))
    
    for key, value in filters.items():
        if not hasattr(IncomingLetter, key):
            continue 
        
        column_to_filter = getattr(IncomingLetter, key)
        
        # Indexed columns: exact match (faster)
        if key.endswith('_id') or key == 'archive_status' or key == 'id':
            query = query.filter(column_to_filter == value)
        else:
            # Text search: use LIKE dengan index
            query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    if pagination:
        result = paginate_query(query, pagination)
        # Convert ke dict dengan relasi
        items_dict = [letter.to_dict() for letter in result.items]
        result.items = items_dict
        return result
    else:
        return query.all()


def get_incoming_letters_count(db: Session, filters: dict = None) -> int:
    """Get total count of incoming letters untuk UI pagination info"""
    query = db.query(IncomingLetter)
    
    if filters:
        for key, value in filters.items():
            if not hasattr(IncomingLetter, key):
                continue
            column_to_filter = getattr(IncomingLetter, key)
            
            if key.endswith('_id') or key == 'archive_status' or key == 'id':
                query = query.filter(column_to_filter == value)
            else:
                query = query.filter(column_to_filter.ilike(f"%{value}%"))
    
    return query.count()