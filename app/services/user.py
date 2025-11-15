from sqlalchemy.orm import Session
from app.models.user import user
from app.services.hash import get_password_hash
from app.services.password import check_password, validate_password_change
import datetime

def create_user(db: Session, user_data: dict) -> user:
    check_password(user_data['password'])

    hashed_password = get_password_hash(user_data['password'])

    new_user = user(
        nuptk=user_data['nuptk'],
        username=user_data['username'],
        password=hashed_password,
        role=user_data['role'],
        status=user_data['status'],
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, nuptk: str, update_data: dict):
    existing_user = db.query(user).filter(user.nuptk == nuptk).first()
    if not existing_user:
        ValueError("User not found")

    for key, value in update_data.items():
        if key == 'password':
            validate_password_change(existing_user.password, value)
            value = get_password_hash(value)

        setattr(existing_user, key, value)
    
    existing_user.updated_at = datetime.datetime.now().isoformat()
    
    db.commit()
    db.refresh(existing_user)
    return existing_user

def delete_user(db: Session, nuptk: str):
    existing_user = db.query(user).filter(user.nuptk == nuptk).first()
    if not existing_user:
        return None

    db.delete(existing_user)
    db.commit()
    return existing_user

def get_all_users(db: Session):
    return db.query(user).all()

def get_user_by_key(db: Session, key: str, value: str) -> user | None:
    if not hasattr(user, key):
        raise ValueError(f"Kolom pencarian '{key}' tidak valid.")

    column_to_filter = getattr(user, key)
    
    return db.query(user).filter(column_to_filter == value).all()