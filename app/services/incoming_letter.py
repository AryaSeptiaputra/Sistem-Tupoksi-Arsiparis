from sqlalchemy.orm import Session
from app.models.incoming_letter import IncomingLetter
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

def get_all_incoming_letters(db: Session) -> list[IncomingLetter]:
    return db.query(IncomingLetter).all()

def get_incoming_letters_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data incoming letter dengan pagination.
    Mengembalikan dict dengan keys: 'incoming_letters', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(IncomingLetter)
    total = query.count()
    incoming_letters = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'incoming_letters': incoming_letters,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_incoming_letters_by_keys(db: Session, filters: dict) -> list[IncomingLetter]:
    query = db.query(IncomingLetter)
    
    for key, value in filters.items():
        if not hasattr(IncomingLetter, key):
            continue 
        
        column_to_filter = getattr(IncomingLetter, key)
        if key.endswith('_id') or key == 'archive_status':
            query = query.filter(column_to_filter == value)
        elif key == 'id':
            query = query.filter(column_to_filter == value)
        else:
            query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()