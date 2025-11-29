from sqlalchemy.orm import Session
from app.models.classification import Classification
import datetime

def create_classification(db: Session, classification_data: dict) -> Classification:
    """
    Creates a new letter classification category.
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
    Updates an existing classification.
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
    Deletes a classification by ID.
    """
    existing_classification = db.query(Classification).filter(Classification.id == classification_id).first()
    if not existing_classification:
        return None

    db.delete(existing_classification)
    db.commit()
    return existing_classification

def get_all_classifications(db: Session) -> list[Classification]:
    """
    Retrieves all classifications.
    """
    return db.query(Classification).all()

def get_classification_by_key(db: Session, key: str, value: str) -> list[Classification]:
    """
    Retrieves classifications filtered by a specific column key.
    """
    if not hasattr(Classification, key):
        raise ValueError(f"Invalid column '{key}' for Classification.")
    
    column_to_filter = getattr(Classification, key)
    return db.query(Classification).filter(column_to_filter == value).all()