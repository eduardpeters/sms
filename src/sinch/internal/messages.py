from typing import Any

from pydantic import BaseModel

from sinch.internal.http import HttpClient
from sinch.models.channels import Recipient
from sinch.models.message import Message


class MessageContent(BaseModel):
    text_message: str


class SendMessageRequest(BaseModel):
    """
    Represents the API expected schema for sending messages
    """

    channel: str
    recipient: str | dict[str, str]  # str for SMS, dict for WhatsApp
    message_content: MessageContent

    def to_api_payload(self) -> dict[str, Any]:
        """Serialise to the expected API payload."""
        return self.model_dump()


class MessagesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def send(self, to: Recipient, text: str) -> Message:
        request = SendMessageRequest(
            channel=to.channel,
            recipient=to.to_api_payload(),
            message_content=MessageContent(text_message=text),
        )
        response = self._http.request(
            "POST", "/messages", json=request.to_api_payload()
        )
        body = response.json()
        return Message.model_validate(body)
