"""Authentication service for user registration, login, and logout."""

from typing import Optional, Tuple

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.models.user import User
from app.services.password_service import PasswordService
from app.services.session_service import SessionService
from app.services.user_service import UserService


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register(
        db: DBSession,
        full_name: str,
        email: str,
        password: str
    ) -> Tuple[User, Session]:
        """
        Register a new user and create a session.

        Args:
            db: Database session
            full_name: User's full name
            email: User's email
            password: User's plain text password

        Returns:
            Tuple of (User, Session)

        Raises:
            ValueError: If email already exists
        """
        # Check email uniqueness
        existing_user = UserService.get_user_by_email(db, email)
        if existing_user:
            raise ValueError("Email already exists")

        # Hash password
        hashed_password = PasswordService.hash_password(password)

        # Create user
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create session
        session = SessionService.create_session(db, user.id)

        return user, session

    @staticmethod
    def login(
        db: DBSession,
        email: str,
        password: str
    ) -> Optional[Tuple[User, Session]]:
        """
        Authenticate user and create a session.

        Args:
            db: Database session
            email: User's email
            password: User's plain text password

        Returns:
            Tuple of (User, Session) if valid, None if invalid credentials
        """
        # Get user by email (case-insensitive)
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None

        # Verify password
        if not PasswordService.verify_password(password, user.hashed_password):
            return None

        # Create new session
        session = SessionService.create_session(db, user.id)

        return user, session

    @staticmethod
    def logout(db: DBSession, session_token: str) -> bool:
        """
        Logout user by deleting the session.

        Args:
            db: Database session
            session_token: Session token to delete

        Returns:
            True if session was deleted, False if not found
        """
        return SessionService.delete_session(db, session_token)
