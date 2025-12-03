from sqlalchemy import Column, String, Text, DateTime, func, Integer
from app.core.database import Base

class Classification(Base):
    """
    Represents the categorization system for letters.

    This model defines the types or categories of letters (e.g., Invitation, 
    Decree, Official Statement) to help organize the archive efficiently.

    Attributes:
        id (int): The primary key for the classification record.
        name (str): The full descriptive name of the classification (e.g., 'Surat Dinas').
        code (str): A short unique code (e.g., '001', 'DNS') used for letter numbering reference.
        description (str, optional): Additional details explaining the purpose of this category.
        created_at (datetime): Timestamp when the category was created.
        updated_at (datetime): Timestamp when the category was last modified.
    """
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True, nullable=False)
    code = Column(String(10), index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime, 
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime, 
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self):
        """Convert classification object to dictionary format for API responses.
        
        Serializes the Classification instance into a JSON-compatible dictionary
        containing essential classification information. This method is commonly
        used when returning data through REST API endpoints.
        
        Returns:
            dict: A dictionary containing the following keys:
                - id (int): The unique identifier of the classification
                - code (str): The classification code (e.g., '001', 'DNS')
                - name (str): The full name of the classification
                - description (str or None): Additional details about the classification
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description
        }