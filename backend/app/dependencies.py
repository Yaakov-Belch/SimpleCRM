"""FastAPI dependencies for authentication and database."""

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.user import User
from app.services.session_service import SessionService
from app.services.user_service import UserService


def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
    db: DBSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from session token.

    Args:
        token: Authorization header containing "Bearer {token}"
        db: Database session

    Returns:
        Current User object

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Extract token from "Bearer {token}" format
    if token.startswith("Bearer "):
        token = token[7:]
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Validate session
    session = SessionService.validate_session(db, token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user
    user = UserService.get_user_by_id(db, session.user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    return user


def get_current_user_optional(
    token: Optional[str] = Header(None, alias="Authorization"),
    db: DBSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from session token (optional).

    Returns None instead of raising exception if token is invalid.

    Args:
        token: Authorization header containing "Bearer {token}"
        db: Database session

    Returns:
        Current User object if valid token, None otherwise
    """
    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None
