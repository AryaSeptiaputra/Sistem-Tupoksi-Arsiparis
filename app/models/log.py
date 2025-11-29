from sqlalchemy import Column, Text, DateTime, func, Integer, ForeignKey
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
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    def to_dict(self):
        """
        Serializes the Log object into a dictionary format.

        Returns:
            dict: A dictionary containing log details with the timestamp 
                  formatted as an ISO 8601 string.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }