"""Tests for authentication routes."""

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


def test_register_with_valid_data(client: TestClient):
    """Test POST /api/auth/register with valid data returns 201."""
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "New User",
            "email": "new@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "session_token" in data
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["full_name"] == "New User"
    assert "hashed_password" not in data["user"]


def test_register_with_duplicate_email(client: TestClient, db: DBSession):
    """Test POST /api/auth/register with duplicate email returns 409."""
    # Register first user
    AuthService.register(
        db,
        full_name="First User",
        email="duplicate@example.com",
        password="password1"
    )

    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Second User",
            "email": "duplicate@example.com",
            "password": "password2"
        }
    )

    assert response.status_code == 409


def test_login_with_valid_credentials(client: TestClient, db: DBSession):
    """Test POST /api/auth/login with valid credentials returns 200."""
    # Register user first
    AuthService.register(
        db,
        full_name="Login User",
        email="login@example.com",
        password="correctpass"
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "correctpass"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "session_token" in data
    assert data["user"]["email"] == "login@example.com"


def test_login_with_invalid_credentials(client: TestClient, db: DBSession):
    """Test POST /api/auth/login with invalid credentials returns 401."""
    # Register user
    AuthService.register(
        db,
        full_name="User",
        email="user@example.com",
        password="correctpass"
    )

    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_logout_with_valid_session(client: TestClient, db: DBSession):
    """Test POST /api/auth/logout with valid session returns 200."""
    # Register and get session token
    user, session = AuthService.register(
        db,
        full_name="Logout User",
        email="logout@example.com",
        password="password"
    )

    # Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {session.session_token}"}
    )

    assert response.status_code == 200
    assert "message" in response.json()


def test_logout_with_invalid_session(client: TestClient):
    """Test POST /api/auth/logout with invalid session returns 401."""
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
