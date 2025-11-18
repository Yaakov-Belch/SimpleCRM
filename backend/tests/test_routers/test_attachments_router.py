"""Tests for attachments router."""

from datetime import datetime
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Activity, Attachment, Contact, Session, User


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


@pytest.fixture
def test_activity(db_session, test_contact):
    """Create a test activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="Test activity",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()
    return activity


def test_upload_attachment(client, test_session, test_activity):
    """Test uploading a file attachment."""
    file_content = b"Test file content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

    response = client.post(
        f"/api/activities/{test_activity.id}/attachments",
        files=files,
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test.txt"
    assert data["file_size"] == len(file_content)


def test_delete_attachment(client, db_session, test_session, test_activity):
    """Test deleting an attachment."""
    attachment = Attachment(
        activity_id=test_activity.id,
        original_filename="test.txt",
        stored_filename="uuid-test.txt",
        file_path="/tmp/test.txt",  # Non-existent file
        file_size=100
    )
    db_session.add(attachment)
    db_session.commit()

    response = client.delete(
        f"/api/activities/{test_activity.id}/attachments/{attachment.id}",
        headers={"Authorization": f"Bearer {test_session.session_token}"}
    )

    assert response.status_code == 204


def test_upload_without_authentication(client, test_activity):
    """Test uploading without authentication."""
    files = {"file": ("test.txt", BytesIO(b"content"), "text/plain")}
    response = client.post(
        f"/api/activities/{test_activity.id}/attachments",
        files=files
    )
    assert response.status_code == 401
