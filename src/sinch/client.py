from sinch.internal.http import HttpClient


class SinchClient:
    """
    Client for the Sinch Messaging API.
    Requires providing `auth_token` for initialization.
    Supports custom `base_url` for the API.

    Usage:
        ```
        client = SinchClient(auth_token="your-auth-token")
        # You may also provide an optional custom `base_url` for requests
        client = SinchClient(auth_token="your-auth-token", base_url="http://localhost:8080")
        ```
    Supported resources:
        SMS and WhatsApp messages
    """

    BASE_URL = "https://messaging.api.sinch.com/v1"

    def __init__(self, auth_token: str, base_url: str | None = None) -> None:
        if not auth_token.strip():
            raise ValueError("auth_token must be provided")

        self._auth_token = auth_token
        self._base_url = base_url or self.BASE_URL
        self._http = HttpClient(self._auth_token, self._base_url)
