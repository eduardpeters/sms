"""
Channel-specific recipient models.

Used to specify desired channel:
    SMS(phone_number="+15551234567")
    WhatsApp(phone_number="+15559876543")

Each model serializes to the API shape via to_api_payload().
"""

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Recipient(BaseModel):
    """Base class for all channels."""

    phone_number: str = Field(..., min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)

    @abstractmethod
    def to_api_payload(self) -> Any:
        """Serialise to the format this channel's API expects."""
        pass

    @property
    @abstractmethod
    def channel(self) -> str:
        """The channel identifier string sent to the API."""
        pass


class SMS(Recipient):
    """
    An SMS recipient.
    """

    @property
    def channel(self) -> str:
        return "sms"

    def to_api_payload(self) -> str:
        return self.phone_number


class WhatsApp(Recipient):
    """
    A WhatsApp recipient.
    """

    @property
    def channel(self) -> str:
        return "whatsapp"

    def to_api_payload(self) -> dict[str, str]:
        return {"identifier": self.phone_number, "type": "whatsapp_id"}
