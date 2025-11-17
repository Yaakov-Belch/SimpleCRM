"""Tests for authentication middleware."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.session_service import SessionService


@pytest.fixture
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def authenticated_user(db: DBSession):
    """Create an authenticated user with session."""
    user, session = AuthService.register(
        db,
        full_name="Auth User",
        email="auth@example.com",
        password="password123"
    )
    return user, session


def test_get_current_user_with_valid_token(db: DBSession, authenticated_user):
    """Test get_current_user allows request with valid session token."""
    user, session = authenticated_user
    token = f"Bearer {session.session_token}"

    current_user = get_current_user(token=token, db=db)

    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.email == user.email


def test_get_current_user_with_invalid_token(db: DBSession):
    """Test get_current_user rejects request with invalid token."""
    token = "Bearer invalid_token_12345"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 401
    assert "Invalid or expired session" in exc_info.value.detail


def test_get_current_user_with_expired_token(db: DBSession, authenticated_user):
    """Test get_current_user rejects request with expired token."""
    user, session = authenticated_user

    # Manually expire the session
    from datetime import datetime, timedelta
    session.expires_at = datetime.utcnow() - timedelta(days=1)
    db.commit()

    token = f"Bearer {session.session_token}"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 401


def test_get_current_user_with_no_token(db: DBSession):
    """Test get_current_user rejects request with no token."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=None, db=db)

    assert exc_info.value.status_code == 401


def test_get_current_user_optional_returns_none_for_invalid(db: DBSession):
    """Test get_current_user_optional returns None instead of raising exception."""
    token = "Bearer invalid_token"

    current_user = get_current_user_optional(token=token, db=db)

    assert current_user is None


def test_get_current_user_optional_returns_user_for_valid(db: DBSession, authenticated_user):
    """Test get_current_user_optional returns user for valid token."""
    user, session = authenticated_user
    token = f"Bearer {session.session_token}"

    current_user = get_current_user_optional(token=token, db=db)

    assert current_user is not None
    assert current_user.id == user.id
