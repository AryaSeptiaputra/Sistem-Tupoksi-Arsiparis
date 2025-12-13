from sqlalchemy.orm import Session
from app.models.user import User
from app.models.teacher import Teacher
from app.utils.hash import get_password_hash
from app.utils.password import check_password, validate_password_change
import datetime

def create_user(db: Session, user_data: dict) -> User:
    """
    Creates a new user account linked to a Teacher.
    """
    # 1. Validasi: Pastikan Teacher ID ada
    teacher_id = user_data.get('teacher_id')
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise ValueError("Data Guru tidak ditemukan.")

    # 2. Validasi: Pastikan Guru ini belum punya akun
    existing_account = db.query(User).filter(User.teacher_id == teacher_id).first()
    if existing_account:
        raise ValueError(f"Guru atas nama '{teacher.full_name}' sudah memiliki akun.")

    # 3. Cek Password Strength
    check_password(user_data['password'])
    hashed_password = get_password_hash(user_data['password'])

    # 4. Simpan (Role & Status sebagai String)
    new_user = User(
        teacher_id=teacher_id,
        password=hashed_password,
        role=user_data['role'],     # String: 'admin', 'headmaster', 'teacher'
        status=user_data['status'], # String: 'active', 'inactive'
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, update_data: dict) -> User | None:
    """
    Updates user details (Role, Status, Password).
    Cannot update teacher_id (Account ownership is fixed).
    """
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        return None

    for key, value in update_data.items():
        if key in ['id', 'teacher_id']: # Prevent changing ID or Owner
            continue
        
        if not hasattr(existing_user, key):
            continue

        if key == 'password':
            # Jika password dikirim tapi kosong, abaikan
            if not value: 
                continue
            validate_password_change(existing_user.password, value)
            value = get_password_hash(value)

        setattr(existing_user, key, value)
    
    existing_user.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_user)
    return existing_user

def delete_user(db: Session, user_id: int) -> User | None:
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        return None

    db.delete(existing_user)
    db.commit()
    return existing_user

def get_all_users(db: Session) -> list[User]:
    # Menggunakan join otomatis via relationship di Model
    return db.query(User).all()

def get_users_by_keys(db: Session, filters: dict) -> list[User]:
    query = db.query(User).join(Teacher)
    
    for key, value in filters.items():
        # Jika filter berdasarkan atribut Guru (misal cari nama/NIP)
        if hasattr(Teacher, key):
            column = getattr(Teacher, key)
            query = query.filter(column.ilike(f"%{value}%"))
        # Jika filter atribut User (role/status)
        elif hasattr(User, key):
            column = getattr(User, key)
            query = query.filter(column.ilike(f"%{value}%"))
        else:
            # Skip invalid filter agar tidak error
            continue
        
    return query.all()