from typing import Any
from sqlalchemy import Column, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Log(Base):
    """Catatan aktivitas operator atau proses otomatis sistem.

    Attributes:
        user_id: Akun pelaku; None berarti aksi dilakukan sistem,
            misalnya scheduler retensi.
        action: Uraian aktivitas.
        timestamp: Waktu aktivitas terjadi.
    """
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    user_id = Column(Integer, ForeignKey('app_user.id', ondelete='SET NULL'), nullable=True, index=True)
    user = relationship("User", backref="logs", lazy="joined")

    def to_dict(self) -> dict[str, Any]:
        """Mengubah baris menjadi dict untuk respons API.

        Returns:
            Kolom baris beserta nama relasi yang dipakai front-end.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            # Key 'username' dipertahankan agar log.js tidak perlu diubah
            "username": self.user.display_name if self.user else "Sistem",
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }
