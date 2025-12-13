import re
from app.utils.hash import verify_password  # Import ini WAJIB ada

def check_password(password: str) -> bool:
    """
    Validates the strength of a password based on complexity rules.
    
    Rules:
    - Minimum 8 characters.
    - At least one uppercase letter.
    - At least one lowercase letter.
    - At least one digit.
    - At least one special character.
    
    Args:
        password (str): The password to validate.
        
    Raises:
        ValueError: If any of the complexity rules are violated.
        
    Returns:
        bool: True if the password is strong.
    """
    if len(password) < 8:
        raise ValueError("Password minimal 8 karakter")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password harus mengandung setidaknya satu huruf besar (A-Z)")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password harus mengandung setidaknya satu huruf kecil (a-z)")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password harus mengandung setidaknya satu angka (0-9)")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        raise ValueError("Password harus mengandung setidaknya satu karakter spesial (!@#$%^&*)")
    return True

def validate_password_change(old_password_hash: str, new_password_plain: str) -> bool:
    """
    Validates that the new password is strong and different from the old one.
    
    Args:
        old_password_hash (str): The hashed password currently stored in DB.
        new_password_plain (str): The new plaintext password input by user.
        
    Raises:
        ValueError: If the new password is the same as the old one or is weak.
    """
    if verify_password(new_password_plain, old_password_hash):
        raise ValueError("Password baru harus berbeda dari password lama")
    
    return check_password(new_password_plain)

def mask_password(password: str) -> str:
    """
    Masks the password for safe display in logs or UIs.

    It keeps the first and last characters visible while masking the middle
    characters with asterisks. If the password is very short (<= 2 chars),
    it masks the entire string.

    Args:
        password (str): The sensitive password string.

    Returns:
        str: The masked version of the password.
    """
    if not password:
        return ""
        
    if len(password) <= 2:
        return '*' * len(password)
        
    return password[0] + '*' * (len(password) - 2) + password[-1]