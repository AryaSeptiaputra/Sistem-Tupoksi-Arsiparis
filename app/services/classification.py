from sqlalchemy.orm import Session
from app.models.classification import Classification
import datetime

def create_classification(db: Session, classification_data: dict) -> Classification:
    """
    Creates a new letter classification category.

    Args:
        db (Session): The database session.
        classification_data (dict): A dictionary containing classification details.
            Expected keys: 'name', 'code', and optionally 'description'.

    Returns:
        Classification: The newly created classification record.
    """
    new_classification = Classification(
        name=classification_data['name'],
        code=classification_data['code'],
        description=classification_data.get('description'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_classification)
    db.commit()
    db.refresh(new_classification)
    return new_classification

def update_classification(db: Session, classification_id: int, update_data: dict) -> Classification | None:
    """
    Updates an existing classification category.

    Args:
        db (Session): The database session.
        classification_id (int): The ID of the classification to update.
        update_data (dict): A dictionary of fields to update. Keys should match 
            valid column names in the Classification model (e.g., 'name', 'code').

    Returns:
        Classification | None: The updated classification record, or None if 
            the classification ID was not found.
    """
    existing_classification = db.query(Classification).filter(Classification.id == classification_id).first()
    if not existing_classification:
        return None

    for key, value in update_data.items():
        if hasattr(existing_classification, key):
            setattr(existing_classification, key, value)
    
    existing_classification.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_classification)
    return existing_classification

def delete_classification(db: Session, classification_id: int) -> Classification | None:
    """
    Deletes a classification category by its ID.

    Args:
        db (Session): The database session.
        classification_id (int): The ID of the classification to delete.

    Returns:
        Classification | None: The deleted record, or None if the ID was not found.
    """
    existing_classification = db.query(Classification).filter(Classification.id == classification_id).first()
    if not existing_classification:
        return None

    db.delete(existing_classification)
    db.commit()
    return existing_classification

def get_all_classifications(db: Session) -> list[Classification]:
    """
    Retrieves all classification categories.

    Args:
        db (Session): The database session.

    Returns:
        list[Classification]: A list of all classifications.
    """
    return db.query(Classification).all()

def get_classifications_by_keys(db: Session, filters: dict) -> list[Classification]:
    """
    Retrieves classifications based on dynamic filter criteria.

    Args:
        db (Session): The database session.
        filters (dict): Key-value pairs matching column names and their expected values
            (e.g., {"code": "A.1"}).

    Returns:
        list[Classification]: A list of matching classification records.

    Raises:
        ValueError: If a provided filter key is not a valid column attribute.
    """
    query = db.query(Classification)
    
    for key, value in filters.items():
        if not hasattr(Classification, key):
            raise ValueError(f"Invalid column '{key}' for Classification.")
        
        column_to_filter = getattr(Classification, key)
        query = query.filter(column_to_filter == value)
        
    return query.all()