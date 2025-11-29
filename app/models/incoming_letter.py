from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer, ForeignKey
from app.core.database import Base

class incoming_letter(Base):
    __tablename__ = "incoming_letter"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True, nullable=False, unique=True)
    letter_date = Column(DateTime, index=True, nullable=False)
    recived_date = Column(DateTime, index=True, nullable=False)
    sender = Column(String, index=True, nullable=False)
    subject = Column(Text, index=False, nullable=False)
    classification_id = Column(Integer, ForeignKey('classification.id'), nullable=False, index=True)
    attachment_path = Column(Text, index=False, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False,server_default=func.now(),onupdate=func.now())