import enum
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, func, Enum
from app.core.database import Base

class ReferenceCategory(str, enum.Enum):
    """
    Daftar kategori tetap yang digunakan di sistem.
    """
    # 1. Untuk model Diploma (major)
    SCHOOL_MAJOR = "school_major"
    
    # 2. Untuk model Teacher (employment_status, status)
    TEACHER_EMP_STATUS = "teacher_emp_status"
    TEACHER_ACTIVE_STATUS = "teacher_active_status"
    
    # 3. Untuk model FinanceArchive (category)
    FINANCE_CATEGORY = "finance_category"
    
    # 4. Untuk model EmployeeArchive (document_type)
    EMP_DOC_TYPE = "emp_doc_type"
    
    # 5. Untuk model OutgoingLetter (approval_status)
    LETTER_APPROVAL_STATUS = "letter_approval_status"
    
    # 6. Shared: Untuk archive_status (Pastikan ini huruf kecil)
    ARCHIVE_STATUS = "archive_status"

    # 7. Untuk model Classification (final_action)
    FINAL_ACTION = "final_action"

class MasterReference(Base):
    __tablename__ = "master_reference"

    id = Column(Integer, primary_key=True, index=True)
    
    # Menggunakan Enum
    category = Column(Enum('school_major', 'teacher_emp_status', 'teacher_active_status', 'finance_category', 'emp_doc_type', 'letter_approval_status', 'archive_status', 'final_action',  name='category'), 
                      nullable=False, index=True)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    
    sort_order = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            # [PERBAIKAN FATAL DISINI]
            # Hapus .value! Cukup self.category saja.
            "category": self.category, 
            
            "code": self.code,
            "name": self.name,
            "sort_order": self.sort_order,
            "is_active": self.is_active
        }