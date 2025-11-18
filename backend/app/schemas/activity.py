"""Activity schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreateSchema(BaseModel):
    """Schema for activity creation request."""

    type: Literal["Call", "Meeting", "Email", "Note"] = Field(default="Note", description="Type of activity")
    subject: str = Field(default="", max_length=255, description="Activity subject")
    notes: Optional[str] = Field(None, description="Activity notes in markdown format")
    activity_date: datetime = Field(default_factory=datetime.utcnow, description="Date and time of the activity")
    pipeline_stage: Optional[str] = Field(None, description="Pipeline stage (inherited if not provided)")


class ActivityUpdateSchema(BaseModel):
    """Schema for activity update request (all fields optional)."""

    type: Optional[Literal["Call", "Meeting", "Email", "Note"]] = Field(None, description="Type of activity")
    subject: Optional[str] = Field(None, max_length=255, description="Activity subject")
    notes: Optional[str] = Field(None, description="Activity notes in markdown format")
    activity_date: Optional[datetime] = Field(None, description="Date and time of the activity")
    pipeline_stage: Optional[str] = Field(None, description="Pipeline stage")


class ActivityResponseSchema(BaseModel):
    """Schema for activity response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    type: str
    subject: str
    notes: Optional[str]
    activity_date: datetime
    pipeline_stage: str
    created_at: datetime
    updated_at: datetime


class ActivityListResponseSchema(BaseModel):
    """Schema for activity list response (no pagination for simplicity)."""

    activities: list[ActivityResponseSchema]
    total: int
