from sqlalchemy import Column, String, Text, DateTime, func, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base

class FinanceArchive(Base):
    __tablename__ = "finance_archive"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    fiscal_year = Column(Integer, index=True, nullable=False)
    period_month = Column(Integer, nullable=True) # 1-12
    
    # [UBAH] Enum -> String
    # Contoh value: 'bos_reguler', 'komite', 'bop', 'lainnya'
    category = Column(String(50), default='bos_reguler', nullable=False)
    
    amount = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    attachment_path = Column(String(255), nullable=True)
    
    # Relasi Klasifikasi
    classification_id = Column(Integer, ForeignKey("classification.id"), nullable=False)
    classification = relationship("Classification", backref="finance_archives", lazy="joined")
    
    # Relasi Lokasi
    storage_location_id = Column(Integer, ForeignKey("storage_location.id"), nullable=True)
    storage_location = relationship("StorageLocation", backref="finance_archives", lazy="joined")
    
    # [UBAH] Enum -> String
    archive_status = Column(String(20), default='active', nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "fiscal_year": self.fiscal_year,
            "period_month": self.period_month,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            
            "classification_code": self.classification.code if self.classification else None,
            "storage_location_name": self.storage_location.name if self.storage_location else "Belum Set",
            
            "archive_status": self.archive_status,
            "file_path": self.attachment_path,
            "created_at": self.created_at
        }