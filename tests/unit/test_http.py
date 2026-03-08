import pytest
import respx
import httpx

from sinch.internal.http import HttpClient
from sinch.exceptions import (
    BadRequestError,
    NotFoundError,
    RecallNotAllowedError,
    SinchAPIError,
    SinchNetworkError,
)


BASE_URL = "https://messaging.api.sinch.com/v1"


@pytest.fixture
def client() -> HttpClient:
    return HttpClient(auth_token="test-token", base_url=BASE_URL)


@respx.mock
def test_auth_header_is_injected(client: HttpClient):
    route = respx.get(f"{BASE_URL}/messages/msg_1").mock(
        return_value=httpx.Response(200, json={"message_id": "msg_1"})
    )
    client.request("GET", "/messages/msg_1")
    assert route.called
    assert route.calls[0].request.headers["x-sinch-auth"] == "test-token"


@respx.mock
def test_raises_client_error_on_network_failure(client: HttpClient):
    respx.get(f"{BASE_URL}/messages/msg_1").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    with pytest.raises(SinchNetworkError):
        client.request("GET", "/messages/msg_1")


@respx.mock
def test_returns_response_on_200(client: HttpClient):
    respx.get(f"{BASE_URL}/messages/msg_1").mock(
        return_value=httpx.Response(200, json={"message_id": "msg_1"})
    )
    response = client.request("GET", "/messages/msg_1")
    assert response.status_code == 200


@respx.mock
def test_returns_response_on_202(client: HttpClient):
    respx.delete(f"{BASE_URL}/messages/msg_1").mock(return_value=httpx.Response(202))
    response = client.request("DELETE", "/messages/msg_1")
    assert response.status_code == 202


@respx.mock
def test_handles_error_v1_responses(client: HttpClient):
    respx.post(f"{BASE_URL}/messages").mock(
        return_value=httpx.Response(
            400,
            json={
                "fault": {
                    "code": "INVALID_RECIPIENT",
                    "description": "Bad phone number",
                }
            },
        )
    )
    with pytest.raises(BadRequestError) as exc_info:
        client.request("POST", "/messages", json={})
    err = exc_info.value
    assert err.status_code == 400
    assert err.code == "INVALID_RECIPIENT"
    assert err.message == "Bad phone number"


@respx.mock
def test_handles_error_v2_responses(client: HttpClient):
    respx.get(f"{BASE_URL}/messages/notthere").mock(
        return_value=httpx.Response(
            404,
            json={
                "error_code": "NOT_FOUND",
                "detail": "No such message",
                "tracking_id": "tr-abc",
            },
        )
    )
    with pytest.raises(NotFoundError) as exc_info:
        client.request("GET", "/messages/notthere")
    err = exc_info.value
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"
    assert err.tracking_id == "tr-abc"

    respx.delete(f"{BASE_URL}/messages/notthere").mock(
        return_value=httpx.Response(
            403,
            json={
                "error_code": "RECALL_NOT_ALLOWED",
                "detail": "Too late",
                "tracking_id": "abc-123",
            },
        )
    )
    with pytest.raises(RecallNotAllowedError) as exc_info:
        client.request("DELETE", "/messages/notthere")
    err = exc_info.value
    assert err.status_code == 403
    assert err.code == "RECALL_NOT_ALLOWED"
    assert err.tracking_id == "abc-123"


@respx.mock
def test_raises_api_error_for_unparseable_error(client: HttpClient):
    respx.post(f"{BASE_URL}/messages").mock(
        return_value=httpx.Response(500, json={"unexpected": "shape"})
    )
    with pytest.raises(SinchAPIError) as exc_info:
        client.request("POST", "/messages", json={})
    err = exc_info.value
    assert err.status_code == 500
    assert err.code == "UNKNOWN"
    assert err.tracking_id is None
