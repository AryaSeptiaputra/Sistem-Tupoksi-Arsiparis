from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class OutgoingLetter(Base):
    __tablename__ = "outgoing_letter"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False)
    letter_date = Column(DateTime, index=True, nullable=False)
    sent_date = Column(DateTime, index=True, nullable=False)
    destination = Column(String(100), index=True, nullable=False)
    subject = Column(String(255), nullable=True)
    is_decree = Column(Boolean, default=False, index=True, nullable=False)
    attachment_path = Column(String(255), nullable=True)

    # Status Arsip (Fisik)
    archive_status = Column(String(20), default='active', nullable=False)

    # --- [BARU] Status Persetujuan ---
    # Value: 'draft', 'pending', 'approved', 'rejected'
    approval_status = Column(String(20), default='pending', nullable=False)
    # ---------------------------------

    classification_id = Column(Integer, ForeignKey("classification.id"), index=True, nullable=False)
    classification = relationship("Classification", backref="outgoing_letters", lazy="joined")

    storage_location_id = Column(Integer, ForeignKey("storage_location.id"), nullable=True)
    storage_location = relationship("StorageLocation", backref="outgoing_letters", lazy="joined")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "letter_date": self.letter_date.isoformat() if self.letter_date else None,
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "destination": self.destination,
            "subject": self.subject,
            "is_decree": self.is_decree,
            "classification_code": self.classification.code if self.classification else None,
            "storage_location_name": self.storage_location.name if self.storage_location else "Belum ditentukan",
            "archive_status": self.archive_status,
            "approval_status": self.approval_status, # Return status baru
            "file_path": self.attachment_path,
            "created_at": self.created_at
        }