from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmployeeArchive(Base):
    __tablename__ = "employee_archive"

    id = Column(Integer, primary_key=True, index=True)
    
    document_name = Column(String(255), nullable=False)
    
    # [UBAH] Enum -> String
    # Value contoh: 'sk_cpns', 'ijazah', 'sertifikat', dll
    document_type = Column(String(50), default='lainnya', nullable=False)
    
    document_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    attachment_path = Column(String(255), nullable=True)
    
    # --- RELASI KEPEMILIKAN ---
    # Menunjukkan dokumen ini MILIK guru siapa (Teacher ID)
    owner_id = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("Teacher", back_populates="my_archives", lazy="joined")

    # Lokasi Fisik
    storage_location_id = Column(Integer, ForeignKey("storage_location.id"), nullable=True)
    storage_location = relationship("StorageLocation", backref="employee_archives", lazy="joined")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "document_year": self.document_year,
            "description": self.description,
            "file_path": self.attachment_path,
            
            # Info Pemilik (Owner)
            "owner_id": self.owner_id,
            "owner_name": self.owner.full_name if self.owner else "Unknown",
            "owner_identity": self.owner.identity_number if self.owner else "-",
        
            "storage_location_id": self.storage_location.id if self.storage_location else None,
            "storage_location_name": self.storage_location.name if self.storage_location else None,
            "created_at": self.created_at
        }