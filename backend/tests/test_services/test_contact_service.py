"""Tests for ContactService."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Contact, User
from app.schemas.contact import ContactCreateSchema, ContactUpdateSchema
from app.services.contact_service import ContactService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


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
def other_user(db_session):
    """Create another test user for isolation testing."""
    user = User(
        email="other@example.com",
        full_name="Other User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_create_contact(db_session, test_user):
    """Test creating a contact."""
    contact_data = ContactCreateSchema(
        name="John Doe",
        email="john@example.com",
        company="Acme Corp"
    )

    contact = ContactService.create_contact(db_session, test_user.id, contact_data)

    assert contact.id is not None
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.company == "Acme Corp"
    assert contact.user_id == test_user.id
    assert contact.pipeline_stage == "Lead"


def test_get_contact_by_id(db_session, test_user):
    """Test getting a contact by ID."""
    contact = Contact(
        name="Jane Smith",
        email="jane@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    retrieved = ContactService.get_contact_by_id(db_session, contact.id, test_user.id)

    assert retrieved is not None
    assert retrieved.id == contact.id
    assert retrieved.name == "Jane Smith"


def test_get_contact_by_id_returns_none_for_other_user(db_session, test_user, other_user):
    """Test that get_contact_by_id returns None for contacts owned by other users."""
    contact = Contact(
        name="Private Contact",
        email="private@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Other user tries to access the contact
    retrieved = ContactService.get_contact_by_id(db_session, contact.id, other_user.id)

    assert retrieved is None


def test_get_contacts_for_user_with_search(db_session, test_user):
    """Test searching contacts by name, email, or company."""
    # Create contacts
    contacts = [
        Contact(name="Alice Anderson", email="alice@example.com", company="Alpha Corp", user_id=test_user.id),
        Contact(name="Bob Brown", email="bob@beta.com", company="Beta Inc", user_id=test_user.id),
        Contact(name="Charlie Chen", email="charlie@gamma.com", company="Gamma LLC", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Search by name
    result, total = ContactService.get_contacts_for_user(db_session, test_user.id, search="alice")
    assert total == 1
    assert result[0].name == "Alice Anderson"

    # Search by email
    result, total = ContactService.get_contacts_for_user(db_session, test_user.id, search="beta")
    assert total == 1
    assert result[0].email == "bob@beta.com"

    # Search by company
    result, total = ContactService.get_contacts_for_user(db_session, test_user.id, search="gamma")
    assert total == 1
    assert result[0].company == "Gamma LLC"


def test_get_contacts_for_user_with_filter(db_session, test_user):
    """Test filtering contacts by pipeline stage."""
    contacts = [
        Contact(name="Lead 1", email="lead1@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="Lead 2", email="lead2@example.com", pipeline_stage="Lead", user_id=test_user.id),
        Contact(name="Client 1", email="client1@example.com", pipeline_stage="Client", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Filter by Lead
    result, total = ContactService.get_contacts_for_user(db_session, test_user.id, stage="Lead")
    assert total == 2

    # Filter by Client
    result, total = ContactService.get_contacts_for_user(db_session, test_user.id, stage="Client")
    assert total == 1


def test_update_contact(db_session, test_user):
    """Test updating a contact."""
    contact = Contact(
        name="Original Name",
        email="original@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    update_data = ContactUpdateSchema(
        name="Updated Name",
        company="New Company"
    )

    updated = ContactService.update_contact(db_session, contact.id, test_user.id, update_data)

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.company == "New Company"
    assert updated.email == "original@example.com"  # Unchanged


def test_delete_contact(db_session, test_user):
    """Test deleting a contact."""
    contact = Contact(
        name="To Delete",
        email="delete@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()
    contact_id = contact.id

    result = ContactService.delete_contact(db_session, contact_id, test_user.id)

    assert result is True

    # Verify contact is deleted
    deleted = db_session.query(Contact).filter(Contact.id == contact_id).first()
    assert deleted is None
