from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user import get_user_by_username
from app.utils.hash import verify_password

def login_user(db: Session, username: str, password: str) -> User | None:
    """
    Mencocokkan username dan kata sandi akun operator.

    Args:
        db (Session): Sesi database.
        username (str): Username login.
        password (str): Kata sandi polos.

    Returns:
        User | None: Akun bila cocok dan aktif; None bila username tidak ada,
            kata sandi salah, atau akun tidak aktif.
    """
    existing_user = get_user_by_username(db, username)

    if not existing_user or not existing_user.is_active:
        return None

    if not verify_password(password, existing_user.password_hash):
        return None

    return existing_user
