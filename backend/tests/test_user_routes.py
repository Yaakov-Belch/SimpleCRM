"""Tests for user profile routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.services.auth_service import AuthService


# Override the database dependency for testing
def override_get_db():
    """Override database dependency for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def db():
    """Create a test database session."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def authenticated_user(db: DBSession):
    """Create an authenticated user with session."""
    user, session = AuthService.register(
        db,
        full_name="Test User",
        email="test@example.com",
        password="password123"
    )
    return user, session


def test_get_users_me_with_valid_session(client: TestClient, authenticated_user):
    """Test GET /api/users/me with valid session returns 200."""
    user, session = authenticated_user

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["full_name"] == user.full_name
    assert "hashed_password" not in data


def test_get_users_me_with_invalid_session(client: TestClient):
    """Test GET /api/users/me with invalid session returns 401."""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_update_users_me_full_name(client: TestClient, authenticated_user):
    """Test PUT /api/users/me updates full_name."""
    user, session = authenticated_user

    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {session.session_token}"},
        json={"full_name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == user.email


def test_update_users_me_email(client: TestClient, authenticated_user):
    """Test PUT /api/users/me updates email."""
    user, session = authenticated_user

    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {session.session_token}"},
        json={"email": "newemail@example.com"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@example.com"
    assert data["full_name"] == user.full_name


def test_update_users_me_with_duplicate_email(client: TestClient, authenticated_user, db: DBSession):
    """Test PUT /api/users/me with duplicate email returns 409."""
    user, session = authenticated_user

    # Create another user
    AuthService.register(
        db,
        full_name="Other User",
        email="other@example.com",
        password="password"
    )

    # Try to update to other user's email
    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {session.session_token}"},
        json={"email": "other@example.com"}
    )

    assert response.status_code == 409


def test_update_users_me_password(client: TestClient, authenticated_user, db: DBSession):
    """Test PUT /api/users/me updates password."""
    user, session = authenticated_user

    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {session.session_token}"},
        json={"password": "newpassword123"}
    )

    assert response.status_code == 200

    # Verify can login with new password
    login_result = AuthService.login(db, user.email, "newpassword123")
    assert login_result is not None


def test_update_users_me_requires_auth(client: TestClient):
    """Test PUT /api/users/me requires authentication."""
    response = client.put(
        "/api/users/me",
        json={"full_name": "New Name"}
    )

    assert response.status_code == 401
