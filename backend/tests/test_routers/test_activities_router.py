"""Tests for activities router."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Activity, Contact, Session, User


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use file::memory:?cache=shared for in-memory database shared across threads
    engine = create_engine(
        "sqlite:///file::memory:?cache=shared&uri=true",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()


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
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_session(db_session, test_user):
    """Create a test session."""
    session = Session(
        session_token="test_token_123",
        user_id=test_user.id,
        expires_at=datetime(2099, 12, 31)
    )
    db_session.add(session)
    db_session.commit()
    return session


@pytest.fixture
def test_contact(db_session, test_user):
    """Create a test contact."""
    contact = Contact(
        name="John Doe",
        email="john@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()
    return contact


def test_create_activity_success(client, test_session, test_contact):
    """Test creating an activity via API."""
    response = client.post(
        f"/api/contacts/{test_contact.id}/activities",
        json={
            "type": "Call",
            "subject": "Follow-up call",
            "notes": "Discussed project",
            "activity_date": "2025-11-18T10:00:00"
        },
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "Call"
    assert data["subject"] == "Follow-up call"


def test_list_contact_activities(client, db_session, test_session, test_contact):
    """Test listing activities for a contact."""
    # Create test activities
    db_session.add_all([
        Activity(
            contact_id=test_contact.id,
            type="Call",
            subject="Activity 1",
            activity_date=datetime.utcnow()
        ),
        Activity(
            contact_id=test_contact.id,
            type="Email",
            subject="Activity 2",
            activity_date=datetime.utcnow()
        )
    ])
    db_session.commit()

    response = client.get(
        f"/api/contacts/{test_contact.id}/activities",
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["activities"]) == 2


def test_get_activity_by_id(client, db_session, test_session, test_contact):
    """Test getting a single activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Meeting",
        subject="Project kickoff",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    response = client.get(
        f"/api/activities/{activity.id}",
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == activity.id
    assert data["subject"] == "Project kickoff"


def test_update_activity(client, db_session, test_session, test_contact):
    """Test updating an activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="Original subject",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    response = client.put(
        f"/api/activities/{activity.id}",
        json={"subject": "Updated subject"},
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Updated subject"


def test_delete_activity(client, db_session, test_session, test_contact):
    """Test deleting an activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="To be deleted",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    response = client.delete(
        f"/api/activities/{activity.id}",
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 204

    # Verify activity was deleted
    deleted = db_session.query(Activity).filter(Activity.id == activity.id).first()
    assert deleted is None


def test_list_all_activities_with_filter(client, db_session, test_session, test_contact):
    """Test listing all activities with type filter."""
    db_session.add_all([
        Activity(
            contact_id=test_contact.id,
            type="Call",
            subject="Call 1",
            activity_date=datetime.utcnow()
        ),
        Activity(
            contact_id=test_contact.id,
            type="Email",
            subject="Email 1",
            activity_date=datetime.utcnow()
        )
    ])
    db_session.commit()

    response = client.get(
        "/api/activities?type=Call",
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "Call"


def test_unauthorized_access(client):
    """Test accessing activity endpoints without authentication."""
    response = client.get("/api/activities")
    assert response.status_code == 401
