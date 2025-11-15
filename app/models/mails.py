from sqlalchemy import Column, String, Text, Enum, DateTime, func, Integer
from app.core.database import Base

class mails(Base):
    __tablename__ = "mails"

    id = Column(Integer, primary_key=True, index=True)
    mail_id = Column(String(36), primary_key=True, index=True)
    