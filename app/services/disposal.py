from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from datetime import datetime

# [PERBAIKAN 1] Import SEMUA model arsip
from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.employee_archive import EmployeeArchive # Baru
from app.models.diploma import Diploma # Baru
from app.models.classification import Classification

def get_expired_archives(db: Session):
    """
    Memindai semua tabel arsip untuk mencari dokumen yang masa retensinya habis.
    Rumus: (Tahun Dokumen + Retensi Aktif + Retensi Inaktif) < Tahun Sekarang
    """
    current_year = datetime.now().year
    expired_items = []

    # --- 1. SCAN SURAT MASUK ---
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
                # [PERBAIKAN] Pastikan selalu ada nilai (fallback ke '-')
                "title": item.subject or "(Tanpa Perihal)", 
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
                "title": item.subject or "(Tanpa Perihal)",
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
        doc_year = item.fiscal_year 
        total_retention = item.classification.retention_active_period + item.classification.retention_inactive_period
        expiry_year = doc_year + total_retention

        if current_year > expiry_year:
            display_title = item.title
            if item.amount:
                display_title += f" (Rp {item.amount:,})"

            expired_items.append({
                "type": "Arsip Keuangan",
                "id": item.id,
                "number": "-", 
                "title": display_title, # Sudah sesuai
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": item.classification.code,
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "finance_archive"
            })

    # --- 4. [BARU] SCAN ARSIP PEGAWAI ---
    # Arsip pegawai tidak punya relasi 'Classification' langsung di model Anda (berdasarkan file employee_archive.py sebelumnya),
    # Tapi biasanya arsip pegawai dimusnahkan berdasarkan umur dokumen.
    # Disini kita asumsikan dokumen > 10 tahun dimusnahkan (atau sesuaikan logika Anda).
    # KARENA MODEL TIDAK ADA RELASI CLASSIFICATION, KITA SKIP RETENSI DARI DB
    # KITA PAKAI LOGIKA MANUAL: Jika document_year + 10 tahun < tahun sekarang
    
    employees = db.query(EmployeeArchive).filter(
        # Asumsi: Jika logic penghapusan pegawai belum ada statusnya, kita filter manual atau tambahkan kolom status nanti.
        # Di sini kita scan semua yg belum dihapus (jika field status ada, pakai itu)
        EmployeeArchive.document_year != None
    ).all()

    for item in employees:
        doc_year = item.document_year
        # [HARDCODE RULE] Contoh: Arsip pegawai dimusnahkan setelah 10 tahun
        # Anda bisa sesuaikan angka ini
        expiry_year = doc_year + 10 
        
        if current_year > expiry_year:
             expired_items.append({
                "type": "Arsip Pegawai",
                "id": item.id,
                "number": "-",
                # Mapping document_name ke title
                "title": f"{item.document_name} ({item.document_type})",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": "-", # Tidak ada relasi klasifikasi
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "employee_archive"
            })
            
    # --- 5. [BARU] SCAN IJAZAH ---
    # Ijazah biasanya TIDAK dimusnahkan (Permanen), tapi jika ada aturan khusus:
    diplomas = db.query(Diploma).filter(
        Diploma.is_collected == True # Contoh: Hanya yg sudah diambil yg boleh dimusnahkan? (Sesuaikan aturan)
    ).all()
    
    for item in diplomas:
        # Parsing tahun ajaran '2020/2021' ambil angka depan
        try:
            doc_year = int(item.academic_year.split('/')[0])
        except:
            doc_year = current_year # Fallback jika format salah

        # [HARDCODE RULE] Contoh: Ijazah copy/legalisir dimusnahkan setelah 5 tahun
        expiry_year = doc_year + 5

        if current_year > expiry_year:
             expired_items.append({
                "type": "Data Ijazah",
                "id": item.id,
                "number": item.number,
                # Mapping student_name ke title
                "title": f"Ijazah: {item.student_name} ({item.major})",
                "doc_year": doc_year,
                "expiry_year": expiry_year,
                "classification": "-",
                "location": item.storage_location.name if item.storage_location else "-",
                "table_source": "diploma"
            })

    return expired_items

def execute_disposal(db: Session, items_to_destroy: list, user_id: int):
    """
    Eksekusi pemusnahan massal untuk semua jenis arsip.
    """
    from app.utils.file_helper import delete_physical_file
    
    count = 0
    for item in items_to_destroy:
        source = item.get('table_source')
        record_id = item.get('id')
        
        record = None
        
        # Mapping Source ke Model
        if source == 'incoming_letter':
            record = db.query(IncomingLetter).filter(IncomingLetter.id == record_id).first()
        elif source == 'outgoing_letter':
            record = db.query(OutgoingLetter).filter(OutgoingLetter.id == record_id).first()
        elif source == 'finance_archive':
            record = db.query(FinanceArchive).filter(FinanceArchive.id == record_id).first()
        elif source == 'employee_archive': # [BARU]
            record = db.query(EmployeeArchive).filter(EmployeeArchive.id == record_id).first()
        elif source == 'diploma': # [BARU]
            record = db.query(Diploma).filter(Diploma.id == record_id).first()
            
        if record:
            # 1. Hapus File Fisik
            if hasattr(record, 'attachment_path') and record.attachment_path:
                delete_physical_file(record.attachment_path)
                record.attachment_path = None
            
            # 2. Update Status (Jika model mendukung status)
            if hasattr(record, 'archive_status'):
                record.archive_status = 'destroyed'
            else:
                # Jika tabel (misal employee/diploma) tidak punya kolom archive_status,
                # Opsinya adalah menghapus record permanen dari DB:
                # db.delete(record)
                # TAPI, lebih aman update deskripsi jika tidak ada kolom status
                if hasattr(record, 'description'):
                     record.description = (record.description or "") + " [MUSNAH]"
            
            count += 1
            
    db.commit()
    return count