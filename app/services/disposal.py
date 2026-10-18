"""Pencarian dan pemusnahan arsip yang melewati masa retensi.

Baris arsip berasal dari beberapa model berbeda (surat, arsip keuangan, arsip
pegawai, ijazah), jadi diberi tipe `Any` pada fungsi yang memprosesnya bersama.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.employee_archive import EmployeeArchive
from app.models.diploma import Diploma
from app.models.classification import Classification
from app.utils.file_helper import delete_physical_file

SOURCE_MODELS = {
    'incoming_letter': IncomingLetter,
    'outgoing_letter': OutgoingLetter,
    'finance_archive': FinanceArchive,
    'employee_archive': EmployeeArchive,
    'diploma': Diploma,
}

# Salinan ijazah yang sudah diambil dimusnahkan setelah 5 tahun
DIPLOMA_RETENTION_YEARS = 5

def _to_expired_item(label: str, table_source: str, item: Any, number: str,
                     title: str, doc_year: int, expiry_year: int, classification: str) -> dict[str, Any]:
    return {
        "type": label,
        "id": item.id,
        "number": number,
        "title": title,
        "doc_year": doc_year,
        "expiry_year": expiry_year,
        "classification": classification,
        "location": item.storage_location.name if item.storage_location else "-",
        "table_source": table_source
    }

def _scan_classified(db: Session, model: Any, label: str, table_source: str, current_year: int,
                     doc_year_of: Callable[[Any], int], number_of: Callable[[Any], str],
                     title_of: Callable[[Any], str]) -> list[dict[str, Any]]:
    rows = db.query(model).join(Classification).filter(
        model.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    expired = []
    for item in rows:
        doc_year = doc_year_of(item)
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention
        if current_year > expiry_year:
            expired.append(_to_expired_item(label, table_source, item, number_of(item), title_of(item),
                                            doc_year, expiry_year, item.classification.code))
    return expired

def _format_finance_title(item: FinanceArchive) -> str:
    if item.amount:
        # Contoh: "Dana BOS (Rp 1,500,000)"
        return f"{item.title} (Rp {item.amount:,})"
    return item.title

def _scan_diplomas(db: Session, current_year: int) -> list[dict[str, Any]]:
    diplomas = db.query(Diploma).filter(Diploma.is_collected == True).all()

    expired = []
    for item in diplomas:
        # Contoh academic_year: "2020/2021" -> 2020
        try: doc_year = int(item.academic_year.split('/')[0])
        except (ValueError, AttributeError): doc_year = current_year

        expiry_year = doc_year + DIPLOMA_RETENTION_YEARS
        if current_year > expiry_year:
            expired.append(_to_expired_item("Data Ijazah", "diploma", item, item.number,
                                            f"Ijazah: {item.student_name}", doc_year, expiry_year, "-"))
    return expired

def get_expired_archives(db: Session) -> list[dict[str, Any]]:
    """Mencari arsip yang sudah melewati masa retensi dan boleh dimusnahkan.

    Arsip dianggap kedaluwarsa bila tahun sekarang melewati tahun dokumen
    ditambah masa aktif dan inaktif klasifikasinya, dan tindakan akhirnya
    `destroy`. Ijazah yang sudah diambil memakai batas tetap 5 tahun.

    Args:
        db: Session database.

    Returns:
        Ringkasan arsip kedaluwarsa, masing-masing dengan `table_source` dan `id`.
    """
    current_year = datetime.now().year
    letter_title = lambda item: item.subject or "(Tanpa Perihal)"

    return [
        *_scan_classified(db, IncomingLetter, "Surat Masuk", "incoming_letter", current_year,
                          lambda item: item.letter_date.year, lambda item: item.number, letter_title),
        *_scan_classified(db, OutgoingLetter, "Surat Keluar", "outgoing_letter", current_year,
                          lambda item: item.letter_date.year, lambda item: item.number, letter_title),
        *_scan_classified(db, FinanceArchive, "Arsip Keuangan", "finance_archive", current_year,
                          lambda item: item.fiscal_year, lambda item: "-", _format_finance_title),
        # Tahun dokumen pegawai yang kosong diganti tahun data dibuat
        *_scan_classified(db, EmployeeArchive, "Arsip Pegawai", "employee_archive", current_year,
                          lambda item: item.document_year or item.created_at.year, lambda item: "-",
                          lambda item: f"{item.document_name} ({item.document_type})"),
        *_scan_diplomas(db, current_year),
    ]

def execute_disposal(db: Session, items_to_destroy: list[dict[str, Any]], user_id: int | None) -> int:
    """Memusnahkan arsip: menghapus file lampiran dan menandai statusnya `destroyed`.

    Args:
        db: Session database.
        items_to_destroy: Arsip pilihan, masing-masing berisi `table_source` dan `id`.
        user_id: Akun yang menjalankan pemusnahan.

    Returns:
        Jumlah arsip yang ditemukan dan dimusnahkan.
    """
    count = 0
    for item in items_to_destroy:
        model = SOURCE_MODELS.get(item.get('table_source'))
        record = db.query(model).filter(model.id == item.get('id')).first() if model else None

        if record:
            if hasattr(record, 'attachment_path') and record.attachment_path:
                delete_physical_file(record.attachment_path)
                record.attachment_path = None

            # Model tanpa archive_status ditandai lewat keterangannya
            if hasattr(record, 'archive_status'):
                record.archive_status = 'destroyed'
            else:
                if hasattr(record, 'description'):
                     record.description = (record.description or "") + " [MUSNAH]"

            count += 1

    db.commit()
    return count
