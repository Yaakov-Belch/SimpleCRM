"""Attachment routes for file upload/download operations."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import AttachmentResponseSchema
from app.services.activity_service import ActivityService
from app.services.attachment_service import AttachmentService

router = APIRouter(prefix="/api", tags=["attachments"])


@router.post(
    "/activities/{activity_id}/attachments",
    response_model=AttachmentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file attachment to activity",
    description="""
    Upload a file attachment to an activity.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID

    **Request Body:**
    - `file` (required): File to upload (multipart/form-data)

    **Success Response (201):**
    Returns the attachment metadata object.

    **Error Responses:**
    - `400 Bad Request`: No file provided
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Activity not found or not owned by current user
    - `500 Internal Server Error`: File system error during upload
    """
)
async def upload_attachment(
    activity_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Upload file attachment to activity."""
    # Verify activity ownership
    activity = ActivityService.get_activity_by_id(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # Get upload directory
    try:
        upload_dir = AttachmentService.get_upload_directory(activity_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create upload directory: {str(e)}"
        )

    # Generate unique stored filename
    file_extension = Path(file.filename).suffix if file.filename else ""
    stored_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / stored_filename

    # Save file to disk
    try:
        content = await file.read()
        file_path.write_bytes(content)
        file_size = len(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Save attachment metadata to database
    attachment = AttachmentService.save_attachment_metadata(
        db,
        activity_id=activity_id,
        original_filename=file.filename or "unnamed",
        stored_filename=stored_filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type
    )

    return attachment


@router.get(
    "/activities/{activity_id}/attachments/{attachment_id}",
    summary="Download file attachment",
    description="""
    Download a file attachment from an activity.

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID
    - `attachment_id` (required): Attachment ID

    **Success Response (200):**
    Returns the file with appropriate Content-Disposition header.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Attachment not found, not owned by current user, or file doesn't exist
    """
)
def download_attachment(
    activity_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Download file attachment."""
    # Get attachment with ownership verification
    attachment = AttachmentService.get_attachment_by_id(
        db, attachment_id, activity_id, current_user.id
    )

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # Check if file exists
    file_path = Path(attachment.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    # Sanitize original filename for download
    sanitized_filename = AttachmentService.sanitize_filename(attachment.original_filename)

    # Serve file with sanitized original filename
    return FileResponse(
        path=str(file_path),
        filename=sanitized_filename,
        media_type=attachment.mime_type or "application/octet-stream"
    )


@router.delete(
    "/activities/{activity_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file attachment",
    description="""
    Delete a file attachment from an activity (removes both file and database record).

    **Authentication:** Required (Bearer token in Authorization header)

    **Path Parameters:**
    - `activity_id` (required): Activity ID
    - `attachment_id` (required): Attachment ID

    **Success Response (204):**
    No content returned.

    **Error Responses:**
    - `401 Unauthorized`: Missing, invalid, or expired session token
    - `404 Not Found`: Attachment not found or not owned by current user
    """
)
def delete_attachment(
    activity_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Delete file attachment."""
    deleted = AttachmentService.delete_attachment(db, attachment_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    return None
