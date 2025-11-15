from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer
from app.core.database import Base

class user(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    nuptk = Column(String(16), index=True, nullable=False, unique=True)
    username = Column(String(50), index=True, nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = Column(Enum('kepala_sekolah', 'admin', 'guru/staff', name='peran_pengguna'), nullable=False)
    status = Column(Enum('aktif', 'non_aktif', name='user_status'), nullable=False)
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
            "nuptk": self.nuptk,
            "username": self.username,
            "role": str(self.role),
            "status": str(self.status),
        }