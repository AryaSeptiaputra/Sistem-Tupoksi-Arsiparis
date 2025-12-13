from sqlalchemy.orm import Session
from app.models.user import User
from app.models.teacher import Teacher
from app.utils.hash import verify_password

def login_user(db: Session, identity_number: str, password: str) -> User | None:
    """
    Authenticates a user using their Teacher Identity Number (NIP/NUPTK) and password.
    
    Performs a JOIN query: Looks for a User where the associated Teacher 
    has the matching identity_number.
    """
    # Query: Select User JOIN Teacher WHERE Teacher.identity_number == input
    existing_user = db.query(User).join(Teacher).filter(Teacher.identity_number == identity_number).first()
    
    if not existing_user:
        return None
    
    if not verify_password(password, existing_user.password):
        return None
        
    return existing_user