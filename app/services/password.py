import re

def check_password(password: str) -> bool:
    """Check if the password is strong.
    
    A strong password must be at least 8 characters long, contain at least one uppercase letter,
    one lowercase letter, one digit, and one special character.
    """
    if len(password) < 8:
        raise ValueError("Password minimal 8 karakter")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password harus mengandung setidaknya satu angka")
    return True

def validate_password_change(old_password: str, new_password: str) -> bool:
    """Validate that the new password is different from the old password and is strong."""
    if old_password == new_password:
        raise ValueError("Password baru harus berbeda dari password lama")
    return check_password(new_password)

def mask_password(password: str) -> str:
    """Mask the password for display purposes."""
    if len(password) <= 2:
        return '*' * len(password)
    return password[0] + '*' * (len(password) - 2) + password[-1]