from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hash import get_password_hash
from app.utils.password import check_password, validate_password_change
import datetime

def create_user(db: Session, user_data: dict) -> User:
    """
    Creates a new user and securely hashes their password.

    This function validates the password strength before hashing it and 
    storing the new user record.

    Args:
        db (Session): The database session.
        user_data (dict): A dictionary containing user details. Must include:
            'nuptk', 'username', 'password', 'role', and 'status'.

    Returns:
        User: The newly created user with the hashed password.
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
    Updates user details and handles secure password changes.

    If the 'password' key is present in `update_data`, this function validates
    the password change logic and re-hashes the new password before saving.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        update_data (dict): Fields to update. 

    Returns:
        User | None: The updated user record, or None if the user ID is not found.
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
    Deletes a user account by ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        User | None: The deleted user record, or None if the ID was not found.
    """
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        return None

    db.delete(existing_user)
    db.commit()
    return existing_user

def get_all_users(db: Session) -> list[User]:
    """
    Retrieves all registered users from the database.

    Args:
        db (Session): The database session.

    Returns:
        list[User]: A list of all users.
    """
    return db.query(User).all()

def get_users_by_keys(db: Session, filters: dict) -> list[User]:
    """
    Retrieves user records filtered by specific attributes.

    Args:
        db (Session): The database session.
        filters (dict): A dictionary of key-value pairs to filter the query.
            Keys must match valid column names in the User model (e.g., 
            {"role": "admin", "status": "active"}).

    Returns:
        list[User]: A list of users that match the filter criteria.

    Raises:
        ValueError: If a provided filter key is not a valid column attribute
            of the User model.
    """
    query = db.query(User)
    
    for key, value in filters.items():
        if not hasattr(User, key):
            raise ValueError(f"Invalid column '{key}' for User.")
        
        column_to_filter = getattr(User, key)
        query = query.filter(column_to_filter == value)
        
    return query.all()