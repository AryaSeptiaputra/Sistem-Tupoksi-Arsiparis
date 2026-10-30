"""
Ubah status kepegawaian, status keaktifan, dan pangkat guru dari nama
referensi menjadi kodenya (issue #27).

Dulu form Guru menyimpan nama referensi ("Pegawai Negeri Sipil", "Aktif",
"Penata Muda"). Sekarang form menyimpan kodenya ("PNS", "aktif", "III/a"),
sehingga data lama perlu diubah sekali.

Pemakaian (dari folder project, virtual environment aktif, setelah backup
database). Database yang dipakai sama dengan aplikasi (DATABASE_URL):
    python scripts/migrate_teacher_codes.py --dry-run
    python scripts/migrate_teacher_codes.py

Aman dijalankan ulang: nilai yang sudah berupa kode dibiarkan, dan nilai yang
tidak dikenal hanya dilaporkan.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.master_reference import MasterReference
from app.models.teacher import Teacher

# Kolom guru dan kategori referensi asal kodenya
FIELD_CATEGORIES = {
    "employment_status": "teacher_emp_status",
    "status": "teacher_active_status",
    "rank": "teacher_rank",
}


def find_code(value: str | None, references: dict[str, str]) -> str | None:
    """Mencari kode referensi untuk nilai yang tersimpan.

    Args:
        value: Nilai tersimpan, berupa nama atau kode referensi.
        references: Pasangan kode -> nama untuk satu kategori referensi.

    Returns:
        Kode yang cocok dengan nama atau kodenya (tanpa membedakan huruf
        besar-kecil), atau None bila tidak dikenal.
    """
    if not value:
        return None
    wanted = value.strip().lower()
    return next((code for code, name in references.items() if wanted in (code.lower(), name.lower())), None)


def _load_references(db: Session) -> dict[str, dict[str, str]]:
    references = {category: {} for category in FIELD_CATEGORIES.values()}
    for ref in db.query(MasterReference).filter(MasterReference.category.in_(list(references))):
        references[ref.category][ref.code] = ref.name
    return references


def _convert_teacher(teacher: Teacher, references: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    changes, unknown = [], []
    for field, category in FIELD_CATEGORIES.items():
        value = getattr(teacher, field)
        if not value:
            continue
        code = find_code(value, references[category])
        if code is None:
            unknown.append(f"{field}={value!r}")
        elif code != value:
            changes.append(f"{field}: {value!r} -> {code!r}")
            setattr(teacher, field, code)
    return changes, unknown


def migrate(db: Session, dry_run: bool) -> tuple[int, int]:
    """Mengubah nilai referensi semua guru menjadi kode.

    Args:
        db: Session database.
        dry_run: True untuk hanya menampilkan perubahan tanpa menyimpannya.

    Returns:
        Jumlah guru yang diubah dan jumlah guru yang punya nilai tidak dikenal.
    """
    references = _load_references(db)
    changed = with_unknown = 0
    for teacher in db.query(Teacher).order_by(Teacher.id):
        changes, unknown = _convert_teacher(teacher, references)
        if changes:
            changed += 1
            print(f"[{teacher.identity_number}] {teacher.full_name}: " + "; ".join(changes))
        if unknown:
            with_unknown += 1
            print(f"[{teacher.identity_number}] {teacher.full_name}: tidak dikenal, dibiarkan: " + ", ".join(unknown))
    if dry_run:
        db.rollback()
    else:
        db.commit()
    return changed, with_unknown


def main() -> int:
    """Menjalankan migrasi dari terminal.

    Returns:
        Kode keluar proses: 0 berhasil.
    """
    parser = argparse.ArgumentParser(description="Ubah nilai referensi data guru menjadi kode.")
    parser.add_argument("--dry-run", action="store_true", help="Tampilkan perubahan tanpa menyimpan")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        changed, with_unknown = migrate(db, args.dry_run)
    finally:
        db.close()

    mode = "akan diubah (dry-run)" if args.dry_run else "diubah"
    print(f"Selesai: {changed} guru {mode}, {with_unknown} guru punya nilai tidak dikenal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
