from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer
from app.core.database import Base

class classification(Base):
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True, nullable=False)
    code = Column(String(3), index=True, unique=True, nullable=False)
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
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description
        }