from sqlalchemy import Column, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Log(Base):
    """
    Represents an audit trail or activity history in the system.

    This model is used to record critical actions performed by users, 
    ensuring accountability and traceability of changes (e.g., who deleted a letter).

    Attributes:
        id (int): The primary key for the log entry.
        user_id (int): Foreign key referencing the 'user.id' who performed the action.
        action (str): A text description of what activity occurred (e.g., 'Deleted user X').
        timestamp (datetime): The exact time when the action occurred.
    """
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    user = relationship("User", backref="logs", lazy="joined")

    def to_dict(self):
        # 1. Inisialisasi default agar tidak kena UnboundLocalError
        user_display_name = "Unknown User" 

        try:
            # 2. Cek apakah Log punya User, dan User punya Teacher
            if self.user and self.user.teacher:
                # Ambil nama lengkap dari tabel Teacher
                user_display_name = self.user.teacher.full_name
            
            # Opsional: Jika User ada tapi Teacher terhapus (Edge case), pakai ID
            elif self.user:
                user_display_name = f"User #{self.user.id}"
                
        except Exception as e:
            # Print error ke terminal untuk debugging tanpa bikin server crash
            print(f"[Log Model Error] Failed to get user name: {e}")
            pass

        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": user_display_name, # Kirim sebagai 'username' agar frontend tidak perlu diubah
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }