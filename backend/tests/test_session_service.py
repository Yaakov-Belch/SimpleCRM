"""Tests for SessionService."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.models.session import Session
from app.models.user import User
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
def test_user(db: DBSession):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashedpassword123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_generate_token_produces_random_tokens():
    """Test that token generation produces cryptographically random tokens."""
    token1 = SessionService.generate_token()
    token2 = SessionService.generate_token()

    assert token1 != token2
    assert len(token1) >= 32  # Base64 encoding of 32 bytes produces ~43 chars
    assert len(token2) >= 32


def test_create_session_with_default_duration(db: DBSession, test_user: User):
    """Test session creation with default 7-day expiration."""
    session = SessionService.create_session(db, test_user.id)

    assert session.user_id == test_user.id
    assert session.session_token is not None
    assert len(session.session_token) >= 32

    # Check expiration is approximately 7 days from now
    expected_expiry = datetime.utcnow() + timedelta(days=7)
    time_diff = abs((session.expires_at - expected_expiry).total_seconds())
    assert time_diff < 5  # Within 5 seconds tolerance


def test_validate_session_with_valid_token(db: DBSession, test_user: User):
    """Test session validation with a valid, non-expired token."""
    session = SessionService.create_session(db, test_user.id)

    validated_session = SessionService.validate_session(db, session.session_token)

    assert validated_session is not None
    assert validated_session.id == session.id
    assert validated_session.user_id == test_user.id


def test_validate_session_with_expired_token(db: DBSession, test_user: User):
    """Test session validation fails with an expired token."""
    # Create session with past expiration
    session = Session(
        session_token=SessionService.generate_token(),
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
    )
    db.add(session)
    db.commit()

    validated_session = SessionService.validate_session(db, session.session_token)

    assert validated_session is None


def test_delete_session(db: DBSession, test_user: User):
    """Test session deletion."""
    session = SessionService.create_session(db, test_user.id)
    token = session.session_token

    # Delete session
    result = SessionService.delete_session(db, token)
    assert result is True

    # Verify session no longer exists
    deleted_session = SessionService.validate_session(db, token)
    assert deleted_session is None


def test_delete_nonexistent_session(db: DBSession):
    """Test deleting a non-existent session returns False."""
    result = SessionService.delete_session(db, "nonexistent_token")
    assert result is False
