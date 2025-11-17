"""Tests for AuthService."""

import pytest
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.password_service import PasswordService


@pytest.fixture
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_register_creates_user_and_session(db: DBSession):
    """Test register creates both user and session."""
    user, session = AuthService.register(
        db,
        full_name="New User",
        email="new@example.com",
        password="password123"
    )

    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.full_name == "New User"
    assert session.user_id == user.id
    assert session.session_token is not None


def test_register_hashes_password(db: DBSession):
    """Test register hashes the password."""
    user, session = AuthService.register(
        db,
        full_name="Test User",
        email="test@example.com",
        password="mypassword"
    )

    assert user.hashed_password != "mypassword"
    assert PasswordService.verify_password("mypassword", user.hashed_password)


def test_register_rejects_duplicate_email(db: DBSession):
    """Test register rejects duplicate email."""
    # Create first user
    AuthService.register(
        db,
        full_name="First User",
        email="duplicate@example.com",
        password="password1"
    )

    # Try to register with same email
    with pytest.raises(ValueError, match="Email already exists"):
        AuthService.register(
            db,
            full_name="Second User",
            email="duplicate@example.com",
            password="password2"
        )


def test_login_with_valid_credentials(db: DBSession):
    """Test login succeeds with valid credentials."""
    # Register user first
    registered_user, _ = AuthService.register(
        db,
        full_name="Login User",
        email="login@example.com",
        password="correctpass"
    )

    # Login with correct credentials
    result = AuthService.login(db, "login@example.com", "correctpass")

    assert result is not None
    user, session = result
    assert user.id == registered_user.id
    assert session.user_id == user.id


def test_login_is_case_insensitive(db: DBSession):
    """Test login is case-insensitive for email."""
    # Register user
    registered_user, _ = AuthService.register(
        db,
        full_name="Case Test",
        email="case@example.com",
        password="password123"
    )

    # Login with different case
    result = AuthService.login(db, "CASE@EXAMPLE.COM", "password123")

    assert result is not None
    user, session = result
    assert user.id == registered_user.id


def test_login_with_invalid_credentials(db: DBSession):
    """Test login fails with invalid credentials."""
    # Register user
    AuthService.register(
        db,
        full_name="User",
        email="user@example.com",
        password="correctpass"
    )

    # Try to login with wrong password
    result = AuthService.login(db, "user@example.com", "wrongpass")

    assert result is None


def test_logout_deletes_session(db: DBSession):
    """Test logout deletes the session."""
    # Register and get session token
    user, session = AuthService.register(
        db,
        full_name="Logout User",
        email="logout@example.com",
        password="password"
    )
    token = session.session_token

    # Logout
    result = AuthService.logout(db, token)

    assert result is True

    # Verify session is deleted
    from app.services.session_service import SessionService
    validated = SessionService.validate_session(db, token)
    assert validated is None
