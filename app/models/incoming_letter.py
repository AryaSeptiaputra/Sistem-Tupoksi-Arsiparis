from sqlalchemy import Column, String, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class IncomingLetter(Base):
    """
    Represents an incoming letter document received by the organization.

    This model stores details about letters sent from external parties to the
    school/institution, including metadata and file storage references.

    Attributes:
        id (int): The primary key for the letter record.
        number (str): The official reference number listed on the physical letter.
        letter_date (datetime): The date written on the letter by the sender.
        received_date (datetime): The date when the letter was actually received/recorded by the admin.
        sender (str): The name of the agency, person, or organization sending the letter.
        subject (str): The summary or title of the letter's content.
        attachment_path (str, optional): Relative file path to the scanned document/PDF.
        classification_id (int): Foreign key referencing the classification category.
        user_id (int): Foreign key referencing the user who input this data.
        created_at (datetime): Timestamp when the record was created in the system.
        updated_at (datetime): Timestamp when the record was last updated.
    """
    __tablename__ = "incoming_letter"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), index=True, nullable=False, unique=True)
    letter_date = Column(DateTime, index=True, nullable=False)
    received_date = Column(DateTime, index=True, nullable=False)
    sender = Column(String(100), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    attachment_path = Column(String(255), nullable=True)
    
    classification_id = Column(Integer, ForeignKey('classification.id'), nullable=False, index=True)
    classification = relationship("Classification", backref="incoming_letters")

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    user = relationship("User", backref="incoming_letters")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """
        Serializes the IncomingLetter object into a dictionary format.

        Returns:
            dict: A dictionary containing letter details. It resolves the
                  relationship to return the classification code and the username
                  of the inputter instead of just IDs.
        """
        return {
            "id": self.id,
            "number": self.number,
            "sender": self.sender,
            "subject": self.subject,
            "classification": self.classification.code if self.classification else None,
            "input_by": self.user.username if self.user else None
        }