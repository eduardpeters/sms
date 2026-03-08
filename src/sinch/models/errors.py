"""
Internal models representing the the two possible error response shapes from the API.
"""

from pydantic import BaseModel


# V1 uses a nested object with the details
class ErrorV1Fault(BaseModel):
    code: str
    description: str


class ErrorV1(BaseModel):
    fault: ErrorV1Fault


class ErrorV2(BaseModel):
    error_code: str
    detail: str
    tracking_id: str
