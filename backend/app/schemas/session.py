"""Session schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponseSchema(BaseModel):
    """Schema for session response."""

    model_config = ConfigDict(from_attributes=True)

    session_token: str
    expires_at: datetime
