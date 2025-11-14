from sqlalchemy import Column, String, Text, Enum
from app.core.database import Base

class user(Base):
    __tablename__ = "user"

    nuptk = Column(String, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum('kepala_sekolah', 'admin', 'guru/staff', name='peran_pengguna'), nullable=False)
    status = Column(Enum('aktif', 'non_aktif', name='user_status'), nullable=False)
    created_at = Column(Text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(Text("CURRENT_TIMESTAMP"), nullable=False)