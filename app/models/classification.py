from typing import Any
from sqlalchemy import Column, String, Text, DateTime, func, Integer
from app.core.database import Base

class Classification(Base):
    """Kode klasifikasi arsip beserta jadwal retensinya (JRA).

    Attributes:
        retention_active_period: Masa aktif dalam tahun.
        retention_inactive_period: Masa inaktif dalam tahun.
        final_action: Tindakan akhir, misalnya `destroy`, `permanent`, atau `assess`.
    """
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True, nullable=False)
    code = Column(String(10), index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    retention_active_period = Column(Integer, default=1, nullable=False) 
    retention_inactive_period = Column(Integer, default=2, nullable=False)
    
    final_action = Column(String(50), default='destroy', nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
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