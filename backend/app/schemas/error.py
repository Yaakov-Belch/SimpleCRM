"""Error response schemas."""

from typing import Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Schema for error details."""

    message: str
    field: Optional[str] = None
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: ErrorDetail
