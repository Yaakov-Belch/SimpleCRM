"""Tests for User and Session models."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models import Base, Session, User


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_user_creation_with_valid_data(db_session):
    """Test creating a user with valid data."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password_here"
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password == "hashed_password_here"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_email_uniqueness_constraint(db_session):
    """Test that email uniqueness constraint is enforced."""
    user1 = User(
        email="duplicate@example.com",
        full_name="User One",
        hashed_password="hash1"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        email="duplicate@example.com",
        full_name="User Two",
        hashed_password="hash2"
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_session_creation_with_foreign_key(db_session):
    """Test creating a session with valid foreign key relationship."""
    user = User(
        email="session@example.com",
        full_name="Session User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    session = Session(
        session_token="test_token_123",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(session)
    db_session.commit()

    assert session.id is not None
    assert session.session_token == "test_token_123"
    assert session.user_id == user.id
    assert session.expires_at > datetime.utcnow()
    assert session.created_at is not None


def test_session_expiration_logic(db_session):
    """Test session expiration logic with expires_at."""
    user = User(
        email="expire@example.com",
        full_name="Expire User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    # Create expired session
    expired_session = Session(
        session_token="expired_token",
        user_id=user.id,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(expired_session)
    db_session.commit()

    # Verify session is expired
    assert expired_session.expires_at < datetime.utcnow()

    # Create valid session
    valid_session = Session(
        session_token="valid_token",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(valid_session)
    db_session.commit()

    # Verify session is not expired
    assert valid_session.expires_at > datetime.utcnow()


def test_user_session_relationship_cascade(db_session):
    """Test that deleting a user cascades to delete sessions."""
    user = User(
        email="cascade@example.com",
        full_name="Cascade User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    # Create multiple sessions for the user
    session1 = Session(
        session_token="token1",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session2 = Session(
        session_token="token2",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(session1)
    db_session.add(session2)
    db_session.commit()

    user_id = user.id

    # Verify sessions exist
    sessions = db_session.query(Session).filter(Session.user_id == user_id).all()
    assert len(sessions) == 2

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify sessions were cascade deleted
    sessions = db_session.query(Session).filter(Session.user_id == user_id).all()
    assert len(sessions) == 0


def test_session_token_uniqueness(db_session):
    """Test that session tokens must be unique."""
    user = User(
        email="token@example.com",
        full_name="Token User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    session1 = Session(
        session_token="unique_token",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(session1)
    db_session.commit()

    session2 = Session(
        session_token="unique_token",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(session2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_sessions_relationship(db_session):
    """Test bidirectional relationship between User and Sessions."""
    user = User(
        email="relationship@example.com",
        full_name="Relationship User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    session1 = Session(
        session_token="rel_token1",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session2 = Session(
        session_token="rel_token2",
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(session1)
    db_session.add(session2)
    db_session.commit()

    # Test user.sessions relationship
    assert len(user.sessions) == 2
    assert session1 in user.sessions
    assert session2 in user.sessions

    # Test session.user relationship
    assert session1.user == user
    assert session2.user == user
