"""Activity schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreateSchema(BaseModel):
    """Schema for activity creation request."""

    type: Literal["Call", "Meeting", "Email", "Note"] = Field(..., description="Type of activity")
    subject: str = Field(..., min_length=1, max_length=255, description="Activity subject")
    notes: Optional[str] = Field(None, description="Activity notes in markdown format")
    activity_date: datetime = Field(..., description="Date and time of the activity")


class ActivityUpdateSchema(BaseModel):
    """Schema for activity update request (all fields optional)."""

    type: Optional[Literal["Call", "Meeting", "Email", "Note"]] = Field(None, description="Type of activity")
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Activity subject")
    notes: Optional[str] = Field(None, description="Activity notes in markdown format")
    activity_date: Optional[datetime] = Field(None, description="Date and time of the activity")


class ActivityResponseSchema(BaseModel):
    """Schema for activity response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    type: str
    subject: str
    notes: Optional[str]
    activity_date: datetime
    created_at: datetime
    updated_at: datetime


class ActivityListResponseSchema(BaseModel):
    """Schema for activity list response (no pagination for simplicity)."""

    activities: list[ActivityResponseSchema]
    total: int
