from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer, ForeignKey
from app.core.database import Base

class outcoming_letter(Base):
    __tablename__ = "outcoming_table"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index= True, nullable=False)
    letter_date = Column(DateTime, index=True, nullable=False)
    recived_data = Column(DateTime, index=True, nullable=False)
    destination = Column(String, index=True, nullable=False)
    subject = Column(Text, index=False, nullable=True)
    is_decree = Column(Enum('iya', 'bukan', name="letter_status"), index=True, nullable=False )
    classification_id = Column(Integer, ForeignKey("classification.id"), index=True, nullable=False)
    attachment_path = Column(Text, index=False, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False,server_default=func.now(),onupdate=func.now())