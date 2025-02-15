from pydantic import BaseModel, Field
from datetime import datetime, timezone

class EmailSchema(BaseModel):
    """ Pydantic schema for email validation. """
    msg_id: str = Field(..., description="Unique message ID from Gmail API")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    snippet: str = Field(default="", description="Email snippet content")
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Email received timestamp")
    is_processed: bool = Field(default=False, description="Flag indicating if the email was processed")