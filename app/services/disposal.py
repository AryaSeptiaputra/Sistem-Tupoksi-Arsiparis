from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from datetime import datetime

from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.employee_archive import EmployeeArchive 
from app.models.diploma import Diploma
from app.models.classification import Classification
from app.utils.file_helper import delete_physical_file

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
    expired_items = []

    incoming = db.query(IncomingLetter).join(Classification).filter(
        IncomingLetter.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    for item in incoming:
        doc_year = item.letter_date.year
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            expired_items.append({
                "type": "Surat Masuk",
                "id": item.id,
                "number": item.number,
                "title": item.subject or "(Tanpa Perihal)", 
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "incoming_letter"
            })

    outgoing = db.query(OutgoingLetter).join(Classification).filter(
        OutgoingLetter.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    for item in outgoing:
        doc_year = item.letter_date.year
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            expired_items.append({
                "type": "Surat Keluar",
                "id": item.id,
                "number": item.number,
                "title": item.subject or "(Tanpa Perihal)",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "outgoing_letter"
            })

    finance = db.query(FinanceArchive).join(Classification).filter(
        FinanceArchive.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    for item in finance:
        doc_year = item.fiscal_year 
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            display_title = item.title
            if item.amount: display_title += f" (Rp {item.amount:,})"
            expired_items.append({
                "type": "Arsip Keuangan",
                "id": item.id,
                "number": "-", 
                "title": display_title,
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "finance_archive"
            })

    employees = db.query(EmployeeArchive).join(Classification).filter(
        EmployeeArchive.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    for item in employees:
        # Tahun dokumen kosong diganti tahun data dibuat
        doc_year = item.document_year or item.created_at.year

        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention
        
        if current_year > expiry_year:
             expired_items.append({
                "type": "Arsip Pegawai",
                "id": item.id,
                "number": "-",
                "title": f"{item.document_name} ({item.document_type})",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "employee_archive"
            })
            
    # Ijazah tidak punya klasifikasi; salinan yang sudah diambil dimusnahkan setelah 5 tahun
    diplomas = db.query(Diploma).filter(Diploma.is_collected == True).all()
    
    for item in diplomas:
        # Contoh academic_year: "2020/2021" -> 2020
        try: doc_year = int(item.academic_year.split('/')[0])
        except (ValueError, AttributeError): doc_year = current_year
        
        expiry_year = doc_year + 5

        if current_year > expiry_year:
             expired_items.append({
                "type": "Data Ijazah",
                "id": item.id,
                "number": item.number,
                "title": f"Ijazah: {item.student_name}",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": "-",
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "diploma"
            })

    return expired_items

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
        source = item.get('table_source')
        record_id = item.get('id')
        record = None
        
        if source == 'incoming_letter':
            record = db.query(IncomingLetter).filter(IncomingLetter.id == record_id).first()
        elif source == 'outgoing_letter':
            record = db.query(OutgoingLetter).filter(OutgoingLetter.id == record_id).first()
        elif source == 'finance_archive':
            record = db.query(FinanceArchive).filter(FinanceArchive.id == record_id).first()
        elif source == 'employee_archive': 
            record = db.query(EmployeeArchive).filter(EmployeeArchive.id == record_id).first()
        elif source == 'diploma':
            record = db.query(Diploma).filter(Diploma.id == record_id).first()
            
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