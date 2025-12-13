from sqlalchemy import Column, String, Enum, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relasi ke Teacher (Untuk Auth)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), unique=True, nullable=False)
    teacher = relationship("Teacher", back_populates="user_account")

    password = Column(String(200), nullable=False)
    role = Column(Enum('headmaster', 'admin', 'teacher', name='user_role'), nullable=False)
    status = Column(Enum('active', 'inactive', name='user_status'), nullable=False)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "identity_number": self.teacher.identity_number if self.teacher else None,
            "full_name": self.teacher.full_name if self.teacher else "Unknown",
            "role": str(self.role),
            "status": str(self.status),
            "created_at": self.created_at
        }