"""Contact schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional

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
    """Schema for pipeline statistics response."""

    lead_count: int = Field(..., ge=0, description="Number of contacts in Lead stage")
    qualified_count: int = Field(..., ge=0, description="Number of contacts in Qualified stage")
    proposal_count: int = Field(..., ge=0, description="Number of contacts in Proposal stage")
    client_count: int = Field(..., ge=0, description="Number of contacts in Client stage")
    total_count: int = Field(..., ge=0, description="Total number of contacts")
