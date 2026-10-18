import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def _prepare_password(password: str) -> str:
    # Prehash SHA-256 menyeragamkan panjang dan encoding kata sandi sebelum argon2
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_password_hash(password: str) -> str:
    """Membuat hash argon2 dari kata sandi polos.

    Args:
        password: Kata sandi polos.

    Returns:
        Hash yang siap disimpan di database.
    """
    prepared = _prepare_password(password)
    return pwd_context.hash(prepared)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mencocokkan kata sandi polos dengan hash tersimpan.

    Args:
        plain_password: Kata sandi yang dimasukkan pengguna.
        hashed_password: Hash dari database.

    Returns:
        True bila cocok.
    """
    prepared = _prepare_password(plain_password)
    return pwd_context.verify(prepared, hashed_password)
