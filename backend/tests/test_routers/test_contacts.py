"""Tests for Contact API endpoints."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Contact, Session, User  # Import all models to register them
from app.services.password_service import PasswordService
from app.services.session_service import SessionService


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session using a temp file."""
    # Create a temporary database file
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


def test_create_contact_success(client, auth_headers):
    """Test creating a contact successfully."""
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Acme Corp",
        "pipeline_stage": "Lead"
    }

    response = client.post("/api/contacts", json=data, headers=auth_headers)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["name"] == "John Doe"
    assert json_data["email"] == "john@example.com"
    assert json_data["company"] == "Acme Corp"
    assert json_data["id"] is not None


def test_create_contact_requires_authentication(client):
    """Test that creating a contact requires authentication."""
    data = {
        "name": "John Doe",
        "email": "john@example.com"
    }

    response = client.post("/api/contacts", json=data)

    assert response.status_code == 401


def test_get_contacts_list(client, db_session, test_user, auth_headers):
    """Test getting list of contacts."""
    # Create test contacts
    contacts = [
        Contact(name="Contact 1", email="contact1@example.com", user_id=test_user.id),
        Contact(name="Contact 2", email="contact2@example.com", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    response = client.get("/api/contacts", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 2
    assert len(json_data["contacts"]) == 2


def test_get_contacts_with_search(client, db_session, test_user, auth_headers):
    """Test getting contacts with search parameter."""
    contacts = [
        Contact(name="Alice Anderson", email="alice@example.com", user_id=test_user.id),
        Contact(name="Bob Brown", email="bob@example.com", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    response = client.get("/api/contacts?search=alice", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 1
    assert json_data["contacts"][0]["name"] == "Alice Anderson"


def test_get_contact_by_id(client, db_session, test_user, auth_headers):
    """Test getting a single contact by ID."""
    contact = Contact(
        name="Jane Smith",
        email="jane@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    response = client.get(f"/api/contacts/{contact.id}", headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Jane Smith"
    assert json_data["id"] == contact.id


def test_get_contact_not_found(client, auth_headers):
    """Test getting a non-existent contact returns 404."""
    response = client.get("/api/contacts/99999", headers=auth_headers)

    assert response.status_code == 404


def test_update_contact(client, db_session, test_user, auth_headers):
    """Test updating a contact."""
    contact = Contact(
        name="Original Name",
        email="original@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    update_data = {
        "name": "Updated Name",
        "company": "New Company"
    }

    response = client.put(f"/api/contacts/{contact.id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Updated Name"
    assert json_data["company"] == "New Company"


def test_delete_contact(client, db_session, test_user, auth_headers):
    """Test deleting a contact."""
    contact = Contact(
        name="To Delete",
        email="delete@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()
    contact_id = contact.id

    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    assert response.status_code == 204

    # Verify contact is deleted
    deleted = db_session.query(Contact).filter(Contact.id == contact_id).first()
    assert deleted is None
