from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.user import User
from app.utils.hash import get_password_hash
import datetime


def seed():
    db = SessionLocal()
    try:
        print("=== MULAI SEEDING 1 GURU & 1 USER ===")

        # ------------------------------------------------------
        # 1. TEACHER (1 data)
        # ------------------------------------------------------
        teacher = Teacher(
            identity_number="19880101001",
            full_name="Guru Admin",
            gender="L",
            employment_status="PNS",
            rank="III/a",
            status="Aktif",
            address="Alamat Guru Admin",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        # ------------------------------------------------------
        # 2. USER (1 data)
        # ------------------------------------------------------
        user = User(
            teacher_id=teacher.id,
            password=get_password_hash("admin123"),
            role="admin",
            status="active",
        )
        db.add(user)
        db.commit()

        print("=== SELESAI: 1 guru & 1 user berhasil dibuat ===")

    except Exception as e:
        print("ERROR:", e)
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    seed()