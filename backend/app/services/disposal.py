from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from datetime import datetime

# Import semua model yang punya retensi
from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.classification import Classification

def get_expired_archives(db: Session):
    """
    Memindai semua tabel arsip untuk mencari dokumen yang masa retensinya habis.
    Rumus: (Tahun Dokumen + Retensi Aktif + Retensi Inaktif) < Tahun Sekarang
    """
    current_year = datetime.now().year
    expired_items = []

    # --- 1. SCAN SURAT MASUK ---
    # Join dengan Classification untuk ambil data retensi
    incoming = db.query(IncomingLetter).join(Classification).filter(
        IncomingLetter.archive_status != 'destroyed', # Jangan ambil yang sudah musnah
        Classification.final_action == 'destroy'      # Hanya yang nasib akhirnya 'Musnah'
    ).all()

    for item in incoming:
        # Hitung tahun kadaluwarsa
        # Asumsi retensi dihitung dari tahun surat
        doc_year = item.letter_date.year
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            expired_items.append({
                "type": "Surat Masuk",
                "id": item.id,
                "number": item.number,
                "title": item.subject,
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "incoming_letter"
            })

    # --- 2. SCAN SURAT KELUAR ---
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
                "title": item.subject, # Asumsi ada kolom subject/perihal
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "outgoing_letter"
            })

    # --- 3. SCAN ARSIP KEUANGAN ---
    finance = db.query(FinanceArchive).join(Classification).filter(
        FinanceArchive.archive_status != 'destroyed',
        Classification.final_action == 'destroy'
    ).all()

    for item in finance:
        doc_year = item.fiscal_year # Keuangan pakai Tahun Anggaran
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            expired_items.append({
                "type": "Arsip Keuangan",
                "id": item.id,
                "number": "-", # Keuangan mungkin tidak punya no surat
                "title": f"{item.title} (Rp {item.amount})",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "finance_archive"
            })

    return expired_items

def execute_disposal(db: Session, items_to_destroy: list, user_id: int):
    """
    Eksekusi pemusnahan massal:
    1. Update status jadi 'destroyed'
    2. Hapus file fisik (scan)
    3. Catat log
    """
    from app.utils.file_helper import delete_physical_file
    
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
            
        if record:
            # 1. Hapus File Fisik
            if record.attachment_path:
                delete_physical_file(record.attachment_path)
                record.attachment_path = None # Kosongkan path
            
            # 2. Update Status
            record.archive_status = 'destroyed'
            
            # 3. Update Timestamp (Opsional, jika ada kolom deleted_at atau disposal_date)
            # record.updated_at = datetime.now()
            
            count += 1
            
    db.commit()
    return count