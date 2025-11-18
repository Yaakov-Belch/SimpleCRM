"""Pydantic schemas for request/response validation."""

from app.schemas.auth import AuthResponseSchema
from app.schemas.contact import (
    ContactCreateSchema,
    ContactListResponseSchema,
    ContactResponseSchema,
    ContactUpdateSchema,
    PipelineStatsResponseSchema,
)
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.session import SessionResponseSchema
from app.schemas.user import (
    UserLoginSchema,
    UserRegisterSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

__all__ = [
    "AuthResponseSchema",
    "ContactCreateSchema",
    "ContactListResponseSchema",
    "ContactResponseSchema",
    "ContactUpdateSchema",
    "PipelineStatsResponseSchema",
    "ErrorDetail",
    "ErrorResponse",
    "SessionResponseSchema",
    "UserLoginSchema",
    "UserRegisterSchema",
    "UserResponseSchema",
    "UserUpdateSchema",
]
