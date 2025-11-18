"""Tests for pipeline statistics API endpoints."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Contact, Session, User
from app.services.password_service import PasswordService
from app.services.session_service import SessionService


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session using a temp file."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=PasswordService.hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(db_session, test_user):
    """Create authentication headers with valid session token."""
    session = SessionService.create_session(db_session, test_user.id)
    return {"Authorization": f"Bearer {session.session_token}"}


def test_get_pipeline_stats_empty(client, auth_headers):
    """Test getting pipeline stats when no contacts exist."""
    response = client.get("/api/contacts/pipeline-stats", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["active_stages"]["Lead"] == 0
    assert json_data["active_stages"]["Qualified"] == 0
    assert json_data["active_stages"]["Proposal"] == 0
    assert json_data["active_stages"]["Client"] == 0
    assert json_data["active_count"] == 0
    assert json_data["passive_count"] == 0


def test_get_pipeline_stats_with_contacts(client, db_session, test_user, auth_headers):
    """Test getting pipeline stats with various contacts."""
    from datetime import datetime
    from app.models import Activity

    # Create contacts in different stages
    contacts = [
        Contact(name="Lead 1", email="lead1@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="Lead 2", email="lead2@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="Lead 3", email="lead3@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="Qualified 1", email="qual1@example.com", pipeline_stage="Qualified", user_id=test_user.id),
        Contact(name="Qualified 2", email="qual2@example.com", pipeline_stage="Qualified", user_id=test_user.id),
        Contact(name="Proposal 1", email="prop1@example.com", pipeline_stage="Proposal", user_id=test_user.id),
        Contact(name="Client 1", email="client1@example.com", pipeline_stage="Client", user_id=test_user.id),
        Contact(name="Client 2", email="client2@example.com", pipeline_stage="Client", user_id=test_user.id),
        Contact(name="Client 3", email="client3@example.com", pipeline_stage="Client", user_id=test_user.id),
        Contact(name="Client 4", email="client4@example.com", pipeline_stage="Client", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Create activities to set the pipeline stages (contacts derive stage from latest activity)
    for contact in contacts:
        activity = Activity(
            contact_id=contact.id,
            type="Note",
            subject=f"Activity for {contact.name}",
            pipeline_stage=contact.pipeline_stage,
            activity_date=datetime.utcnow()
        )
        db_session.add(activity)
    db_session.commit()

    response = client.get("/api/contacts/pipeline-stats", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["active_stages"]["Lead"] == 3
    assert json_data["active_stages"]["Qualified"] == 2
    assert json_data["active_stages"]["Proposal"] == 1
    assert json_data["active_stages"]["Client"] == 4
    assert json_data["active_count"] == 10
    assert json_data["passive_count"] == 0


def test_update_contact_pipeline_stage(client, db_session, test_user, auth_headers):
    """Test updating a contact's pipeline stage."""
    contact = Contact(
        name="Test Contact",
        email="test@example.com",
        pipeline_stage="Lead",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Update to Qualified
    update_data = {"pipeline_stage": "Qualified"}
    response = client.put(f"/api/contacts/{contact.id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["pipeline_stage"] == "Qualified"


def test_update_contact_with_invalid_pipeline_stage(client, db_session, test_user, auth_headers):
    """Test that updating with an invalid pipeline stage returns validation error."""
    contact = Contact(
        name="Test Contact",
        email="test@example.com",
        pipeline_stage="Lead",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Try to update with invalid stage
    update_data = {"pipeline_stage": "InvalidStage"}
    response = client.put(f"/api/contacts/{contact.id}", json=update_data, headers=auth_headers)

    # Should return 400 or 422 (both are acceptable for validation errors)
    assert response.status_code in [400, 422]


def test_create_contact_with_pipeline_stage(client, auth_headers):
    """Test creating a contact with a specified pipeline stage."""
    data = {
        "name": "New Contact",
        "email": "new@example.com",
        "pipeline_stage": "Proposal"
    }

    response = client.post("/api/contacts", json=data, headers=auth_headers)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["pipeline_stage"] == "Proposal"


def test_create_contact_defaults_to_lead(client, auth_headers):
    """Test creating a contact without specifying pipeline_stage defaults to Lead."""
    data = {
        "name": "New Contact",
        "email": "new@example.com"
    }

    response = client.post("/api/contacts", json=data, headers=auth_headers)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["pipeline_stage"] == "Lead"


def test_pipeline_stats_user_isolation(client, db_session, test_user, auth_headers):
    """Test that pipeline stats only include current user's contacts."""
    from datetime import datetime
    from app.models import Activity

    # Create another user
    other_user = User(
        email="other@example.com",
        full_name="Other User",
        hashed_password=PasswordService.hash_password("password123")
    )
    db_session.add(other_user)
    db_session.commit()

    # Create contacts for test_user
    test_contacts = [
        Contact(name="User1 Lead", email="u1l@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="User1 Client", email="u1c@example.com", pipeline_stage="Client", user_id=test_user.id),
    ]
    for contact in test_contacts:
        db_session.add(contact)

    # Create contacts for other_user
    other_contacts = [
        Contact(name="User2 Lead", email="u2l@example.com", pipeline_stage="Lead", user_id=other_user.id),
        Contact(name="User2 Qualified", email="u2q@example.com", pipeline_stage="Qualified", user_id=other_user.id),
        Contact(name="User2 Proposal", email="u2p@example.com", pipeline_stage="Proposal", user_id=other_user.id),
    ]
    for contact in other_contacts:
        db_session.add(contact)
    db_session.commit()

    # Create activities to set the pipeline stages for test_user's contacts
    for contact in test_contacts:
        activity = Activity(
            contact_id=contact.id,
            type="Note",
            subject=f"Activity for {contact.name}",
            pipeline_stage=contact.pipeline_stage,
            activity_date=datetime.utcnow()
        )
        db_session.add(activity)

    # Create activities for other_user's contacts too
    for contact in other_contacts:
        activity = Activity(
            contact_id=contact.id,
            type="Note",
            subject=f"Activity for {contact.name}",
            pipeline_stage=contact.pipeline_stage,
            activity_date=datetime.utcnow()
        )
        db_session.add(activity)
    db_session.commit()

    # Get stats for test_user
    response = client.get("/api/contacts/pipeline-stats", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["active_stages"]["Lead"] == 1
    assert json_data["active_stages"]["Qualified"] == 0
    assert json_data["active_stages"]["Proposal"] == 0
    assert json_data["active_stages"]["Client"] == 1
    assert json_data["active_count"] == 2  # Only test_user's contacts
    assert json_data["passive_count"] == 0
