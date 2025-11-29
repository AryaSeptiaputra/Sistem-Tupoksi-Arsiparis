import hashlib
from passlib.context import CryptContext

# Konfigurasi hashing password menggunakan algoritma bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prepare_password(password: str) -> str:
    """
    Pre-hashes the password using SHA256 before passing it to bcrypt.
    
    This helps in two ways:
    1. It allows passwords longer than 72 bytes (bcrypt's limit).
    2. It normalizes the encoding.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_password_hash(password: str) -> str:
    """
    Generates a secure hash for a given plaintext password.
    
    Args:
        password (str): The plaintext password to hash.
        
    Returns:
        str: The hashed password string.
    """
    prepared = _prepare_password(password)
    return pwd_context.hash(prepared)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plaintext password matches the stored hash.
    
    Args:
        plain_password (str): The plaintext password input by user.
        hashed_password (str): The hashed password stored in the database.
        
    Returns:
        bool: True if passwords match, False otherwise.
    """
    prepared = _prepare_password(plain_password)
    return pwd_context.verify(prepared, hashed_password)