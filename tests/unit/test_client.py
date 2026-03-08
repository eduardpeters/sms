import pytest
from sinch import SinchClient


def test_client_requires_token():
    with pytest.raises(ValueError, match="auth_token must be provided"):
        SinchClient("")


def test_client_accepts_explicit_token():
    client = SinchClient(auth_token="test-token")
    assert client._auth_token == "test-token"


def test_client_uses_default_base_url():
    client = SinchClient(auth_token="test-token")
    assert client._base_url == "https://messaging.api.sinch.com/v1"


def test_client_accepts_custom_base_url():
    client = SinchClient(auth_token="test-token", base_url="http://localhost:8080")
    assert client._base_url == "http://localhost:8080"
