from sqlalchemy import Column, String, Text, DateTime, func, Integer
from app.core.database import Base

class StorageLocation(Base):
    """
    Represents the physical location where archives are stored.
    Examples: 'Lemari A', 'Rak 3', 'Boks 10'.
    
    Attributes:
        name (str): The name/label of the storage unit.
        description (str): Details about the location or its contents.
    """
    __tablename__ = "storage_location"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime, 
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime, 
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self):
        """Convert object to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }