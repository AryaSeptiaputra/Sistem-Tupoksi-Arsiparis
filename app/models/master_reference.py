from typing import Any
import enum
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, func, Enum
from app.core.database import Base

class ReferenceCategory(str, enum.Enum):
    """Kategori opsi dropdown yang dikenal sistem."""
    SCHOOL_MAJOR = "school_major"
    TEACHER_EMP_STATUS = "teacher_emp_status"
    TEACHER_ACTIVE_STATUS = "teacher_active_status"
    TEACHER_RANK = "teacher_rank"
    FINANCE_CATEGORY = "finance_category"
    EMP_DOC_TYPE = "emp_doc_type"
    LETTER_APPROVAL_STATUS = "letter_approval_status"
    ARCHIVE_STATUS = "archive_status"
    FINAL_ACTION = "final_action"

class MasterReference(Base):
    """Satu opsi dropdown, misalnya satu jurusan atau satu golongan."""
    __tablename__ = "master_reference"

    id = Column(Integer, primary_key=True, index=True)
    
    # Isi harus sama dengan nilai ReferenceCategory
    category = Column(Enum(
        'school_major', 
        'teacher_emp_status', 
        'teacher_active_status', 
        'teacher_rank',
        'finance_category', 
        'emp_doc_type', 
        'letter_approval_status', 
        'archive_status', 
        'final_action',  
        name='category'), 
        nullable=False, index=True)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    
    sort_order = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
        return {
            "id": self.id,
            "category": self.category, 
            "code": self.code,
            "name": self.name,
            "sort_order": self.sort_order,
            "description": self.description,
            "is_active": self.is_active
        }