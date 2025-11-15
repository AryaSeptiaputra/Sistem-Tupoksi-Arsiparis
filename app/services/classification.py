from sqlalchemy.orm import Session
from app.models.classification import classification
import datetime

def create_classification(db: Session, classification_data: dict) -> classification:
    new_classification = classification(
        name=classification_data['name'],
        code=classification_data['code'],
        description=classification_data.get('description'),
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    
    db.add(new_classification)
    db.commit()
    db.refresh(new_classification)
    return new_classification

def update_classification(db: Session, classification_id: int, update_data: dict):
    existing_classification = db.query(classification).filter(classification.id == classification_id).first()
    if not existing_classification:
        raise ValueError("Classification not found")

    for key, value in update_data.items():
        setattr(existing_classification, key, value)
    
    existing_classification.updated_at = datetime.datetime.now().isoformat()
    
    db.commit()
    db.refresh(existing_classification)
    return existing_classification

def delete_classification(db: Session, classification_id: int):
    existing_classification = db.query(classification).filter(classification.id == classification_id).first()
    if not existing_classification:
        return None

    db.delete(existing_classification)
    db.commit()
    return existing_classification

def get_all_classifications(db: Session):
    return db.query(classification).all()

def get_classification_by_key(db: Session, key: str, value: str) -> classification | None:
    if not hasattr(classification, key):
        raise ValueError(f"Kolom pencarian '{key}' tidak valid.")
    
    column_to_filter = getattr(classification, key)
    return db.query(classification).filter(column_to_filter == value).first()