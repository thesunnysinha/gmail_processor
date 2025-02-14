from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field
import datetime
from config import DB_PATH
from db import Base


class Email(Base):
    """ ORM model for storing emails in the database. """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    msg_id = Column(String, unique=True, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    snippet = Column(String, nullable=True)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_processed = Column(Boolean, default=False)

class EmailSchema(BaseModel):
    """ Pydantic schema for email validation. """
    msg_id: str = Field(..., description="Unique message ID from Gmail API")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    snippet: str = Field(default="", description="Email snippet content")
    received_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, description="Email received timestamp")
    is_processed: bool = Field(default=False, description="Flag indicating if the email was processed")

# Database setup
engine = create_engine(DB_PATH, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """ Initialize the database. """
    Base.metadata.create_all(engine)
