from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hash import get_password_hash
from app.utils.password import check_password, validate_password_change
import datetime

def create_user(db: Session, user_data: dict) -> User:
    """
    Creates a new user with hashed password.
    """
    check_password(user_data['password'])

    hashed_password = get_password_hash(user_data['password'])

    new_user = User(
        nuptk=user_data['nuptk'],
        username=user_data['username'],
        password=hashed_password,
        role=user_data['role'],
        status=user_data['status'],
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, update_data: dict) -> User | None:
    """
    Updates user details, including secure password change validation.
    """
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        return None

    for key, value in update_data.items():
        if key == 'id':
            continue
        
        if not hasattr(existing_user, key):
            continue

        if key == 'password':
            validate_password_change(existing_user.password, value)
            value = get_password_hash(value)

        setattr(existing_user, key, value)
    
    existing_user.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_user)
    return existing_user

def delete_user(db: Session, user_id: int) -> User | None:
    """
    Deletes a user by ID.
    """
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        return None

    db.delete(existing_user)
    db.commit()
    return existing_user

def get_all_users(db: Session) -> list[User]:
    """
    Retrieves all users.
    """
    return db.query(User).all()

def get_user_by_key(db: Session, key: str, value: str) -> list[User]:
    """
    Retrieves users filtered by a specific column key.
    """
    if not hasattr(User, key):
        raise ValueError(f"Invalid column '{key}' for User.")

    column_to_filter = getattr(User, key)
    return db.query(User).filter(column_to_filter == value).all()