"""Contact routes for CRUD operations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import (
    ContactCreateSchema,
    ContactListResponseSchema,
    ContactResponseSchema,
    ContactUpdateSchema,
    FilterCountsResponseSchema,
    PipelineStatsResponseSchema,
)
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.post(
    "",
    response_model=ContactResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
    description="""
    Create a new contact for the authenticated user.

    **Authentication:** Required (Bearer token in Authorization header)

    **Headers:**
    - `Authorization` (required): Bearer token, e.g., "Bearer abc123...xyz"

    **Request Body:**
    - `name` (required): Contact name (max 255 characters)
    - `email` (required): Valid email address
    - `phone` (optional): Phone number
    - `company` (optional): Company name
    - `job_title` (optional): Job title
    - `website` (optional): Website URL
    - `notes` (optional): Notes about the contact
    - `pipeline_stage` (optional): One of Lead, Qualified, Proposal, Client (default: Lead)

    **Success Response (201):**
    ```json
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "company": "Acme Corp",
      "job_title": "CEO",
      "website": "https://example.com",
      "notes": "Important client",
      "pipeline_stage": "Lead",
      "user_id": 1,
      "created_at": "2025-11-17T10:30:00Z",
      "updated_at": "2025-11-17T10:30:00Z"
    }
    ```

    **Error Responses:**
    - `400 Bad Request`: Invalid input data
    - `401 Unauthorized`: Missing, invalid, or expired session token
    """
)
def create_contact(
    contact_data: ContactCreateSchema,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Create a new contact."""
    contact = ContactService.create_contact(db, current_user.id, contact_data)
    return contact


@router.get(
    "/pipeline-stats",
    response_model=PipelineStatsResponseSchema,
    summary="Get pipeline stage statistics",
    description="""
    Retrieve contact counts grouped by pipeline stage for the authenticated user.
    Returns separate counts for active and passive stages.

    **Authentication:** Required (Bearer token in Authorization header)

    **Query Parameters:**
    - `search` (optional): Search term to filter contacts (case-insensitive)

    **Success Response (200):**
    ```json
    {
      "active_stages": {
        "Lead": 10,
        "Qualified": 5,
        "Proposal": 3,
        "Client": 8
      },
      "passive_stages": {
        "Qualified Out": 2,
        "Lost Proposal": 1,
        "Work Completed": 4,
        "Archived": 3
      },
      "active_count": 26,
      "passive_count": 10
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    """
)
def get_pipeline_stats(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get pipeline stage statistics for the current user."""
    stats = ContactService.get_pipeline_stats(db, current_user.id, search)
    return PipelineStatsResponseSchema(**stats)


@router.get(
    "/filter-counts",
    response_model=FilterCountsResponseSchema,
    summary="Get filter counts for contacts and activities",
    description="""
    Retrieve counts for pipeline stages and activity types.
    Counts respect the optional search query parameter.

    **Authentication:** Required (Bearer token in Authorization header)

    **Query Parameters:**
    - `search` (optional): Search term to filter contacts (case-insensitive)

    **Success Response (200):**
    ```json
    {
      "stage_counts": {
        "Lead": 15,
        "Qualified": 8,
        "Proposal": 5,
        "Client": 12
      },
      "activity_type_counts": {
        "Note": 42,
        "Call": 18,
        "Meeting": 12,
        "Email": 25
      }
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    """
)
def get_filter_counts(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get filter counts for contacts and activities."""
    counts = ContactService.get_filter_counts(db, current_user.id, search)
    return FilterCountsResponseSchema(**counts)


@router.get(
    "",
    response_model=ContactListResponseSchema,
    summary="List all contacts for current user",
    description="""
    Retrieve a paginated list of contacts for the authenticated user.

    Supports search and filtering by pipeline stage.

    **Authentication:** Required (Bearer token in Authorization header)

    **Query Parameters:**
    - `page` (optional): Page number (default: 1)
    - `limit` (optional): Items per page (default: 50, max: 100)
    - `search` (optional): Search term for name, email, or company (case-insensitive)
    - `stage` (optional): Filter by pipeline stage (Lead, Qualified, Proposal, Client, All)

    **Success Response (200):**
    ```json
    {
      "contacts": [...],
      "total": 100,
      "page": 1,
      "limit": 50,
      "has_more": true
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    """
)
def list_contacts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all contacts for current user with pagination, search, and filter."""
    contacts, total = ContactService.get_contacts_for_user(
        db, current_user.id, page, limit, search, stage
    )

    has_more = (page * limit) < total

    return ContactListResponseSchema(
        contacts=contacts,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more
    )


@router.get(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    summary="Get a single contact by ID",
    description="""
    Retrieve a single contact by ID.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `contact_id` (required): Contact ID

    **Success Response (200):**
    Returns the contact object.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Contact not found or not owned by current user
    """
)
def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get a single contact by ID."""
    contact = ContactService.get_contact_by_id(db, contact_id, current_user.id)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    summary="Update a contact",
    description="""
    Update a contact by ID. Supports partial updates.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `contact_id` (required): Contact ID

    **Request Body (all fields optional):**
    - `name`, `email`, `phone`, `company`, `job_title`, `website`, `notes`, `pipeline_stage`

    **Success Response (200):**
    Returns the updated contact object.

    **Error Responses:**
    - `400 Bad Request`: Invalid input data (e.g., invalid pipeline_stage value)
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Contact not found or not owned by current user
    """
)
def update_contact(
    contact_id: int,
    update_data: ContactUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Update a contact by ID."""
    contact = ContactService.update_contact(db, contact_id, current_user.id, update_data)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a contact",
    description="""
    Permanently delete a contact by ID (hard delete).

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `contact_id` (required): Contact ID

    **Success Response (204):**
    No content returned.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Contact not found or not owned by current user
    """
)
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Delete a contact by ID (hard delete)."""
    deleted = ContactService.delete_contact(db, contact_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return None
