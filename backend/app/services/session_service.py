"""Session management service."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session


class SessionService:
    """Service for handling session creation, validation, and deletion."""

    @staticmethod
    def generate_token() -> str:
        """
        Generate a cryptographically secure random session token.

        Returns:
            Random token string (approximately 43 characters, base64-encoded)
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_session(
        db: DBSession,
        user_id: int,
        duration_days: int = 7
    ) -> Session:
        """
        Create a new session for a user.

        Args:
            db: Database session
            user_id: ID of the user
            duration_days: Session duration in days (default: 7)

        Returns:
            Created Session object
        """
        # Generate unique token
        token = SessionService.generate_token()

        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(days=duration_days)

        # Create session
        session = Session(
            session_token=token,
            user_id=user_id,
            expires_at=expires_at
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def validate_session(db: DBSession, token: str) -> Optional[Session]:
        """
        Validate a session token.

        Args:
            db: Database session
            token: Session token to validate

        Returns:
            Session object if valid and not expired, None otherwise
        """
        session = db.query(Session).filter(
            Session.session_token == token
        ).first()

        if not session:
            return None

        # Check if session has expired
        if session.expires_at <= datetime.utcnow():
            return None

        return session

    @staticmethod
    def delete_session(db: DBSession, token: str) -> bool:
        """
        Delete a session by token.

        Args:
            db: Database session
            token: Session token to delete

        Returns:
            True if session was deleted, False if not found
        """
        session = db.query(Session).filter(
            Session.session_token == token
        ).first()

        if not session:
            return False

        db.delete(session)
        db.commit()

        return True
