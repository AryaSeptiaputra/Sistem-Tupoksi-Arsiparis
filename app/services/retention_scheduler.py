from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from app.models.incoming_letter import IncomingLetter
from app.models.outgoing_letter import OutgoingLetter
from app.models.finance_archive import FinanceArchive
from app.models.classification import Classification
from app.core.database import engine
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_and_deactivate_archives() -> None:
    """Mengubah arsip aktif yang melewati masa aktif menjadi inaktif.

    Dijalankan scheduler harian dengan session sendiri. Batasnya tanggal
    terima (surat masuk), tanggal kirim (surat keluar), atau tahun anggaran
    (arsip keuangan) ditambah masa aktif klasifikasi. Error dicatat ke log
    tanpa dilempar, supaya scheduler tetap berjalan.
    """
    db: Session = SessionLocal()
    try:
        logger.info("Memulai pengecekan retensi otomatis")
        counter = 0
        today = datetime.now()
        
        incoming_docs = db.query(IncomingLetter).join(Classification)\
            .filter(IncomingLetter.archive_status == 'active').all()
        
        for doc in incoming_docs:
            limit = doc.received_date + relativedelta(years=doc.classification.retention_active_period)
            if today > limit:
                doc.archive_status = 'inactive'
                counter += 1

        outgoing_docs = db.query(OutgoingLetter).join(Classification)\
            .filter(OutgoingLetter.archive_status == 'active').all()
        
        for doc in outgoing_docs:
            limit = doc.sent_date + relativedelta(years=doc.classification.retention_active_period)
            if today > limit:
                doc.archive_status = 'inactive'
                counter += 1

        finance_docs = db.query(FinanceArchive).join(Classification)\
            .filter(FinanceArchive.archive_status == 'active').all()
        
        for doc in finance_docs:
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

# Menjalankan pengecekan sekali dari terminal: python -m app.services.retention_scheduler
if __name__ == "__main__":
    print("--- Menjalankan Scheduler Manual ---")
    check_and_deactivate_archives()
    print("--- Selesai ---")