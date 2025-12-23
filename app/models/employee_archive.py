from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, Session
from app.core.database import Base
import datetime

# ================= MODEL =================
class EmployeeArchive(Base):
    __tablename__ = "employee_archive"

    id = Column(Integer, primary_key=True, index=True)
    
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), default='lainnya', nullable=False)
    archive_status = Column(String(50), default='active', nullable=False)
    document_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    attachment_path = Column(String(255), nullable=True)
    
    # --- RELASI KEPEMILIKAN ---
    owner_id = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("Teacher", back_populates="my_archives", lazy="joined")

    # --- RELASI KLASIFIKASI (BARU) ---
    classification_id = Column(Integer, ForeignKey('classification.id'), nullable=True, index=True)
    classification = relationship("Classification", backref="employee_archives", lazy="joined")

    # --- RELASI LOKASI ---
    storage_location_id = Column(Integer, ForeignKey("storage_location.id"), nullable=True)
    storage_location = relationship("StorageLocation", backref="employee_archives", lazy="joined")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "archive_status": self.archive_status,
            "document_year": self.document_year,
            "description": self.description,
            "file_path": self.attachment_path,
            "owner_id": self.owner_id,
            "owner_name": self.owner.full_name if self.owner else "Unknown",
            "owner_identity": self.owner.identity_number if self.owner else "-",
            
            # Data Klasifikasi
            "classification_id": self.classification_id,
            "classification_code": self.classification.code if self.classification else None,
            "classification_name": self.classification.name if self.classification else None,
            
            "storage_location_id": self.storage_location.id if self.storage_location else None,
            "storage_location_name": self.storage_location.name if self.storage_location else None,
            "created_at": self.created_at
        }