"""Attachment schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttachmentResponseSchema(BaseModel):
    """Schema for attachment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: Optional[str]
    uploaded_at: datetime
