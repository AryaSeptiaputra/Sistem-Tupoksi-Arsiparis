from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Diploma(Base):
    __tablename__ = "diploma"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False, unique=True)
    student_name = Column(String(100), index=True, nullable=False)
    major = Column(String(100), index=True, nullable=False) 
    academic_year = Column(String(9), index=True, nullable=False)
    
    is_collected = Column(Boolean, default=False, nullable=False)
    collected_at = Column(DateTime, nullable=True)
    attachment_path = Column(String(255), nullable=True)

    storage_location_id = Column(Integer, ForeignKey("storage_location.id"), nullable=True)
    storage_location = relationship("StorageLocation", backref="diplomas", lazy="joined")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "student_name": self.student_name,
            "major": self.major,
            "academic_year": self.academic_year,
            "is_collected": self.is_collected,
            "collacted_at": self.collected_at,
            "storage_location_id": self.storage_location.id if self.storage_location else None,
            "storage_location_name": self.storage_location.name if self.storage_location else None,
            "created_at": self.created_at,
            "attachment_path": self.attachment_path
        }