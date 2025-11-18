"""Attachment service for file attachment operations."""

import os
import re
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.activity import Activity
from app.models.attachment import Attachment
from app.models.contact import Contact


class AttachmentService:
    """Service for attachment-related operations."""

    @staticmethod
    def save_attachment_metadata(
        db: DBSession,
        activity_id: int,
        original_filename: str,
        stored_filename: str,
        file_path: str,
        file_size: int,
        mime_type: Optional[str] = None
    ) -> Attachment:
        """
        Save attachment metadata to database.

        Args:
            db: Database session
            activity_id: ID of the activity
            original_filename: Original filename from upload
            stored_filename: Unique filename for storage
            file_path: Full path where file is stored
            file_size: Size of file in bytes
            mime_type: MIME type of file

        Returns:
            Created Attachment object
        """
        attachment = Attachment(
            activity_id=activity_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )

        db.add(attachment)
        db.commit()
        db.refresh(attachment)

        return attachment

    @staticmethod
    def get_attachment_by_id(
        db: DBSession,
        attachment_id: int,
        activity_id: int,
        user_id: int
    ) -> Optional[Attachment]:
        """
        Get attachment by ID with ownership verification.

        Args:
            db: Database session
            attachment_id: Attachment ID
            activity_id: Activity ID
            user_id: User ID for ownership verification

        Returns:
            Attachment object if found and owned by user, None otherwise
        """
        attachment = db.query(Attachment).join(Activity).join(Contact).filter(
            Attachment.id == attachment_id,
            Attachment.activity_id == activity_id,
            Contact.user_id == user_id
        ).first()

        return attachment

    @staticmethod
    def delete_attachment(
        db: DBSession,
        attachment_id: int,
        user_id: int
    ) -> bool:
        """
        Delete attachment (database record and file) with ownership verification.

        Args:
            db: Database session
            attachment_id: Attachment ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found or not owned
        """
        # Get attachment with ownership verification
        attachment = db.query(Attachment).join(Activity).join(Contact).filter(
            Attachment.id == attachment_id,
            Contact.user_id == user_id
        ).first()

        if not attachment:
            return False

        # Delete file from filesystem
        file_path = Path(attachment.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                # Continue with database deletion even if file deletion fails
                pass

        # Delete database record
        db.delete(attachment)
        db.commit()

        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by replacing unsafe characters with '-'.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Replace unsafe characters with '-'
        # Unsafe: /, \, :, *, ?, ", <, >, |, null bytes, and whitespace
        unsafe_pattern = r'[/\\:*?"<>|\x00\s]'
        sanitized = re.sub(unsafe_pattern, '-', filename)

        # Ensure filename is not empty
        if not sanitized or sanitized == '-':
            sanitized = 'unnamed-file'

        return sanitized

    @staticmethod
    def get_upload_directory(activity_id: int) -> Path:
        """
        Get upload directory path for activity and create if doesn't exist.

        Args:
            activity_id: Activity ID

        Returns:
            Path object for upload directory
        """
        base_dir = Path("/home/yaakov/git/SimpleCRM/backend/uploads")
        upload_dir = base_dir / "activities" / str(activity_id)

        # Create directory if it doesn't exist
        upload_dir.mkdir(parents=True, exist_ok=True)

        return upload_dir
