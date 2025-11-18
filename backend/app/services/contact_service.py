"""Contact service for contact-related operations."""

from typing import Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session as DBSession

from app.models.contact import Contact
from app.schemas.contact import ContactCreateSchema, ContactUpdateSchema


class ContactService:
    """Service for contact-related operations."""

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
        return db.query(Contact).filter(
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
        # Enforce max limit
        limit = min(limit, 100)

        # Base query with user filter
        query = db.query(Contact).filter(Contact.user_id == user_id)

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

        # Apply pipeline stage filter
        if stage and stage != "All":
            query = query.filter(Contact.pipeline_stage == stage)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        contacts = query.order_by(Contact.created_at.desc()).offset(offset).limit(limit).all()

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
    def get_pipeline_stats(db: DBSession, user_id: int) -> dict:
        """
        Get pipeline stage statistics for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with counts per stage and total count
        """
        # Query to get counts grouped by pipeline_stage
        stage_counts = (
            db.query(Contact.pipeline_stage, func.count(Contact.id))
            .filter(Contact.user_id == user_id)
            .group_by(Contact.pipeline_stage)
            .all()
        )

        # Initialize all stages with 0 counts
        stats = {
            "lead_count": 0,
            "qualified_count": 0,
            "proposal_count": 0,
            "client_count": 0,
            "total_count": 0
        }

        # Map stage names to count keys
        stage_mapping = {
            "Lead": "lead_count",
            "Qualified": "qualified_count",
            "Proposal": "proposal_count",
            "Client": "client_count"
        }

        # Populate counts from query results
        for stage, count in stage_counts:
            if stage in stage_mapping:
                stats[stage_mapping[stage]] = count
                stats["total_count"] += count

        return stats
