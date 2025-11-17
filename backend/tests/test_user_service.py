"""Tests for UserService."""

import pytest
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.services.password_service import PasswordService
from app.services.user_service import UserService


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
        hashed_password=PasswordService.hash_password("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_get_user_by_email_finds_existing_user(db: DBSession, test_user: User):
    """Test get_user_by_email finds an existing user."""
    found_user = UserService.get_user_by_email(db, "test@example.com")

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


def test_get_user_by_email_is_case_insensitive(db: DBSession, test_user: User):
    """Test get_user_by_email is case-insensitive."""
    found_user = UserService.get_user_by_email(db, "TEST@EXAMPLE.COM")

    assert found_user is not None
    assert found_user.id == test_user.id


def test_get_user_by_email_returns_none_for_nonexistent(db: DBSession):
    """Test get_user_by_email returns None for non-existent user."""
    found_user = UserService.get_user_by_email(db, "nonexistent@example.com")

    assert found_user is None


def test_get_user_by_id(db: DBSession, test_user: User):
    """Test get_user_by_id retrieves correct user."""
    found_user = UserService.get_user_by_id(db, test_user.id)

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


def test_update_user_updates_fields_correctly(db: DBSession, test_user: User):
    """Test update_user updates fields correctly."""
    update_data = {"full_name": "Updated Name"}

    updated_user = UserService.update_user(db, test_user.id, update_data)

    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == test_user.email  # Unchanged


def test_update_user_hashes_password_when_provided(db: DBSession, test_user: User):
    """Test update_user hashes password when provided."""
    old_hashed = test_user.hashed_password
    update_data = {"password": "newpassword123"}

    updated_user = UserService.update_user(db, test_user.id, update_data)

    assert updated_user.hashed_password != old_hashed
    assert PasswordService.verify_password("newpassword123", updated_user.hashed_password)


def test_update_user_enforces_email_uniqueness(db: DBSession, test_user: User):
    """Test update_user enforces email uniqueness."""
    # Create another user
    other_user = User(
        email="other@example.com",
        full_name="Other User",
        hashed_password=PasswordService.hash_password("password")
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Try to update test_user's email to other_user's email
    update_data = {"email": "other@example.com"}

    with pytest.raises(ValueError, match="Email already exists"):
        UserService.update_user(db, test_user.id, update_data)
