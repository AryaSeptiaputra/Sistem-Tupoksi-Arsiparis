from sqlalchemy.orm import Session
from app.models.incoming_letter import IncomingLetter
import datetime

def create_incoming_letter(db: Session, letter_data: dict, user_id: int) -> IncomingLetter:
    """
    Creates a new incoming letter record.
    """
    new_letter = IncomingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'], 
        received_date=letter_data['received_date'],
        sender=letter_data['sender'],
        subject=letter_data['subject'],
        attachment_path=letter_data.get('attachment_path'),
        classification_id=letter_data['classification_id'],
        user_id=user_id,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_letter)
    db.commit()
    db.refresh(new_letter)
    return new_letter

def update_incoming_letter(db: Session, letter_id: int, update_data: dict) -> IncomingLetter | None:
    """
    Updates an existing incoming letter.
    """
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    for key, value in update_data.items():
        if key == 'id' or key == 'user_id': 
            continue
        if hasattr(existing_letter, key):
            setattr(existing_letter, key, value)
            
    existing_letter.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_letter)
    return existing_letter

def delete_incoming_letter(db: Session, letter_id: int) -> IncomingLetter | None:
    """
    Deletes an incoming letter by ID.
    """
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_incoming_letters(db: Session) -> list[IncomingLetter]:
    """
    Retrieves all incoming letters.
    """
    return db.query(IncomingLetter).all()

def get_incoming_letter_by_key(db: Session, key: str, value: str) -> list[IncomingLetter]:
    """
    Retrieves incoming letters filtered by a specific column key.
    """
    if not hasattr(IncomingLetter, key):
        raise ValueError(f"Invalid column '{key}' for IncomingLetter.")
    
    column_to_filter = getattr(IncomingLetter, key)
    return db.query(IncomingLetter).filter(column_to_filter == value).all()