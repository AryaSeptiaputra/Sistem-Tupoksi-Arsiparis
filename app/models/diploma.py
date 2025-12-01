from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Diploma(Base):
    """
    Represents a vocational student's diploma (Ijazah SMK) stored as an archived document.

    This model serves as part of the archive documentation system for Vocational High School (SMK).
    It stores metadata extracted from diploma documents and tracks the physical collection status
    of the diploma by the student.

    Attributes:
        id (int): Primary key of the diploma record.
        number (str): Serial number of the diploma (Nomor Seri Ijazah - DN/xx).
        student_name (str): Full name of the student.
        major (str): Vocational major/competency (Kompetensi Keahlian), e.g., 'Teknik Komputer Jaringan'.
        academic_year (str): Academic year of graduation, e.g., '2024/2025'.
        is_collected (bool): Status indicating if the physical diploma has been collected (Sudah diambil/Belum).
        collected_at (datetime): Timestamp when the diploma was collected (if applicable).
        attachment_path (str): Storage path or filename of the scanned document.
        created_at (datetime): Timestamp when the record is created.
        updated_at (datetime): Timestamp when the record is last modified.
        user_id (int): Reference to the admin/staff who created the archive entry.
        user (User): Relationship to the User model.
    """

    __tablename__ = "diploma"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False, unique=True)
    student_name = Column(String(100), index=True, nullable=False)
    
    # Di SMK, nama jurusan/kompetensi keahlian bisa cukup panjang
    major = Column(String(100), index=True, nullable=False) 
    
    academic_year = Column(String(9), index=True, nullable=False)
    
    # Atribut baru: Status pengambilan ijazah
    is_collected = Column(Boolean, default=False, nullable=False)
    collected_at = Column(DateTime, nullable=True)

    attachment_path = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="diplomas", lazy="joined")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert diploma object to complete dictionary format for API responses.
        
        Returns:
            dict: A dictionary containing diploma metadata and collection status.
        """
        return {
            "id": self.id,
            "number": self.number,
            "student_name": self.student_name,
            "major": self.major,
            "academic_year": self.academic_year,
            "status": {
                "is_collected": self.is_collected,
                "collected_at": self.collected_at,
                "status_text": "Sudah Diambil" if self.is_collected else "Belum Diambil"
            },
            "attachment_path": self.attachment_path,
            "created_by": self.user.username if self.user else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }