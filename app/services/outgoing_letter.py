from sqlalchemy.orm import Session
from app.models.outgoing_letter import OutgoingLetter
import datetime

def create_outgoing_letter(db: Session, letter_data: dict, user_id: int) -> OutgoingLetter:
    """
    Creates a new outgoing letter record.
    """
    new_letter = OutgoingLetter(
        number=letter_data['number'],
        letter_date=letter_data['letter_date'],
        sent_date=letter_data['sent_date'],
        destination=letter_data['destination'],
        subject=letter_data['subject'],
        is_decree=letter_data['is_decree'],
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

def update_outgoing_letter(db: Session, letter_id: int, update_data: dict) -> OutgoingLetter | None:
    """
    Updates an existing outgoing letter.
    """
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
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

def delete_outgoing_letter(db: Session, letter_id: int) -> OutgoingLetter | None:
    """
    Deletes an outgoing letter by ID.
    """
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_outgoing_letters(db: Session) -> list[OutgoingLetter]:
    """
    Retrieves all outgoing letters.
    """
    return db.query(OutgoingLetter).all()

def get_outgoing_letter_by_key(db: Session, key: str, value: str) -> list[OutgoingLetter]:
    """
    Retrieves outgoing letters filtered by a specific column key.
    """
    if not hasattr(OutgoingLetter, key):
        raise ValueError(f"Invalid column '{key}' for OutgoingLetter.")
    
    column_to_filter = getattr(OutgoingLetter, key)
    return db.query(OutgoingLetter).filter(column_to_filter == value).all()