import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hash import get_password_hash, verify_password
from app.utils.password import check_password, validate_password_change

def get_user(db: Session, user_id: int) -> User | None:
    """
    Mengambil akun berdasarkan id.

    Args:
        db (Session): Sesi database.
        user_id (int): Id akun.

    Returns:
        User | None: Akun, atau None bila tidak ada.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Mengambil akun berdasarkan username.

    Args:
        db (Session): Sesi database.
        username (str): Username yang dicari, persis sama.

    Returns:
        User | None: Akun, atau None bila tidak ada.
    """
    return db.query(User).filter(User.username == username).first()

def has_active_user(db: Session) -> bool:
    """
    Menjawab apakah sudah ada akun aktif. Aplikasi hanya boleh punya satu.

    Args:
        db (Session): Sesi database.

    Returns:
        bool: True bila ada akun dengan is_active True.
    """
    return db.query(User).filter(User.is_active.is_(True)).first() is not None

def _validate_username_free(db: Session, username: str, own_id: int | None = None) -> None:
    other = get_user_by_username(db, username)
    if other and other.id != own_id:
        raise ValueError(f"Username '{username}' sudah dipakai.")

def _validate_required(value: str, label: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{label} wajib diisi.")
    return value

def create_user(db: Session, username: str, display_name: str, password: str) -> User:
    """
    Membuat akun operator. Ditolak bila sudah ada akun aktif.

    Args:
        db (Session): Sesi database.
        username (str): Username login.
        display_name (str): Nama tampilan.
        password (str): Kata sandi polos; harus lolos `check_password`.

    Returns:
        User: Akun baru.

    Raises:
        ValueError: Sudah ada akun aktif, username dipakai, isian kosong,
            atau kata sandi lemah.
    """
    if has_active_user(db):
        raise ValueError("Sudah ada akun aktif. Aplikasi ini hanya untuk satu pengguna.")
    username = _validate_required(username, "Username")
    display_name = _validate_required(display_name, "Nama tampilan")
    _validate_username_free(db, username)
    check_password(password)

    new_user = User(
        username=username,
        display_name=display_name,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_profile(db: Session, user_id: int, username: str, display_name: str) -> User | None:
    """
    Mengubah username dan nama tampilan akun.

    Args:
        db (Session): Sesi database.
        user_id (int): Id akun yang diubah.
        username (str): Username baru.
        display_name (str): Nama tampilan baru.

    Returns:
        User | None: Akun yang sudah diubah, atau None bila tidak ada.

    Raises:
        ValueError: Isian kosong atau username dipakai akun lain.
    """
    existing_user = get_user(db, user_id)
    if not existing_user:
        return None

    username = _validate_required(username, "Username")
    display_name = _validate_required(display_name, "Nama tampilan")
    _validate_username_free(db, username, own_id=user_id)

    existing_user.username = username
    existing_user.display_name = display_name
    db.commit()
    db.refresh(existing_user)
    return existing_user

def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> User | None:
    """
    Mengganti kata sandi setelah kata sandi lama dicocokkan.

    Args:
        db (Session): Sesi database.
        user_id (int): Id akun.
        old_password (str): Kata sandi saat ini.
        new_password (str): Kata sandi baru.

    Returns:
        User | None: Akun yang sudah diubah, atau None bila tidak ada.

    Raises:
        ValueError: Kata sandi lama salah, atau kata sandi baru lemah
            atau sama dengan yang lama.
    """
    existing_user = get_user(db, user_id)
    if not existing_user:
        return None

    if not verify_password(old_password or "", existing_user.password_hash):
        raise ValueError("Kata sandi lama salah.")
    validate_password_change(existing_user.password_hash, new_password)

    existing_user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(existing_user)
    return existing_user

def reset_password(db: Session, username: str, new_password: str) -> User:
    """
    Mengganti kata sandi tanpa kata sandi lama. Hanya dipanggil dari CLI di server.

    Args:
        db (Session): Sesi database.
        username (str): Username akun.
        new_password (str): Kata sandi baru; harus lolos `check_password`.

    Returns:
        User: Akun yang sudah diubah.

    Raises:
        ValueError: Username tidak ditemukan atau kata sandi lemah.
    """
    existing_user = get_user_by_username(db, username)
    if not existing_user:
        raise ValueError(f"Username '{username}' tidak ditemukan.")
    check_password(new_password)

    existing_user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(existing_user)
    return existing_user

def record_login(db: Session, user: User) -> None:
    """
    Menyimpan waktu login terakhir.

    Args:
        db (Session): Sesi database.
        user (User): Akun yang baru saja berhasil login.
    """
    user.last_login_at = datetime.datetime.now()
    db.commit()
