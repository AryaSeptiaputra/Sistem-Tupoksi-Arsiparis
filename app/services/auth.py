from sqlalchemy.orm import Session
from app.models.user import user
from app.services.hash import verify_password

def login_user(db: Session, nuptk: str, password: str):
    existing_user = db.query(user).filter(user.nuptk == nuptk).first()
    if not existing_user:
        return None
    if not verify_password(password, existing_user.password):
        return None
    return existing_user