"""
The Message model returned by the API.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict


class MessageStatus(StrEnum):
    """
    Possible states of a message.
    """

    ACCEPTED = "ACCEPTED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class Message(BaseModel):
    """
    Represents a message returned by the Sinch Messaging API.

    """

    id: str = Field(alias="message_id")
    status: MessageStatus
    channel: str
    recipient_id: str
    created_at: datetime

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
