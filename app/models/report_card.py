from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReportCard(Base):
    """
    Represents a student's report card stored as an archived document record.

    This model serves as part of the archive documentation system and stores
    essential metadata extracted from report card documents. Each entry is
    linked to the user who uploaded it for audit trail purposes.

    Attributes:
        id (int): Primary key of the report card record.
        number (str): Document number or registry code of the report card.
        student_name (str): Full name of the student as printed in the document.
        class_name (str): The classroom designation (example: 'VIII-A').
        academic_year (str): Academic year period, e.g., '2024/2025'.
        attachment_path (str): Storage path or filename of the uploaded document.
        created_at (datetime): Timestamp when the record is created.
        updated_at (datetime): Timestamp when the record is last modified.
        user_id (int): Reference to the user who created the archive entry.
        user (User): Relationship to the User model.
    """

    __tablename__ = "report_card"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False, unique=True)
    student_name = Column(String(100), index=True, nullable=False)
    class_name = Column(String(50), index=True, nullable=False)
    academic_year = Column(String(9), index=True, nullable=False)
    attachment_path = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="report_cards")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert report card object to complete dictionary format for API responses.
        
        Serializes the ReportCard instance into a comprehensive JSON-compatible
        dictionary containing all essential report card metadata including student
        information, academic period, and audit trail timestamps. The user relationship
        is resolved to provide the creator's username.
        
        Returns:
            dict: A dictionary containing the following keys:
                - id (int): The unique identifier of the report card record
                - number (str): The document registry number (e.g., 'RC/2024/001')
                - student_name (str): Full name of the student
                - class_name (str): Classroom designation (e.g., 'X-A', 'VIII-B')
                - academic_year (str): Academic year period (format: 'YYYY/YYYY', e.g., '2024/2025')
                - attachment_path (str or None): File path to the stored document
                - created_by (str or None): Username of the user who created this record
                - created_at (datetime): Timestamp when record was created
                - updated_at (datetime): Timestamp of last modification
        """
        return {
            "id": self.id,
            "number": self.number,
            "student_name": self.student_name,
            "class_name": self.class_name,
            "academic_year": self.academic_year,
            "attachment_path": self.attachment_path,
            "created_by": self.user.username if self.user else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
