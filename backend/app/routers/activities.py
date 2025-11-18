"""Activity routes for CRUD operations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import (
    ActivityCreateSchema,
    ActivityListResponseSchema,
    ActivityResponseSchema,
    ActivityUpdateSchema,
)
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/api", tags=["activities"])


@router.get(
    "/contacts/{contact_id}/activities",
    response_model=ActivityListResponseSchema,
    summary="List activities for a contact",
    description="""
    Retrieve all activities for a specific contact.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `contact_id` (required): Contact ID

    **Success Response (200):**
    ```json
    {
      "activities": [...],
      "total": 10
    }
    ```

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Contact not found or not owned by current user
    """
)
def list_contact_activities(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all activities for a contact."""
    activities = ActivityService.get_activities_for_contact(
        db, contact_id, current_user.id
    )

    if activities is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return ActivityListResponseSchema(
        activities=activities,
        total=len(activities)
    )


@router.post(
    "/contacts/{contact_id}/activities",
    response_model=ActivityResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity for a contact",
    description="""
    Create a new activity for a specific contact.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `contact_id` (required): Contact ID

    **Request Body:**
    - `type` (required): Activity type (Call, Meeting, Email, Note)
    - `subject` (required): Activity subject (max 255 characters)
    - `notes` (optional): Activity notes in markdown format
    - `activity_date` (required): Date and time of the activity

    **Success Response (201):**
    Returns the created activity object.

    **Error Responses:**
    - `400 Bad Request`: Invalid input data
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Contact not found or not owned by current user
    """
)
def create_activity(
    contact_id: int,
    activity_data: ActivityCreateSchema,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Create a new activity for a contact."""
    activity = ActivityService.create_activity(
        db, contact_id, current_user.id, activity_data
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return activity


@router.get(
    "/activities",
    response_model=list[ActivityResponseSchema],
    summary="List all activities for current user",
    description="""
    Retrieve all activities across all contacts for the authenticated user.

    **Authentication:** Required (Bearer token in Authorization header)

    **Query Parameters:**
    - `type` (optional): Filter by activity type (Call, Meeting, Email, Note, All)
    - `search` (optional): Search term for subject and notes (case-insensitive)

    **Success Response (200):**
    Returns array of activity objects.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    """
)
def list_all_activities(
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all activities across all contacts for user."""
    activities = ActivityService.get_all_activities_for_user(
        db, current_user.id, activity_type=type, search=search
    )
    return activities


@router.get(
    "/activities/{activity_id}",
    response_model=ActivityResponseSchema,
    summary="Get a single activity by ID",
    description="""
    Retrieve a single activity by ID.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID

    **Success Response (200):**
    Returns the activity object.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Activity not found or not owned by current user
    """
)
def get_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get a single activity by ID."""
    activity = ActivityService.get_activity_by_id(db, activity_id, current_user.id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


@router.put(
    "/activities/{activity_id}",
    response_model=ActivityResponseSchema,
    summary="Update an activity",
    description="""
    Update an activity by ID. Supports partial updates.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID

    **Request Body (all fields optional):**
    - `type`, `subject`, `notes`, `activity_date`

    **Success Response (200):**
    Returns the updated activity object.

    **Error Responses:**
    - `400 Bad Request`: Invalid input data
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Activity not found or not owned by current user
    """
)
def update_activity(
    activity_id: int,
    update_data: ActivityUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Update an activity by ID."""
    activity = ActivityService.update_activity(
        db, activity_id, current_user.id, update_data
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


@router.delete(
    "/activities/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an activity",
    description="""
    Permanently delete an activity by ID (hard delete).

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID

    **Success Response (204):**
    No content returned.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Activity not found or not owned by current user
    """
)
def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Delete an activity by ID (hard delete)."""
    deleted = ActivityService.delete_activity(db, activity_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return None
