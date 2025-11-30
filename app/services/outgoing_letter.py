from sqlalchemy.orm import Session
from app.models.outgoing_letter import OutgoingLetter
import datetime

def create_outgoing_letter(db: Session, letter_data: dict, user_id: int) -> OutgoingLetter:
    """
    Creates a new outgoing letter record in the database.

    Args:
        db (Session): The database session.
        letter_data (dict): A dictionary containing letter details. Expected keys:
            'number', 'letter_date', 'sent_date', 'destination', 'subject',
            'is_decree', 'classification_id', and optionally 'attachment_path'.
        user_id (int): The ID of the user creating the record.

    Returns:
        OutgoingLetter: The newly created outgoing letter record.
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
    Updates an existing outgoing letter record.

    Args:
        db (Session): The database session.
        letter_id (int): The ID of the letter to update.
        update_data (dict): A dictionary of fields to update. Keys 'id' and 
            'user_id' will be ignored to preserve integrity.

    Returns:
        OutgoingLetter | None: The updated record, or None if not found.
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
    Deletes an outgoing letter record by its ID.

    Args:
        db (Session): The database session.
        letter_id (int): The ID of the letter to delete.

    Returns:
        OutgoingLetter | None: The deleted record, or None if the ID was not found.
    """
    existing_letter = db.query(OutgoingLetter).filter(OutgoingLetter.id == letter_id).first()
    if not existing_letter:
        return None

    db.delete(existing_letter)
    db.commit()
    return existing_letter

def get_all_outgoing_letters(db: Session) -> list[OutgoingLetter]:
    """
    Retrieves all outgoing letter records from the database.

    Args:
        db (Session): The database session.

    Returns:
        list[OutgoingLetter]: A list of all outgoing letters.
    """
    return db.query(OutgoingLetter).all()

def get_outgoing_letters_by_keys(db: Session, filters: dict) -> list[OutgoingLetter]:
    """
    Retrieves outgoing letter records filtered by specific attributes.

    Args:
        db (Session): The database session.
        filters (dict): A dictionary of key-value pairs to filter the query.
            Keys must match valid column names in the OutgoingLetter model
            (e.g., {"is_decree": True, "destination": "Sekolah"}).

    Returns:
        list[OutgoingLetter]: A list of outgoing letters matching the filter criteria.

    Raises:
        ValueError: If a provided filter key is not a valid column attribute
            of the OutgoingLetter model.
    """
    query = db.query(OutgoingLetter)
    
    for key, value in filters.items():
        if not hasattr(OutgoingLetter, key):
            raise ValueError(f"Invalid column '{key}' for OutgoingLetter.")
        
        column_to_filter = getattr(OutgoingLetter, key)
        query = query.filter(column_to_filter == value)
        
    return query.all()