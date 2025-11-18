"""Integration tests for authentication feature end-to-end workflows."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.session import Session
from app.models.user import User


@pytest.fixture
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_complete_registration_autologin_profile_update_flow(client, db: DBSession):
    """Test complete flow: register → auto-login → update profile."""
    # Step 1: Register a new user
    register_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Integration Test User",
            "email": "integration@example.com",
            "password": "testpassword123"
        }
    )

    assert register_response.status_code == 201
    register_data = register_response.json()
    assert "session_token" in register_data
    assert register_data["user"]["email"] == "integration@example.com"
    assert register_data["user"]["full_name"] == "Integration Test User"

    session_token = register_data["session_token"]
    user_id = register_data["user"]["id"]

    # Step 2: Verify user is automatically logged in (can access protected endpoint)
    headers = {"Authorization": f"Bearer {session_token}"}
    me_response = client.get("/api/users/me", headers=headers)

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["id"] == user_id
    assert me_data["email"] == "integration@example.com"

    # Step 3: Update user profile using the session from registration
    update_response = client.put(
        "/api/users/me",
        headers=headers,
        json={
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }
    )

    assert update_response.status_code == 200
    update_data = update_response.json()
    assert update_data["full_name"] == "Updated Name"
    assert update_data["email"] == "updated@example.com"

    # Step 4: Verify changes persisted
    verify_response = client.get("/api/users/me", headers=headers)
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["full_name"] == "Updated Name"
    assert verify_data["email"] == "updated@example.com"


def test_session_expiration_across_endpoints(client, db: DBSession):
    """Test that expired sessions are rejected across all protected endpoints."""
    # Step 1: Create a user and session
    register_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Expiration Test",
            "email": "expire@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201
    session_token = register_response.json()["session_token"]

    # Step 2: Manually expire the session in database
    session = db.query(Session).filter(Session.session_token == session_token).first()
    assert session is not None
    session.expires_at = datetime.utcnow() - timedelta(days=1)
    db.commit()

    # Step 3: Try to access protected endpoints with expired session
    headers = {"Authorization": f"Bearer {session_token}"}

    # Test GET /api/users/me
    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 401

    # Test PUT /api/users/me
    update_response = client.put(
        "/api/users/me",
        headers=headers,
        json={"full_name": "Should Not Work"}
    )
    assert update_response.status_code == 401

    # Test POST /api/auth/logout
    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 401


def test_concurrent_session_management(client, db: DBSession):
    """Test that multiple concurrent sessions work independently."""
    # Step 1: Register a user
    register_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Multi Session User",
            "email": "multisession@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201
    session1_token = register_response.json()["session_token"]
    user_id = register_response.json()["user"]["id"]

    # Step 2: Login again to create a second session
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "multisession@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200
    session2_token = login_response.json()["session_token"]

    # Verify two different sessions were created
    assert session1_token != session2_token

    # Step 3: Verify both sessions work independently
    headers1 = {"Authorization": f"Bearer {session1_token}"}
    headers2 = {"Authorization": f"Bearer {session2_token}"}

    me_response1 = client.get("/api/users/me", headers=headers1)
    me_response2 = client.get("/api/users/me", headers=headers2)

    assert me_response1.status_code == 200
    assert me_response2.status_code == 200
    assert me_response1.json()["id"] == user_id
    assert me_response2.json()["id"] == user_id

    # Step 4: Logout from session1
    logout1_response = client.post("/api/auth/logout", headers=headers1)
    assert logout1_response.status_code == 200

    # Step 5: Verify session1 is invalidated but session2 still works
    me_response1_after = client.get("/api/users/me", headers=headers1)
    me_response2_after = client.get("/api/users/me", headers=headers2)

    assert me_response1_after.status_code == 401  # Session1 should be invalid
    assert me_response2_after.status_code == 200  # Session2 should still work

    # Verify session count in database
    sessions = db.query(Session).filter(Session.user_id == user_id).all()
    assert len(sessions) == 1  # Only session2 should remain


def test_login_password_update_relogin_flow(client, db: DBSession):
    """Test flow: register → login → update password → logout → login with new password."""
    # Step 1: Register a user
    register_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Password Change User",
            "email": "pwchange@example.com",
            "password": "oldpassword123"
        }
    )

    assert register_response.status_code == 201
    session_token = register_response.json()["session_token"]

    # Step 2: Update password
    headers = {"Authorization": f"Bearer {session_token}"}
    update_response = client.put(
        "/api/users/me",
        headers=headers,
        json={"password": "newpassword456"}
    )

    assert update_response.status_code == 200

    # Step 3: Logout
    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    # Step 4: Try to login with old password (should fail)
    old_login_response = client.post(
        "/api/auth/login",
        json={
            "email": "pwchange@example.com",
            "password": "oldpassword123"
        }
    )

    assert old_login_response.status_code == 401

    # Step 5: Login with new password (should succeed)
    new_login_response = client.post(
        "/api/auth/login",
        json={
            "email": "pwchange@example.com",
            "password": "newpassword456"
        }
    )

    assert new_login_response.status_code == 200
    assert "session_token" in new_login_response.json()

    # Step 6: Verify can access protected endpoint with new session
    new_headers = {"Authorization": f"Bearer {new_login_response.json()['session_token']}"}
    me_response = client.get("/api/users/me", headers=new_headers)

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "pwchange@example.com"


def test_email_uniqueness_across_users(client, db: DBSession):
    """Test that email uniqueness is enforced when updating profile."""
    # Step 1: Register first user
    register1_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "User One",
            "email": "user1@example.com",
            "password": "password123"
        }
    )

    assert register1_response.status_code == 201

    # Step 2: Register second user
    register2_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "User Two",
            "email": "user2@example.com",
            "password": "password123"
        }
    )

    assert register2_response.status_code == 201
    session2_token = register2_response.json()["session_token"]

    # Step 3: Try to update user2's email to user1's email
    headers = {"Authorization": f"Bearer {session2_token}"}
    update_response = client.put(
        "/api/users/me",
        headers=headers,
        json={"email": "user1@example.com"}
    )

    # Should get conflict error
    assert update_response.status_code == 409

    # Step 4: Verify user2's email didn't change
    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user2@example.com"
