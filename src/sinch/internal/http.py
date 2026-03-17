from typing import Any

import httpx
from pydantic import ValidationError

from sinch.exceptions import (
    BadRequestError,
    NotFoundError,
    RecallNotAllowedError,
    SinchAPIError,
    SinchNetworkError,
)
from sinch.models.errors import ErrorV1, ErrorV2


class HttpClient:
    """
    Internal HTTP client.
    Handles sending requests and translates API responses/errors to the SDK models
    """

    def __init__(self, auth_token: str, base_url: str) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "X-Sinch-Auth": auth_token,
                "Content-Type": "application/json",
            },
        )

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        try:
            response = self._client.request(method, path, params=params, json=json)
        except httpx.TransportError as e:
            raise SinchNetworkError(str(e)) from e

        # Parse API errors and raise mapped SDK exception
        if not response.is_success:
            _raise_for_response(response)

        return response


def _raise_for_response(response: httpx.Response) -> None:
    status_code = response.status_code

    try:
        body = response.json()
    except Exception:
        raise SinchAPIError(
            status_code=status_code,
            code="INVALID_JSON",
            message=response.text or "Unkown error",
        )

    try:
        # Error payload versions need different handling by shape
        if "fault" in body:
            error = ErrorV1.model_validate(body)
        else:
            error = ErrorV2.model_validate(body)
    except ValidationError:
        # Unexpected error shape, keep status code and raise API error
        raise SinchAPIError(status_code=status_code, code="UNKNOWN", message=str(body))

    _raise_by_status_code(status_code, error)


def _raise_by_status_code(status_code: int, error: ErrorV1 | ErrorV2) -> None:
    if isinstance(error, ErrorV1):
        code = error.fault.code
        message = error.fault.description
        tracking_id = None
    else:
        code = error.error_code
        message = error.detail
        tracking_id = error.tracking_id

    if status_code == 400:
        raise BadRequestError(code=code, message=message, tracking_id=tracking_id)
    if status_code == 404:
        raise NotFoundError(code=code, message=message, tracking_id=tracking_id)
    if status_code == 403:
        raise RecallNotAllowedError(code=code, message=message, tracking_id=tracking_id)

    # Any unexpected status code raises generic API exception
    raise SinchAPIError(
        status_code=status_code, code=code, message=message, tracking_id=tracking_id
    )
