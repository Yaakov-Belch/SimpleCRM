"""User schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterSchema(BaseModel):
    """Schema for user registration request."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLoginSchema(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    """Schema for user profile update request (all fields optional)."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponseSchema(BaseModel):
    """Schema for user response (excludes hashed_password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    created_at: datetime
    updated_at: datetime
