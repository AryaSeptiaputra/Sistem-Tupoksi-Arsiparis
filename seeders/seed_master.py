from app.core.database import SessionLocal
from app.models.master_reference import MasterReference
import datetime

def seed_master_references():
    db = SessionLocal()
    try:
        print("=== MULAI SEEDING MASTER REFERENCE SMK ===")

        references = [
            # 1. SCHOOL MAJOR (Jurusan SMK)
            {"category": "school_major", "code": "KI", "name": "Kimia Industri", "sort_order": 1},
            {"category": "school_major", "code": "TPT", "name": "Teknik Penyempurnaan Tekstil", "sort_order": 2},
            {"category": "school_major", "code": "AK", "name": "Analisis Kimia", "sort_order": 3},
            {"category": "school_major", "code": "FM", "name": "Farmasi", "sort_order": 4},

            # 2. TEACHER EMPLOYMENT STATUS
            {"category": "teacher_emp_status", "code": "PNS", "name": "Pegawai Negeri Sipil", "sort_order": 1},
            {"category": "teacher_emp_status", "code": "PPPK", "name": "Pegawai Pemerintah dengan Perjanjian Kerja", "sort_order": 2},
            {"category": "teacher_emp_status", "code": "GTT", "name": "Guru Tidak Tetap", "sort_order": 3},
            {"category": "teacher_emp_status", "code": "GTY", "name": "Guru Tetap Yayasan", "sort_order": 4},

            # 3. TEACHER RANK (Pangkat/Golongan)
            {"category": "teacher_rank", "code": "III/a", "name": "Penata Muda", "sort_order": 1},
            {"category": "teacher_rank", "code": "III/b", "name": "Penata Muda Tingkat I", "sort_order": 2},
            {"category": "teacher_rank", "code": "III/c", "name": "Penata", "sort_order": 3},
            {"category": "teacher_rank", "code": "III/d", "name": "Penata Tingkat I", "sort_order": 4},
            {"category": "teacher_rank", "code": "IV/a", "name": "Pembina", "sort_order": 5},

            # 4. TEACHER ACTIVE STATUS
            {"category": "teacher_active_status", "code": "aktif", "name": "Aktif", "sort_order": 1},
            {"category": "teacher_active_status", "code": "cuti", "name": "Cuti", "sort_order": 2},
            {"category": "teacher_active_status", "code": "pensiun", "name": "Pensiun/Keluar", "sort_order": 3},

            # 5. FINAL ACTION (JRA Arsip)
            {"category": "final_action", "code": "destroy", "name": "Musnah", "sort_order": 1},
            {"category": "final_action", "code": "permanent", "name": "Permanen / Statis", "sort_order": 2},
            {"category": "final_action", "code": "assess", "name": "Dinilai Kembali", "sort_order": 3},

            # 6. ARCHIVE STATUS
            {"category": "archive_status", "code": "active", "name": "Aktif", "sort_order": 1},
            {"category": "archive_status", "code": "inactive", "name": "Inaktif", "sort_order": 2},
            {"category": "archive_status", "code": "destroyed", "name": "Terhapus/Musnah", "sort_order": 3},

            # 7. [TAMBAHAN] FINANCE CATEGORY (Jenis Keuangan)
            {"category": "finance_category", "code": "BOS_REG", "name": "BOS Reguler", "sort_order": 1},
            {"category": "finance_category", "code": "BOS_DA", "name": "BOS Daerah / BOPD", "sort_order": 2},
            {"category": "finance_category", "code": "SPP", "name": "Komite / SPP Siswa", "sort_order": 3},
            {"category": "finance_category", "code": "H_L", "name": "Hibah / Lain-lain", "sort_order": 4},

            # 8. [TAMBAHAN] EMP DOC TYPE (Jenis Dokumen Pegawai)
            {"category": "emp_doc_type", "code": "SK_CPNS", "name": "SK CPNS/PPPK", "sort_order": 1},
            {"category": "emp_doc_type", "code": "SK_PANGKAT", "name": "SK Pangkat/Golongan", "sort_order": 2},
            {"category": "emp_doc_type", "code": "SK_BERKALA", "name": "SK Kenaikan Gaji Berkala", "sort_order": 3},
            {"category": "emp_doc_type", "code": "IJAZAH", "name": "Ijazah & Sertifikat Pendidik", "sort_order": 4},
            {"category": "emp_doc_type", "code": "PAK", "name": "Penilaian Angka Kredit (PAK)", "sort_order": 5},

            # 9. [TAMBAHAN] LETTER APPROVAL STATUS (Status Persetujuan Surat)
            {"category": "letter_approval_status", "code": "draft", "name": "Konsep / Draft", "sort_order": 1},
            {"category": "letter_approval_status", "code": "pending", "name": "Menunggu Persetujuan", "sort_order": 2},
            {"category": "letter_approval_status", "code": "approved", "name": "Disetujui / TTD", "sort_order": 3},
            {"category": "letter_approval_status", "code": "rejected", "name": "Ditolak / Revisi", "sort_order": 4},
        ]

        for ref_data in references:
            exists = db.query(MasterReference).filter_by(
                category=ref_data["category"], 
                code=ref_data["code"]
            ).first()

            if not exists:
                new_ref = MasterReference(
                    category=ref_data["category"],
                    code=ref_data["code"],
                    name=ref_data["name"],
                    sort_order=ref_data["sort_order"],
                    is_active=True
                )
                db.add(new_ref)

        db.commit()
        print(f"=== SELESAI: Berhasil menambahkan {len(references)} data master reference ===")

    except Exception as e:
        print("ERROR SEEDING MASTER:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_references()