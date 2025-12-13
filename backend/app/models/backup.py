from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Backup(Base):
    __tablename__ = 'backup'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='SET NULL'), nullable=True, index=True)
    user = relationship('User', backref='backup', lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "triggered_by": self.user.username if self.user else "SYSTEM"
        }
