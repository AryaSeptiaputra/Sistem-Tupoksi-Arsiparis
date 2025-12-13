from sqlalchemy import Column, String, Text, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Teacher(Base):
    """
    Model Master Data Guru & Tenaga Kependidikan.
    Update: Menggunakan tipe data String untuk fleksibilitas (menggantikan Enum).
    """
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True)

    # 1. Identitas
    identity_number = Column(String(50), unique=True, index=True, nullable=False) # NIP/NUPTK
    full_name = Column(String(150), index=True, nullable=False)
    
    # 2. Biodata (Ubah Enum jadi String)
    # Validasi input L/P dilakukan di Frontend/JS
    gender = Column(String(20), nullable=False) 
    
    # 3. Kepegawaian (Ubah Enum jadi String)
    # Contoh isi: 'PNS', 'PPPK', 'Honorer', 'GTY' -> Diatur di JS
    employment_status = Column(String(50), nullable=False)
    
    # Golongan (Opsional)
    rank = Column(String(20), nullable=True) # Cth: III/a
    
    # 4. [BARU] Status Keaktifan di Sekolah
    # Contoh isi: 'Aktif', 'Pensiun', 'Keluar', 'Cuti', 'Meninggal Dunia'
    status = Column(String(50), default="Aktif", nullable=False)

    address = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # --- RELASI ---
    # 1. Relasi ke Akun Login (Tetap ada untuk login)
    user_account = relationship("User", back_populates="teacher", uselist=False, cascade="all, delete-orphan")

    # 2. Relasi ke Arsip Pribadi (Milik Guru Ini) - Cascade Delete
    my_archives = relationship("EmployeeArchive", back_populates="owner", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "identity_number": self.identity_number,
            "full_name": self.full_name,
            "gender": self.gender,
            "employment_status": self.employment_status,
            "rank": self.rank,
            "status": self.status, # Return status keaktifan ke API
            "address": self.address,
            "created_at": self.created_at
        }