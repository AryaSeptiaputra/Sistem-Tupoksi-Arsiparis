from __future__ import annotations

from datetime import datetime
from typing import Any
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Teacher(Base):
    """Data induk guru dan tenaga kependidikan."""
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True)

    # NIP atau NUPTK
    identity_number = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(150), index=True, nullable=False)
    
    # Nilai L/P divalidasi di front-end
    gender = Column(String(20), nullable=False) 
    
    # Contoh: 'PNS', 'PPPK', 'Honorer', 'GTY'
    employment_status = Column(String(50), nullable=False)
    
    # Golongan, contoh: III/a
    rank = Column(String(100), nullable=True)
    
    # Status keaktifan, contoh: 'Aktif', 'Pensiun', 'Keluar', 'Cuti', 'Meninggal Dunia'
    status = Column(String(50), default="Aktif", nullable=False)

    address = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Tanpa cascade delete: guru yang masih punya arsip ditolak dihapus oleh delete_teacher
    my_archives = relationship("EmployeeArchive", back_populates="owner")

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
        return {
            "id": self.id,
            "identity_number": self.identity_number,
            "full_name": self.full_name,
            "gender": self.gender,
            "employment_status": self.employment_status,
            "rank": self.rank,
            "status": self.status,
            "address": self.address,
            "created_at": self.created_at
        }