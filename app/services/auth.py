from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hash import verify_password

def login_user(db: Session, nuptk: str, password: str) -> User | None:
    """
    Authenticates a user by NUPTK and password.
    """
    existing_user = db.query(User).filter(User.nuptk == nuptk).first()
    
    if not existing_user:
        return None
    
    if not verify_password(password, existing_user.password):
        return None
        
    return existing_user