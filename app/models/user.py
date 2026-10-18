from typing import Any

from sqlalchemy import Column, String, Boolean, DateTime, func, Integer
from app.core.database import Base

class User(Base):
    """
    Akun operator tunggal aplikasi (rancangan 001a, K1).

    Tidak ada role dan tidak ada relasi ke data pegawai. Baris lama dari
    tabel `user` disalin ke sini dengan id yang sama oleh
    `scripts/migrate_single_user.py`; hanya satu baris yang boleh aktif.

    Attributes:
        username (str): Nama login, unik. Awalnya NIP lama, bisa diganti.
        password_hash (str): Hash argon2 atas prehash SHA-256 (`app/utils/hash.py`).
        display_name (str): Nama yang tampil di header dan log aktivitas.
        is_active (bool): Login ditolak bila False.
        last_login_at (datetime | None): Waktu login terakhir yang berhasil.
    """
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "is_active": bool(self.is_active),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
