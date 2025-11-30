from sqlalchemy.orm import Session
from app.models.incoming_letter import IncomingLetter
import datetime

def create_incoming_letter(db: Session, letter_data: dict, user_id: int) -> IncomingLetter:
    """
    Creates a new incoming letter record in the database.

    Args:
        db (Session): The database session.
        letter_data (dict): A dictionary containing letter details. Expected keys:
            'number', 'letter_date', 'received_date', 'sender', 'subject',
            'classification_id', and optionally 'attachment_path'.
        user_id (int): The ID of the user creating the record.

    Returns:
        IncomingLetter: The newly created incoming letter record.
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
    Updates an existing incoming letter record.

    Args:
        db (Session): The database session.
        letter_id (int): The ID of the letter to update.
        update_data (dict): A dictionary of fields to update. Keys 'id' and 
            'user_id' will be ignored if present.

    Returns:
        IncomingLetter | None: The updated record, or None if the letter ID 
            was not found.
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
    Deletes an incoming letter record by its ID.

    Args:
        db (Session): The database session.
        letter_id (int): The ID of the letter to delete.

    Returns:
        IncomingLetter | None: The deleted record, or None if the ID was not found.
    """
    existing_letter = db.query(IncomingLetter).filter(IncomingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_incoming_letters(db: Session) -> list[IncomingLetter]:
    """
    Retrieves all incoming letter records from the database.

    Args:
        db (Session): The database session.

    Returns:
        list[IncomingLetter]: A list of all incoming letters.
    """
    return db.query(IncomingLetter).all()

def get_incoming_letters_by_keys(db: Session, filters: dict) -> list[IncomingLetter]:
    """
    Retrieves incoming letters filtered by specific column values.

    Args:
        db (Session): The database session.
        filters (dict): Key-value pairs to filter the query. Keys must match 
            valid column names in the IncomingLetter model.

    Returns:
        list[IncomingLetter]: A list of incoming letters matching the filters.

    Raises:
        ValueError: If a key in the filters dictionary does not exist as a 
            column in the model.
    """
    query = db.query(IncomingLetter)
    
    for key, value in filters.items():
        if not hasattr(IncomingLetter, key):
            raise ValueError(f"Invalid column '{key}' for IncomingLetter.")
        
        column_to_filter = getattr(IncomingLetter, key)
        query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()