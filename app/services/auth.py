from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hash import verify_password

def login_user(db: Session, nuptk: str, password: str) -> User | None:
    """
    Authenticates a user using their NUPTK and password.

    This function verifies the provided NUPTK against the database and checks
    if the password matches the stored hashed password.

    Args:
        db (Session): The database session.
        nuptk (str): The user's unique NUPTK identifier.
        password (str): The raw password string to verify.

    Returns:
        User | None: The authenticated user object if credentials are valid, 
            or None if the user is not found or the password is incorrect.
    """
    existing_user = db.query(User).filter(User.nuptk == nuptk).first()
    
    if not existing_user:
        return None
    
    if not verify_password(password, existing_user.password):
        return None
        
    return existing_user