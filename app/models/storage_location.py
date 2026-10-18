from datetime import datetime
from typing import Any
from sqlalchemy import Column, String, Text, DateTime, Integer
from app.core.database import Base

class StorageLocation(Base):
    """Lokasi fisik penyimpanan arsip, misalnya 'Lemari A' atau 'Rak 3'."""
    __tablename__ = "storage_location"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime, 
        nullable=False,
        default=datetime.now
    )
    updated_at = Column(
        DateTime, 
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }