from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime
from core.db import Base

class Email(Base):
    """Model for storing emails in the database. """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    msg_id = Column(String, unique=True, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    snippet = Column(String, nullable=True)
    received_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    is_processed = Column(Boolean, default=False)