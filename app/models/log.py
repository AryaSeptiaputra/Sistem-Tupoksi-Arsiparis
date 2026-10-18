from sqlalchemy import Column, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Log(Base):
    """
    Represents an audit trail or activity history in the system.

    This model is used to record critical actions performed by the operator
    or by automatic system processes (e.g., the retention scheduler).

    Attributes:
        id (int): The primary key for the log entry.
        user_id (int | None): Foreign key to 'app_user.id'. None means the
            action was performed by the system.
        action (str): A text description of what activity occurred.
        timestamp (datetime): The exact time when the action occurred.
    """
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    user_id = Column(Integer, ForeignKey('app_user.id', ondelete='SET NULL'), nullable=True, index=True)
    user = relationship("User", backref="logs", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            # Key 'username' dipertahankan agar log.js tidak perlu diubah
            "username": self.user.display_name if self.user else "Sistem",
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }
