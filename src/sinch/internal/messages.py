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
        """
        Send a message to a recipient.
        """
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

    def get(self, message_id: str) -> Message:
        """
        Retrieve a message by its ID.
        """
        response = self._http.request("GET", f"/messages/{message_id}")
        body = response.json()
        return Message.model_validate(body)

    def list(self, page_size: int = 20) -> "MessagesPage":
        return self._fetch_page(page_size, page_token=None)

    def recall(self, message_id: str) -> None:
        """
        Attempt to recall a message by its ID.
        Availability depends on the channel.
        If unable to recall raises `RecallNotAllowedError` with details.
        """
        self._http.request("DELETE", f"/messages/{message_id}")

    def _fetch_page(
        self,
        page_size: int,
        page_token: str | None,
    ) -> "MessagesPage":
        """
        Internal method to fetch a specific page.
        """
        params: dict[str, Any] = {"page_size": page_size}
        if page_token is not None:
            params["pageToken"] = page_token

        response = self._http.request("GET", "/messages", params=params)
        body = response.json()

        return MessagesPage(
            items=[Message.model_validate(m) for m in body.get("messages", [])],
            next_page_token=body.get("next_page_token"),
            resource=self,
            page_size=page_size,
        )


class MessagesPage:
    """
    Represents a page of messages returned by the API.
    Check for next page availability using `has_next_page`.
    Fetch the next page if available using `next_page` (will return None if no next page exists).
    """

    def __init__(
        self,
        items: list[Message],
        next_page_token: str | None,
        resource: MessagesResource,
        page_size: int,
    ) -> None:
        self.items = items
        self._next_page_token = next_page_token
        self._resource = resource
        self._page_size = page_size

    def has_next_page(self) -> bool:
        return self._next_page_token is not None

    def next_page(self) -> "MessagesPage | None":
        if not self.has_next_page():
            return None

        return self._resource._fetch_page(
            page_size=self._page_size, page_token=self._next_page_token
        )
