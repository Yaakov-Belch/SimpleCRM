"""Contact service for contact-related operations."""

from typing import Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DBSession

from app.models.activity import Activity
from app.models.contact import Contact
from app.schemas.contact import ContactCreateSchema, ContactUpdateSchema


class ContactService:
    """Service for contact-related operations."""

    # Define active and passive stage lists
    ACTIVE_STAGES = ["Lead", "Qualified", "Proposal", "Client"]
    PASSIVE_STAGES = ["Qualified Out", "Lost Proposal", "Work Completed", "Archived"]

    @staticmethod
    def create_contact(
        db: DBSession,
        user_id: int,
        contact_data: ContactCreateSchema
    ) -> Contact:
        """
        Create a new contact.

        Args:
            db: Database session
            user_id: ID of the user creating the contact
            contact_data: Contact creation data

        Returns:
            Created Contact object
        """
        # Convert website HttpUrl to string if present
        contact_dict = contact_data.model_dump()
        if contact_dict.get("website"):
            contact_dict["website"] = str(contact_dict["website"])

        contact = Contact(
            **contact_dict,
            user_id=user_id
        )

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact

    @staticmethod
    def get_contact_by_id(
        db: DBSession,
        contact_id: int,
        user_id: int
    ) -> Optional[Contact]:
        """
        Get contact by ID with ownership verification.

        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID for ownership verification

        Returns:
            Contact object if found and owned by user, None otherwise
        """
        from sqlalchemy.orm import joinedload
        return db.query(Contact).options(
            joinedload(Contact.activities)
        ).filter(
            Contact.id == contact_id,
            Contact.user_id == user_id
        ).first()

    @staticmethod
    def get_contacts_for_user(
        db: DBSession,
        user_id: int,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        stage: Optional[str] = None
    ) -> Tuple[list[Contact], int]:
        """
        Get contacts for user with pagination, search, and filter.

        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            limit: Items per page (max 100)
            search: Optional search term (searches name, email, company)
            stage: Optional pipeline stage filter

        Returns:
            Tuple of (list of contacts, total count)
        """
        from sqlalchemy.orm import joinedload
        from sqlalchemy import select

        # Enforce max limit
        limit = min(limit, 100)

        # Base query with user filter and eager load activities for current_pipeline_stage
        query = db.query(Contact).options(
            joinedload(Contact.activities)
        ).filter(Contact.user_id == user_id)

        # Apply search filter (case-insensitive OR search)
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Contact.name).like(search_term),
                    func.lower(Contact.email).like(search_term),
                    func.lower(Contact.company).like(search_term)
                )
            )

        # For pipeline stage filtering, we need to filter in Python since current_pipeline_stage
        # is computed from activities. Get all contacts first, then filter.
        # This is acceptable for small datasets; for large datasets, we'd need a different approach.

        # Get all matching contacts (before stage filter)
        all_contacts = query.order_by(Contact.created_at.desc()).all()

        # Apply pipeline stage filter in Python
        if stage and stage != "All":
            # Support comma-separated stage values for multi-stage filtering
            stages = [s.strip() for s in stage.split(',')]
            filtered_contacts = [c for c in all_contacts if c.current_pipeline_stage in stages]
        else:
            filtered_contacts = all_contacts

        # Get total count after stage filter
        total = len(filtered_contacts)

        # Apply pagination to filtered results
        offset = (page - 1) * limit
        contacts = filtered_contacts[offset:offset + limit]

        return contacts, total

    @staticmethod
    def update_contact(
        db: DBSession,
        contact_id: int,
        user_id: int,
        update_data: ContactUpdateSchema
    ) -> Optional[Contact]:
        """
        Update contact with partial data.

        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID for ownership verification
            update_data: Contact update data

        Returns:
            Updated Contact object if found and owned, None otherwise
        """
        contact = ContactService.get_contact_by_id(db, contact_id, user_id)
        if not contact:
            return None

        # Convert Pydantic model to dict, excluding unset fields
        update_dict = update_data.model_dump(exclude_unset=True)

        # Convert website HttpUrl to string if present
        if "website" in update_dict and update_dict["website"]:
            update_dict["website"] = str(update_dict["website"])

        # Update fields
        for field, value in update_dict.items():
            setattr(contact, field, value)

        db.commit()
        # Query contact again to get fresh data
        return ContactService.get_contact_by_id(db, contact_id, user_id)

    @staticmethod
    def delete_contact(
        db: DBSession,
        contact_id: int,
        user_id: int
    ) -> bool:
        """
        Delete contact (hard delete).

        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found or not owned
        """
        contact = ContactService.get_contact_by_id(db, contact_id, user_id)
        if not contact:
            return False

        db.delete(contact)
        db.commit()

        return True

    @staticmethod
    def get_pipeline_stats(
        db: DBSession,
        user_id: int,
        search: Optional[str] = None
    ) -> dict:
        """
        Get pipeline stage statistics for a user with active/passive separation.

        Args:
            db: Database session
            user_id: User ID
            search: Optional search query to filter contacts

        Returns:
            Dictionary with active_stages, passive_stages, active_count, passive_count
        """
        # Get all contacts for the user with optional search filter
        contacts = db.query(Contact).filter(Contact.user_id == user_id)

        # Apply search filter if provided
        if search:
            search_term = f"%{search.lower()}%"
            contacts = contacts.filter(
                or_(
                    func.lower(Contact.name).like(search_term),
                    func.lower(Contact.email).like(search_term),
                    func.lower(Contact.company).like(search_term)
                )
            )

        contacts = contacts.all()

        # Initialize stage counts
        active_stages = {stage: 0 for stage in ContactService.ACTIVE_STAGES}
        passive_stages = {stage: 0 for stage in ContactService.PASSIVE_STAGES}

        # Count contacts by their current pipeline stage
        for contact in contacts:
            current_stage = contact.current_pipeline_stage
            if current_stage in active_stages:
                active_stages[current_stage] += 1
            elif current_stage in passive_stages:
                passive_stages[current_stage] += 1

        # Calculate totals
        active_count = sum(active_stages.values())
        passive_count = sum(passive_stages.values())

        return {
            "active_stages": active_stages,
            "passive_stages": passive_stages,
            "active_count": active_count,
            "passive_count": passive_count
        }

    @staticmethod
    def get_filter_counts(
        db: DBSession,
        user_id: int,
        search: Optional[str] = None
    ) -> dict:
        """
        Get filter counts for contacts and activities.

        Args:
            db: Database session
            user_id: User ID
            search: Optional search query to filter contacts

        Returns:
            Dictionary with stage_counts and activity_type_counts
        """
        # Get all contacts for the user with optional search filter
        contacts_query = db.query(Contact).filter(Contact.user_id == user_id)

        # Apply search filter if provided
        if search:
            search_term = f"%{search.lower()}%"
            contacts_query = contacts_query.filter(
                or_(
                    func.lower(Contact.name).like(search_term),
                    func.lower(Contact.email).like(search_term),
                    func.lower(Contact.company).like(search_term)
                )
            )

        contacts = contacts_query.all()

        # Initialize stage counts with all possible stages
        all_stages = ContactService.ACTIVE_STAGES + ContactService.PASSIVE_STAGES
        stage_counts = {stage: 0 for stage in all_stages}

        # Get contact IDs for activity filtering
        contact_ids = [contact.id for contact in contacts]

        # Count contacts by their current pipeline stage
        for contact in contacts:
            current_stage = contact.current_pipeline_stage
            if current_stage in stage_counts:
                stage_counts[current_stage] += 1

        # Get activity type counts for the filtered contacts
        activity_type_counts = {}
        if contact_ids:
            activity_counts = (
                db.query(Activity.type, func.count(Activity.id))
                .filter(Activity.contact_id.in_(contact_ids))
                .group_by(Activity.type)
                .all()
            )
            activity_type_counts = {activity_type: count for activity_type, count in activity_counts}
        else:
            # If no contacts match, return empty activity counts
            activity_type_counts = {"Call": 0, "Meeting": 0, "Email": 0, "Note": 0}

        # Remove stages with zero counts for cleaner response
        stage_counts = {stage: count for stage, count in stage_counts.items() if count > 0}

        return {
            "stage_counts": stage_counts,
            "activity_type_counts": activity_type_counts
        }
