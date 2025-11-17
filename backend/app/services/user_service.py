"""User service for user-related operations."""

from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.models.user import User
from app.services.password_service import PasswordService


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def get_user_by_id(db: DBSession, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: DBSession, email: str) -> Optional[User]:
        """
        Get user by email (case-insensitive).

        Args:
            db: Database session
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(
            func.lower(User.email) == email.lower()
        ).first()

    @staticmethod
    def update_user(
        db: DBSession,
        user_id: int,
        update_data: Dict[str, str]
    ) -> User:
        """
        Update user with partial data.

        Args:
            db: Database session
            user_id: User ID to update
            update_data: Dictionary of fields to update

        Returns:
            Updated User object

        Raises:
            ValueError: If email already exists for another user
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Handle email uniqueness if email is being changed
        if "email" in update_data:
            new_email = update_data["email"]
            existing_user = UserService.get_user_by_email(db, new_email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already exists")
            user.email = new_email

        # Handle full_name update
        if "full_name" in update_data:
            user.full_name = update_data["full_name"]

        # Handle password update (hash it first)
        if "password" in update_data:
            user.hashed_password = PasswordService.hash_password(
                update_data["password"]
            )

        db.commit()
        db.refresh(user)

        return user
