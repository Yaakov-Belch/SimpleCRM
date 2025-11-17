"""Authentication response schemas."""

from pydantic import BaseModel

from app.schemas.user import UserResponseSchema


class AuthResponseSchema(BaseModel):
    """Schema for authentication responses (login and register)."""

    user: UserResponseSchema
    session_token: str
