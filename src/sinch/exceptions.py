class SinchError(Exception):
    """Base class for all SDK errors."""


class SinchNetworkError(SinchError):
    """Raised when a network-level error occurs."""


class SinchAPIError(SinchError):
    """Raised when the API returns a 4xx or 5xx response."""

    def __init__(
        self, status_code: int, code: str, message: str, tracking_id: str | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.tracking_id = tracking_id


class BadRequestError(SinchAPIError):
    """Raised on HTTP 400."""

    def __init__(self, code: str, message: str, tracking_id: str | None = None) -> None:
        super().__init__(400, code, message, tracking_id)


class NotFoundError(SinchAPIError):
    """Raised on HTTP 404."""

    def __init__(self, code: str, message: str, tracking_id: str | None = None) -> None:
        super().__init__(404, code, message, tracking_id)


class RecallNotAllowedError(SinchAPIError):
    """Raised on HTTP 403 when a message cannot be recalled."""

    def __init__(self, code: str, message: str, tracking_id: str | None = None) -> None:
        super().__init__(403, code, message, tracking_id)
