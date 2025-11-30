from sqlalchemy import Column, String, Enum, DateTime, func, Integer
from app.core.database import Base

class User(Base):
    """
    Represents a registered user within the application.

    This model stores authentication details, personal identification, and
    role-based access control information. It serves as the central entity
    for login sessions and audit logs.

    Attributes:
        id (int): The primary key for the user record.
        nuptk (str): Nomor Unik Pendidik dan Tenaga Kependidikan. A unique 16-digit 
                     identification number for teachers/staff in Indonesia.
        username (str): A unique username used for system login.
        password (str): Hashed password string for security authentication.
        role (Enum): The authorization level of the user. Options are:
                     - 'headmaster': Full access and approval rights.
                     - 'admin': System management rights.
                     - 'teacher': Standard access rights.
        status (Enum): The current state of the user account. Options are:
                       - 'active': Can log in and perform actions.
                       - 'inactive': Account is frozen/disabled.
        created_at (datetime): Timestamp when the user was registered.
        updated_at (datetime): Timestamp when the user record was last modified.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    nuptk = Column(String(16), index=True, nullable=False, unique=True)
    username = Column(String(50), index=True, nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = Column(Enum('headmaster', 'admin', 'teacher', name='user_role'), nullable=False)
    status = Column(Enum('active', 'inactive', name='user_status'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert user object to safe dictionary format excluding sensitive data.
        
        Serializes the User instance into a JSON-compatible dictionary suitable
        for API responses. The password field is intentionally excluded for security
        purposes, ensuring sensitive authentication data is never exposed through
        API endpoints or logs.
        
        Returns:
            dict: A dictionary containing the following keys:
                - id (int): The unique identifier of the user
                - nuptk (str): The 16-digit unique teacher/staff identification number
                - username (str): The username for system login
                - role (str): The user's authorization level ('headmaster', 'admin', or 'teacher')
                - status (str): The account status ('active' or 'inactive')
        """
        return {
            "id": self.id,
            "nuptk": self.nuptk,
            "username": self.username,
            "role": str(self.role),
            "status": str(self.status),
        }