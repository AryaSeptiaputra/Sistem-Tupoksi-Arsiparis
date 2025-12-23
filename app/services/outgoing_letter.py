from sqlalchemy.orm import Session
from app.models.outgoing_letter import OutgoingLetter
import datetime

def create_outgoing_letter(db: Session, letter_data: dict) -> OutgoingLetter:
    new_letter = OutgoingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'],
        sent_date=letter_data['sent_date'],
        destination=letter_data['destination'],
        subject=letter_data['subject'],
        is_decree=letter_data['is_decree'],
        attachment_path=letter_data.get('attachment_path'),
        classification_id=letter_data['classification_id'],
        storage_location_id=letter_data.get('storage_location_id'), 
        
        archive_status=letter_data.get('archive_status', 'active'),
        
        # [BARU] Default 'pending' saat dibuat
        approval_status=letter_data.get('approval_status', 'pending'),
        
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return new_letter

def update_outgoing_letter(db: Session, letter_id: int, update_data: dict) -> OutgoingLetter | None:
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    for key, value in update_data.items():
        if key in ['id', 'created_at']: 
            continue
        
        if hasattr(existing_letter, key):
            setattr(existing_letter, key, value)
            
    existing_letter.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_letter)
    return existing_letter

def delete_outgoing_letter(db: Session, letter_id: int) -> OutgoingLetter | None:
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_outgoing_letters(db: Session) -> list[OutgoingLetter]:
    return db.query(OutgoingLetter).all()

def get_outgoing_letters_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data outgoing letter dengan pagination.
    Mengembalikan dict dengan keys: 'outgoing_letters', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(OutgoingLetter)
    total = query.count()
    outgoing_letters = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'outgoing_letters': outgoing_letters,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_outgoing_letters_by_keys(db: Session, filters: dict) -> list[OutgoingLetter]:
    query = db.query(OutgoingLetter)
    
    for key, value in filters.items():
        if not hasattr(OutgoingLetter, key):
            continue
        
        column_to_filter = getattr(OutgoingLetter, key)
        # Exact match untuk status & boolean
        if key == 'archive_status' or key == 'is_decree' or key.endswith('_id'):
            query = query.filter(column_to_filter == value)
        else:
            query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()