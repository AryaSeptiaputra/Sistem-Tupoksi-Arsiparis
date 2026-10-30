"""
Data awal untuk test end-to-end: referensi master, akun operator, dan data dasar.

Dijalankan oleh `e2e/conftest.py` sebagai subprocess, dengan cwd folder sementara
dan env DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY, E2E_USERNAME, E2E_PASSWORD.

Data surat dan arsip dimasukkan langsung lewat model, bukan lewat API, agar test
edit, filter, hapus, dan dashboard tidak bergantung pada fitur tambah yang juga diuji.
Nomor berawalan "E2E/" dipakai test sebagai penanda baris.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.models.classification import Classification
from app.models.diploma import Diploma
from app.models.employee_archive import EmployeeArchive
from app.models.finance_archive import FinanceArchive
from app.models.incoming_letter import IncomingLetter
from app.models.master_reference import MasterReference
from app.models.outgoing_letter import OutgoingLetter
from app.models.storage_location import StorageLocation
from app.models.teacher import Teacher
from app.services.user import create_user
from database.seeders.seed_master import seed_master_references

# Data guru menyimpan kode referensi, sama seperti nilai dropdown halaman Guru
TEACHERS = [
    {"identity_number": "198001012005011001", "full_name": "Budi Santoso", "gender": "L",
     "employment_status": "PNS", "rank": "III/a", "status": "aktif"},
    {"identity_number": "199002022019022002", "full_name": "Sari Wulandari", "gender": "P",
     "employment_status": "GTT", "rank": "", "status": "aktif"},
]

# Lampiran surat lama; path relatif terhadap cwd server, sama dengan hasil handle_file_upload
EXPIRED_ATTACHMENT = "storage/documents/incoming_letters/e2e_surat_lama.pdf"

# (nomor, tanggal surat, pengirim, perihal, kode klasifikasi)
INCOMING_LETTERS = [
    ("E2E/MASUK/001", datetime(2026, 9, 1), "Kantor Cabang Dinas", "Edaran jadwal ujian", "421"),
    ("E2E/MASUK/002", datetime(2026, 10, 5), "Universitas Padjadjaran", "Permohonan izin penelitian", "000"),
    ("E2E/MASUK/EDIT", datetime(2026, 8, 1), "Komite Sekolah", "Undangan rapat komite", "421"),
    ("E2E/MASUK/HAPUS", datetime(2026, 7, 1), "Dinas Kesehatan", "Sosialisasi kesehatan", "421"),
]
# (nomor, tujuan, perihal, status persetujuan, surat keputusan)
OUTGOING_LETTERS = [
    ("E2E/KELUAR/001", "Dinas Pendidikan", "Laporan bulanan", "pending", False),
    ("E2E/KELUAR/002", "Kepala Sekolah", "SK pembagian tugas", "approved", True),
    ("E2E/KELUAR/003", "Yayasan Pendidikan", "Permohonan dana", "rejected", False),
    ("E2E/KELUAR/EDIT", "Orang Tua Siswa", "Pemberitahuan libur", "pending", False),
    ("E2E/KELUAR/HAPUS", "Ikatan Alumni", "Undangan reuni", "draft", False),
]


def _save_expired_attachment() -> None:
    os.makedirs(os.path.dirname(EXPIRED_ATTACHMENT), exist_ok=True)
    with open(EXPIRED_ATTACHMENT, "wb") as f:
        f.write(b"%PDF-1.4\n%%EOF\n")


def _seed_letters(db: Session, classes: dict[str, int], location_id: int) -> None:
    for number, letter_date, sender, subject, code in INCOMING_LETTERS:
        db.add(IncomingLetter(number=number, letter_date=letter_date, received_date=letter_date,
                              sender=sender, subject=subject, classification_id=classes[code],
                              storage_location_id=location_id, archive_status="active"))
    for number, destination, subject, approval, is_decree in OUTGOING_LETTERS:
        db.add(OutgoingLetter(number=number, letter_date=datetime(2026, 10, 1), sent_date=datetime(2026, 10, 2),
                              destination=destination, subject=subject, approval_status=approval,
                              is_decree=is_decree, archive_status="active", classification_id=classes["421"],
                              storage_location_id=location_id))


def _seed_archives(db: Session, class_id: int, owner_id: int) -> None:
    db.add_all([
        FinanceArchive(title="Laporan BOS Triwulan 3", fiscal_year=2026, period_month=9, category="BOS_REG",
                       amount=1500000, classification_id=class_id, archive_status="active"),
        FinanceArchive(title="Iuran Komite 2025", fiscal_year=2025, period_month=3, category="SPP",
                       amount=750000, classification_id=class_id, archive_status="active"),
        Diploma(number="DN-E2E-001", student_name="Andi Pratama", major="Kimia Industri",
                academic_year="2025/2026", is_collected=True, collected_at=datetime(2026, 7, 1)),
        Diploma(number="DN-E2E-002", student_name="Rina Lestari", major="Farmasi",
                academic_year="2025/2026", is_collected=False),
        EmployeeArchive(document_name="SK Pangkat Budi", document_type="SK_PANGKAT", archive_status="active",
                        document_year=2026, owner_id=owner_id, classification_id=class_id),
    ])


def _seed_base_data(db: Session) -> None:
    destroy = Classification(code="000", name="Umum", retention_active_period=1,
                             retention_inactive_period=1, final_action="destroy")
    permanent = Classification(code="421", name="Sekolah", retention_active_period=2,
                               retention_inactive_period=5, final_action="permanent")
    location = StorageLocation(name="Lemari A - Rak 1", description="Lemari uji")
    teachers = [Teacher(**t) for t in TEACHERS]
    db.add_all([destroy, permanent, location, *teachers])
    db.flush()
    _seed_letters(db, {"000": destroy.id, "421": permanent.id}, location.id)
    _seed_archives(db, permanent.id, teachers[0].id)

    _save_expired_attachment()
    # Tahun surat 2015 + retensi 1 + 1 tahun sudah lewat, jadi muncul di halaman Penyusutan
    db.add(IncomingLetter(number="E2E/2015/001", letter_date=datetime(2015, 1, 10),
                          received_date=datetime(2015, 1, 12), sender="Dinas Pendidikan",
                          subject="Surat lama untuk uji penyusutan", classification_id=destroy.id,
                          storage_location_id=location.id, archive_status="inactive",
                          attachment_path=EXPIRED_ATTACHMENT))
    db.commit()


def main() -> int:
    """Mengisi database uji yang masih kosong.

    Returns:
        Kode keluar proses: 0 berhasil.

    Raises:
        RuntimeError: Kalau referensi master gagal diisi.
    """
    Base.metadata.create_all(bind=engine)
    seed_master_references()

    db = SessionLocal()
    try:
        if db.query(MasterReference).count() == 0:
            raise RuntimeError("Referensi master gagal diisi; lihat keluaran seed_master_references.")
        create_user(db, os.environ["E2E_USERNAME"], "Operator Uji", os.environ["E2E_PASSWORD"])
        _seed_base_data(db)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
