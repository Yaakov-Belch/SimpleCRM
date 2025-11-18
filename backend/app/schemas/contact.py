"""Contact schemas for request/response validation."""

from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ContactCreateSchema(BaseModel):
    """Schema for contact creation request."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    website: Optional[HttpUrl] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)
    pipeline_stage: Literal["Lead", "Qualified", "Proposal", "Client"] = "Lead"


class ContactUpdateSchema(BaseModel):
    """Schema for contact update request (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    website: Optional[HttpUrl] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=5000)
    pipeline_stage: Optional[Literal["Lead", "Qualified", "Proposal", "Client"]] = None


class ContactResponseSchema(BaseModel):
    """Schema for contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    website: Optional[str]
    notes: Optional[str]
    pipeline_stage: str
    current_pipeline_stage: str  # Computed from latest activity
    user_id: int
    created_at: datetime
    updated_at: datetime


class ContactListResponseSchema(BaseModel):
    """Schema for paginated contact list response."""

    contacts: list[ContactResponseSchema]
    total: int
    page: int
    limit: int
    has_more: bool


class PipelineStatsResponseSchema(BaseModel):
    """Schema for pipeline statistics response with active/passive separation."""

    active_stages: Dict[str, int] = Field(..., description="Counts for active stages")
    passive_stages: Dict[str, int] = Field(..., description="Counts for passive stages")
    active_count: int = Field(..., ge=0, description="Total count of contacts in active stages")
    passive_count: int = Field(..., ge=0, description="Total count of contacts in passive stages")


class FilterCountsResponseSchema(BaseModel):
    """Schema for filter counts response."""

    stage_counts: Dict[str, int] = Field(..., description="Counts by pipeline stage")
    activity_type_counts: Dict[str, int] = Field(..., description="Counts by activity type")
