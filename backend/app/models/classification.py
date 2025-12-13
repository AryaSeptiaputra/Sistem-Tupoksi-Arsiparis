from sqlalchemy import Column, String, Text, DateTime, func, Integer
from app.core.database import Base

class Classification(Base):
    """
    Represents the categorization system for letters with Retention Schedule (JRA).
    Update: 'final_action' changed from Enum to String for flexibility.
    """
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True, nullable=False)
    code = Column(String(10), index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # --- Retensi Arsip ---
    retention_active_period = Column(Integer, default=1, nullable=False) 
    retention_inactive_period = Column(Integer, default=2, nullable=False)
    
    # [UBAH] Enum -> String
    # Value contoh: 'destroy', 'permanent', 'assess' (diatur di Frontend)
    final_action = Column(String(50), default='destroy', nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "retention_active_period": self.retention_active_period,
            "retention_inactive_period": self.retention_inactive_period,
            "final_action": self.final_action,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }