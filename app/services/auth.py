from sqlalchemy.orm import Session
from app.models.user import user
from app.services.hash import verify_password

def login_user(db: Session, nuptk: str, kata_sandi: str):
    user = db.query(user).filter(user.nuptk == nuptk).first()
    if not user:
        return None
    if not verify_password(kata_sandi, user.kata_sandi):
        return None
    return user