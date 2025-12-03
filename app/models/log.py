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
        """Convert log entry object to dictionary format with ISO-formatted timestamp.
        
        Serializes the Log instance into a JSON-compatible dictionary suitable
        for audit trail reports and API responses. The timestamp is converted
        to ISO 8601 format for standardized date-time representation.
        
        Returns:
            dict: A dictionary containing the following keys:
                - id (int): The unique identifier of the log entry
                - user_id (int): The ID of the user who performed the action
                - action (str): Description of the action performed (e.g., 'Deleted letter IN/001/2024')
                - timestamp (str): ISO 8601 formatted datetime string (e.g., '2024-11-30T10:30:45.123456')
        """
        try:
            if self.user and self.user.username:
                username = self.user.username
        except:
            pass

        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": username,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }