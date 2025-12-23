from sqlalchemy.orm import Session
from app.models.classification import Classification
import datetime

def create_classification(db: Session, data: dict) -> Classification:
    new_cls = Classification(
        name=data['name'],
        code=data['code'],
        description=data.get('description'),
        retention_active_period=data.get('retention_active_period', 1),
        retention_inactive_period=data.get('retention_inactive_period', 2),
        final_action=data.get('final_action', 'destroy') # Default string 'destroy'
    )
    
    db.add(new_cls)
    db.commit()
    db.refresh(new_cls)
    return new_cls

def update_classification(db: Session, cls_id: int, data: dict) -> Classification | None:
    cls = db.query(Classification).filter(Classification.id == cls_id).first()
    if not cls:
        return None

    for key, value in data.items():
        if key == 'id': continue
        if hasattr(cls, key):
            setattr(cls, key, value)
    
    cls.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(cls)
    return cls

def delete_classification(db: Session, cls_id: int) -> Classification | None:
    cls = db.query(Classification).filter(Classification.id == cls_id).first()
    if not cls:
        return None
    
    db.delete(cls)
    db.commit()
    return cls

def get_all_classifications(db: Session) -> list[Classification]:
    return db.query(Classification).all()

def get_classifications_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data classification dengan pagination.
    Mengembalikan dict dengan keys: 'classifications', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(Classification)
    total = query.count()
    classifications = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'classifications': classifications,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_classifications_by_keys(db: Session, filters: dict) -> list[Classification]:
    query = db.query(Classification)
    for key, value in filters.items():
        if hasattr(Classification, key):
            col = getattr(Classification, key)
            query = query.filter(col.ilike(f"%{value}%"))
    return query.all()