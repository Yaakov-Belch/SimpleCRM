"""Activity service for activity-related operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DBSession, joinedload

from app.models.activity import Activity
from app.models.contact import Contact
from app.schemas.activity import ActivityCreateSchema, ActivityUpdateSchema


class ActivityService:
    """Service for activity-related operations."""

    @staticmethod
    def create_activity(
        db: DBSession,
        contact_id: int,
        user_id: int,
        activity_data: ActivityCreateSchema
    ) -> Optional[Activity]:
        """
        Create a new activity for a contact.

        Args:
            db: Database session
            contact_id: ID of the contact
            user_id: ID of the user (for ownership verification)
            activity_data: Activity creation data

        Returns:
            Created Activity object if contact is owned by user, None otherwise
        """
        # Verify contact ownership
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == user_id
        ).first()

        if not contact:
            return None

        # Prepare activity data
        activity_dict = activity_data.model_dump()

        # Set default values if not provided
        if not activity_dict.get("type"):
            activity_dict["type"] = "Note"
        if not activity_dict.get("activity_date"):
            activity_dict["activity_date"] = datetime.utcnow()
        if activity_dict.get("subject") is None:
            activity_dict["subject"] = ""

        # Handle pipeline_stage inheritance
        if not activity_dict.get("pipeline_stage"):
            # Query contact's most recent activity to inherit pipeline_stage
            latest_activity = db.query(Activity).filter(
                Activity.contact_id == contact_id
            ).order_by(
                Activity.activity_date.desc()
            ).first()

            if latest_activity:
                activity_dict["pipeline_stage"] = latest_activity.pipeline_stage
            else:
                # No previous activities, default to "Lead"
                activity_dict["pipeline_stage"] = "Lead"

        activity = Activity(
            contact_id=contact_id,
            **activity_dict
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity

    @staticmethod
    def get_activities_for_contact(
        db: DBSession,
        contact_id: int,
        user_id: int
    ) -> Optional[list[Activity]]:
        """
        Get all activities for a contact with ownership verification.

        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID for ownership verification

        Returns:
            List of activities sorted by activity_date desc, or None if contact not owned
        """
        # Verify contact ownership
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == user_id
        ).first()

        if not contact:
            return None

        activities = db.query(Activity).options(
            joinedload(Activity.attachments)
        ).filter(
            Activity.contact_id == contact_id
        ).order_by(
            Activity.activity_date.desc()
        ).all()

        return activities

    @staticmethod
    def get_all_activities_for_user(
        db: DBSession,
        user_id: int,
        activity_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> list[Activity]:
        """
        Get all activities across all user's contacts with optional filtering.

        Args:
            db: Database session
            user_id: User ID
            activity_type: Optional filter by activity type
            search: Optional search term for subject and notes

        Returns:
            List of activities sorted by activity_date desc
        """
        # Query activities through contact relationship
        query = db.query(Activity).join(Contact).filter(
            Contact.user_id == user_id
        ).options(
            joinedload(Activity.attachments)
        )

        # Filter by type if provided
        if activity_type and activity_type != "All":
            query = query.filter(Activity.type == activity_type)

        # Search in subject and notes if search term provided
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Activity.subject).like(search_term),
                    func.lower(Activity.notes).like(search_term)
                )
            )

        # Sort by activity date descending
        activities = query.order_by(Activity.activity_date.desc()).all()

        return activities

    @staticmethod
    def get_activity_by_id(
        db: DBSession,
        activity_id: int,
        user_id: int
    ) -> Optional[Activity]:
        """
        Get activity by ID with ownership verification.

        Args:
            db: Database session
            activity_id: Activity ID
            user_id: User ID for ownership verification

        Returns:
            Activity object if found and owned by user, None otherwise
        """
        activity = db.query(Activity).join(Contact).filter(
            Activity.id == activity_id,
            Contact.user_id == user_id
        ).options(
            joinedload(Activity.attachments)
        ).first()

        return activity

    @staticmethod
    def update_activity(
        db: DBSession,
        activity_id: int,
        user_id: int,
        update_data: ActivityUpdateSchema
    ) -> Optional[Activity]:
        """
        Update activity with ownership verification.

        Args:
            db: Database session
            activity_id: Activity ID
            user_id: User ID for ownership verification
            update_data: Activity update data

        Returns:
            Updated Activity object if found and owned, None otherwise
        """
        activity = ActivityService.get_activity_by_id(db, activity_id, user_id)
        if not activity:
            return None

        # Update fields with provided values
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(activity, field, value)

        db.commit()
        db.refresh(activity)

        return activity

    @staticmethod
    def delete_activity(
        db: DBSession,
        activity_id: int,
        user_id: int
    ) -> bool:
        """
        Delete activity (hard delete) with ownership verification.

        Args:
            db: Database session
            activity_id: Activity ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found or not owned
        """
        activity = ActivityService.get_activity_by_id(db, activity_id, user_id)
        if not activity:
            return False

        db.delete(activity)
        db.commit()

        return True
