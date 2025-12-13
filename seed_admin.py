from app.core.database import SessionLocal
from app.models.classification import Classification
from app.models.storage_location import StorageLocation
from app.models.teacher import Teacher
from app.models.user import User
from app.models.employee_archive import EmployeeArchive
from app.models.finance_archive import FinanceArchive
from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.diploma import Diploma
from app.models.log import Log
from app.utils.hash import get_password_hash

import datetime
import random


def seed():
    db = SessionLocal()
    try:
        print("=== MULAI SEEDING 10 DATA PER TABEL ===")

        # ------------------------------------------------------
        # 1. CLASSIFICATION (10 data)
        # ------------------------------------------------------
        class_list = []
        for i in range(1, 11):
            data = Classification(
                code=f"CL-{i:02d}",
                name=f"Klasifikasi {i}",
                description="Klasifikasi dummy",
                retention_active_period=1,
                retention_inactive_period=2,
                final_action="destroy"
            )
            db.add(data)
            class_list.append(data)

        # ------------------------------------------------------
        # 2. STORAGE LOCATION (10 data)
        # ------------------------------------------------------
        loc_list = []
        for i in range(1, 11):
            data = StorageLocation(
                name=f"Lemari-{i}",
                description=f"Lemari penyimpanan nomor {i}"
            )
            db.add(data)
            loc_list.append(data)

        # ------------------------------------------------------
        # 3. TEACHER (10 data)
        # ------------------------------------------------------
        teacher_list = []
        for i in range(1, 11):
            data = Teacher(
                identity_number=f"19880{i}001",
                full_name=f"Guru Contoh {i}",
                gender="L" if i % 2 else "P",
                employment_status="PNS" if i % 2 else "Honorer",
                rank="III/a",
                status="Aktif",
                address=f"Alamat Guru {i}",
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
            db.add(data)
            teacher_list.append(data)

        db.commit()
        db.refresh(class_list[0])
        db.refresh(loc_list[0])
        for t in teacher_list:
            db.refresh(t)

        # ------------------------------------------------------
        # 4. USER (10 data)
        # ------------------------------------------------------
        for i, t in enumerate(teacher_list):
            data = User(
                teacher_id=t.id,
                password=get_password_hash(f"password{i+1}"),
                role="admin" if i == 0 else "teacher",
                status="active",
            )
            db.add(data)

        # ------------------------------------------------------
        # 5. EMPLOYEE ARCHIVE (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = EmployeeArchive(
                document_name=f"Dokumen Pegawai {i}",
                document_type="ijazah",
                document_year=2010 + i,
                description="Arsip pegawai dummy",
                owner_id=random.choice(teacher_list).id,
                storage_location_id=random.choice(loc_list).id
            )
            db.add(data)

        # ------------------------------------------------------
        # 6. FINANCE ARCHIVE (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = FinanceArchive(
                title=f"Laporan Keuangan {i}",
                fiscal_year=2020 + (i % 5),
                period_month=(i % 12) + 1,
                category="bos_reguler",
                amount=1000000 * i,
                description="Laporan dummy",
                classification_id=random.choice(class_list).id,
                storage_location_id=random.choice(loc_list).id,
                archive_status="active",
            )
            db.add(data)

        # ------------------------------------------------------
        # 7. INCOMING LETTER (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = IncomingLetter(
                number=f"SM-{i:03d}/2024",
                letter_date=datetime.datetime.now(),
                received_date=datetime.datetime.now(),
                sender=f"Instansi {i}",
                subject=f"Surat Masuk {i}",
                classification_id=random.choice(class_list).id,
                storage_location_id=random.choice(loc_list).id,
                archive_status="active"
            )
            db.add(data)

        # ------------------------------------------------------
        # 8. OUTGOING LETTER (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = OutgoingLetter(
                number=f"SK-{i:03d}/2024",
                letter_date=datetime.datetime.now(),
                sent_date=datetime.datetime.now(),
                destination=f"Lembaga {i}",
                subject=f"Surat Keluar {i}",
                is_decree=False,
                classification_id=random.choice(class_list).id,
                storage_location_id=random.choice(loc_list).id,
                archive_status="active",
                approval_status="approved" if i % 2 else "pending",
            )
            db.add(data)

        # ------------------------------------------------------
        # 9. DIPLOMA (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = Diploma(
                number=f"IJZ-{i:04d}",
                student_name=f"Siswa {i}",
                major="IPA" if i % 2 else "IPS",
                academic_year="2023/2024",
                is_collected=False,
                storage_location_id=random.choice(loc_list).id
            )
            db.add(data)

        # ------------------------------------------------------
        # 10. LOG (10 data)
        # ------------------------------------------------------
        for i in range(1, 11):
            data = Log(
                user_id=1,  # admin pertama
                action=f"Melakukan aksi dummy {i}"
            )
            db.add(data)

        db.commit()
        print("=== SELESAI: Semua tabel terisi 10 data tanpa drama ===")

    except Exception as e:
        print("ERROR:", e)
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    seed()
