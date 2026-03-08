import json
from typing import Any
import pytest
import respx
import httpx

from sinch import SinchClient, SMS, WhatsApp, MessageStatus
from sinch.exceptions import NotFoundError, RecallNotAllowedError

BASE_URL = "https://messaging.api.sinch.com/v1"

MESSAGE_PAYLOAD = {
    "message_id": "msg_abc123",
    "status": "ACCEPTED",
    "channel": "sms",
    "recipient_id": "+50212345678",
    "created_at": "2026-03-08T12:00:00Z",
}


def _load_request_payload(route: respx.Route) -> dict[str, Any]:
    """
    Test helper to retrieve the first request made and extract its parsed JSON payload
    """
    body = route.calls[0].request

    payload = json.loads(body.content)

    return payload


@pytest.fixture
def client() -> SinchClient:
    return SinchClient(auth_token="test-token")


@respx.mock
def test_send_sms(client: SinchClient):
    route = respx.post(f"{BASE_URL}/messages").mock(
        return_value=httpx.Response(202, json=MESSAGE_PAYLOAD)
    )
    msg = client.messages.send(to=SMS(phone_number="+50212345678"), text="Hello!")

    assert msg.id == "msg_abc123"
    assert msg.status == MessageStatus.ACCEPTED

    request_payload = _load_request_payload(route)
    assert request_payload["channel"] == "sms"
    assert request_payload["recipient"] == "+50212345678"
    assert request_payload["message_content"]["text_message"] == "Hello!"


@respx.mock
def test_send_whatsapp(client: SinchClient):
    route = respx.post(f"{BASE_URL}/messages").mock(
        return_value=httpx.Response(
            202,
            json={
                **MESSAGE_PAYLOAD,
                "channel": "whatsapp",
                "recipient_id": "+50287654321",
            },
        )
    )
    msg = client.messages.send(to=WhatsApp(phone_number="+50287654321"), text="Hi!")

    assert msg.channel == "whatsapp"

    request_payload = _load_request_payload(route)

    assert request_payload["channel"] == "whatsapp"
    assert request_payload["recipient"] == {
        "identifier": "+50287654321",
        "type": "whatsapp_id",
    }
    assert request_payload["message_content"]["text_message"] == "Hi!"


@respx.mock
def test_get_message(client: SinchClient):
    respx.get(f"{BASE_URL}/messages/msg_abc123").mock(
        return_value=httpx.Response(200, json=MESSAGE_PAYLOAD)
    )
    msg = client.messages.get("msg_abc123")
    assert msg.id == "msg_abc123"


@respx.mock
def test_get_message_not_found(client: SinchClient):
    respx.get(f"{BASE_URL}/messages/missing").mock(
        return_value=httpx.Response(
            404,
            json={
                "error_code": "NOT_FOUND",
                "detail": "No such message",
                "tracking_id": "tr-1",
            },
        )
    )
    with pytest.raises(NotFoundError) as exc_info:
        client.messages.get("missing")
    assert exc_info.value.tracking_id == "tr-1"


@respx.mock
def test_recall_returns_none(client: SinchClient):
    respx.delete(f"{BASE_URL}/messages/msg_abc123").mock(
        return_value=httpx.Response(202)
    )
    result = client.messages.recall("msg_abc123")
    assert result is None


@respx.mock
def test_recall_raises_when_not_allowed(client: SinchClient):
    respx.delete(f"{BASE_URL}/messages/msg_abc123").mock(
        return_value=httpx.Response(
            403,
            json={
                "error_code": "RECALL_NOT_ALLOWED",
                "detail": "Too late",
                "tracking_id": "tr-2",
            },
        )
    )
    with pytest.raises(RecallNotAllowedError) as exc_info:
        client.messages.recall("msg_abc123")
    assert exc_info.value.code == "RECALL_NOT_ALLOWED"
