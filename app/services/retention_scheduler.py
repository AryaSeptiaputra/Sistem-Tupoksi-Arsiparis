from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.classification import Classification
from app.core.database import engine # Import engine untuk buat session baru
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Setup Session Factory
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_and_deactivate_archives() -> None:
    """
    Fungsi ini akan dipanggil oleh Scheduler.
    Membuka koneksi DB sendiri, cek retensi, update, lalu tutup koneksi.
    """
    db: Session = SessionLocal()
    try:
        logger.info("Memulai pengecekan retensi otomatis")
        counter = 0
        today = datetime.now()
        
        # --- 1. SURAT MASUK ---
        incoming_docs = db.query(IncomingLetter).join(Classification)\
            .filter(IncomingLetter.archive_status == 'active').all()
        
        for doc in incoming_docs:
            limit = doc.received_date + relativedelta(years=doc.classification.retention_active_period)
            if today > limit:
                doc.archive_status = 'inactive'
                counter += 1

        # --- 2. SURAT KELUAR ---
        outgoing_docs = db.query(OutgoingLetter).join(Classification)\
            .filter(OutgoingLetter.archive_status == 'active').all()
        
        for doc in outgoing_docs:
            limit = doc.sent_date + relativedelta(years=doc.classification.retention_active_period)
            if today > limit:
                doc.archive_status = 'inactive'
                counter += 1

        # --- 3. ARSIP KEUANGAN ---
        finance_docs = db.query(FinanceArchive).join(Classification)\
            .filter(FinanceArchive.archive_status == 'active').all()
        
        for doc in finance_docs:
            # Logic: Jika tahun sekarang > (Tahun Anggaran + Retensi)
            expiry_year = doc.fiscal_year + doc.classification.retention_active_period
            if today.year > expiry_year:
                doc.archive_status = 'inactive'
                counter += 1

        if counter > 0:
            db.commit()
            logger.info(f"{counter} dokumen diubah menjadi inaktif")
        else:
            logger.info("Tidak ada dokumen yang kedaluwarsa hari ini")

    except Exception as e:
        logger.error(f"Scheduler retensi gagal: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

# ... (kode sebelumnya)

# Tambahkan blok ini di paling bawah file:
if __name__ == "__main__":
    print("--- Menjalankan Scheduler Manual ---")
    check_and_deactivate_archives()
    print("--- Selesai ---")