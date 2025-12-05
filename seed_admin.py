from app.core.database import SessionLocal
from app.models.user import User
from app.utils.hash import get_password_hash
import datetime

def seed_admin():
    db = SessionLocal()
    
    # --- KONFIGURASI ADMIN PERTAMA ---
    admin_nuptk = "112022190"
    admin_password = "aes040904"
    admin_username = "AryaSeptiaputra"
    
    try:
        # 1. Cek apakah user sudah ada
        existing_user = db.query(User).filter(User.nuptk == admin_nuptk).first()
        
        if existing_user:
            print(f"User dengan NUPTK {admin_nuptk} sudah ada. Tidak perlu dibuat ulang.")
            return

        # 2. Buat object User baru
        # Ingat: Password harus di-hash dulu!
        hashed_password = get_password_hash(admin_password)
        
        new_admin = User(
            nuptk=admin_nuptk,
            username=admin_username,
            password=hashed_password,
            role='admin',   # Pastikan sesuai dengan Enum di model ('admin'/'headmaster'/'teacher')
            status='active', # Pastikan sesuai dengan Enum ('active'/'inactive')
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )

        # 3. Simpan ke Database
        db.add(new_admin)
        db.commit()
        
        print("---------------------------------------------------------")
        print("SUKSES! Admin pertama berhasil dibuat.")
        print(f"NUPTK    : {admin_nuptk}")
        print(f"Password : {admin_password}")
        print("---------------------------------------------------------")
        print("Sekarang Anda bisa menjalankan 'test_api.py' menggunakan akun ini.")

    except Exception as e:
        print(f"Terjadi Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()