from sqlalchemy.orm import Session
from app.models.classification import Classification
from app.utils.pagination import PaginationParams, paginate_query, PaginatedResult
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

def get_all_classifications(db: Session, pagination: PaginationParams = None) -> PaginatedResult | list[Classification]:
    query = db.query(Classification).order_by(Classification.id.desc())

    if pagination:
        return paginate_query(query, pagination)

    return query.all()

def get_classifications_by_keys(db: Session, filters: dict) -> list[Classification]:
    query = db.query(Classification)
    for key, value in filters.items():
        if hasattr(Classification, key):
            col = getattr(Classification, key)
            query = query.filter(col.ilike(f"%{value}%"))
    return query.all()