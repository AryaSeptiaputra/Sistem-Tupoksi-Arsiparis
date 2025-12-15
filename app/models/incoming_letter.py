from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class IncomingLetter(Base):
    __tablename__ = "incoming_letter"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False, unique=True)
    letter_date = Column(DateTime, index=True, nullable=False)
    received_date = Column(DateTime, index=True, nullable=False)
    sender = Column(String(100), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    attachment_path = Column(String(255), nullable=True)
    
    # Relasi Klasifikasi
    classification_id = Column(Integer, ForeignKey('classification.id'), nullable=False, index=True)
    classification = relationship("Classification", backref="incoming_letters", lazy="joined")

    # Relasi Lokasi
    storage_location_id = Column(Integer, ForeignKey('storage_location.id'), nullable=True, index=True)
    storage_location = relationship("StorageLocation", backref="incoming_letters", lazy="joined")

    # Status Arsip (String)
    archive_status = Column(String(20), default='active', nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "letter_date": self.letter_date.isoformat() if self.letter_date else None,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "sender": self.sender,
            "subject": self.subject,
            "classification_id": self.classification.id if self.classification else None,
            "classification_code": self.classification.code if self.classification else None,
            "classification_name": self.classification.name if self.classification else None,
            "storage_location_id": self.storage_location.id if self.storage_location else None,
            "storage_location_name": self.storage_location.name if self.storage_location else None,
            "archive_status": self.archive_status,
            "file_path": self.attachment_path,
            "created_at": self.created_at
        }