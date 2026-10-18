import re
from app.utils.hash import verify_password

def check_password(password: str) -> bool:
    """Memeriksa kekuatan kata sandi.

    Aturannya: minimal 8 karakter, berisi huruf besar, huruf kecil, dan angka.

    Args:
        password: Kata sandi polos.

    Returns:
        True bila kata sandi memenuhi semua aturan.

    Raises:
        ValueError: Kalau salah satu aturan tidak terpenuhi.
    """
    if len(password) < 8:
        raise ValueError("Password minimal 8 karakter")
    # Minimal satu huruf besar A-Z
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password harus mengandung setidaknya satu huruf besar (A-Z)")
    # Minimal satu huruf kecil a-z
    if not re.search(r'[a-z]', password):
        raise ValueError("Password harus mengandung setidaknya satu huruf kecil (a-z)")
    # Minimal satu angka 0-9
    if not re.search(r'[0-9]', password):
        raise ValueError("Password harus mengandung setidaknya satu angka (0-9)")

    return True

def validate_password_change(old_password_hash: str, new_password_plain: str) -> bool:
    """Memeriksa bahwa kata sandi baru kuat dan berbeda dari yang lama.

    Args:
        old_password_hash: Hash kata sandi yang tersimpan.
        new_password_plain: Kata sandi baru dalam bentuk polos.

    Returns:
        True bila kata sandi baru boleh dipakai.

    Raises:
        ValueError: Kalau kata sandi baru sama dengan yang lama atau terlalu lemah.
    """
    if verify_password(new_password_plain, old_password_hash):
        raise ValueError("Password baru harus berbeda dari password lama")

    return check_password(new_password_plain)
