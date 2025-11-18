"""Tests for Contact model."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models import Base, Contact, User


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
        hashed_password="hashed_password_here"
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_contact_creation_with_required_fields(db_session, test_user):
    """Test creating a contact with only required fields."""
    contact = Contact(
        name="John Doe",
        email="john@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    assert contact.id is not None
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.user_id == test_user.id
    assert contact.pipeline_stage == "Lead"  # Default value
    assert contact.created_at is not None
    assert contact.updated_at is not None


def test_contact_creation_with_all_fields(db_session, test_user):
    """Test creating a contact with all fields."""
    contact = Contact(
        name="Jane Smith",
        email="jane@example.com",
        phone="+1234567890",
        company="Acme Corp",
        job_title="CEO",
        website="https://example.com",
        notes="Important client",
        pipeline_stage="Client",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    assert contact.id is not None
    assert contact.name == "Jane Smith"
    assert contact.email == "jane@example.com"
    assert contact.phone == "+1234567890"
    assert contact.company == "Acme Corp"
    assert contact.job_title == "CEO"
    assert contact.website == "https://example.com"
    assert contact.notes == "Important client"
    assert contact.pipeline_stage == "Client"


def test_contact_name_required_constraint(db_session, test_user):
    """Test that name is required."""
    contact = Contact(
        email="test@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_contact_email_required_constraint(db_session, test_user):
    """Test that email is required."""
    contact = Contact(
        name="Test User",
        user_id=test_user.id
    )
    db_session.add(contact)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_contact_user_relationship(db_session, test_user):
    """Test the relationship between Contact and User."""
    contact = Contact(
        name="Test Contact",
        email="contact@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Test contact.user relationship
    assert contact.user == test_user

    # Test user.contacts relationship
    assert len(test_user.contacts) == 1
    assert test_user.contacts[0] == contact


def test_contact_cascade_delete_on_user_deletion(db_session, test_user):
    """Test that deleting a user cascades to delete contacts."""
    contact1 = Contact(
        name="Contact 1",
        email="contact1@example.com",
        user_id=test_user.id
    )
    contact2 = Contact(
        name="Contact 2",
        email="contact2@example.com",
        user_id=test_user.id
    )
    db_session.add(contact1)
    db_session.add(contact2)
    db_session.commit()

    user_id = test_user.id

    # Verify contacts exist
    contacts = db_session.query(Contact).filter(Contact.user_id == user_id).all()
    assert len(contacts) == 2

    # Delete user
    db_session.delete(test_user)
    db_session.commit()

    # Verify contacts were cascade deleted
    contacts = db_session.query(Contact).filter(Contact.user_id == user_id).all()
    assert len(contacts) == 0


def test_contact_pipeline_stage_enum_values(db_session, test_user):
    """Test pipeline stage accepts valid enum values."""
    stages = ["Lead", "Qualified", "Proposal", "Client"]

    for stage in stages:
        contact = Contact(
            name=f"Contact {stage}",
            email=f"{stage.lower()}@example.com",
            pipeline_stage=stage,
            user_id=test_user.id
        )
        db_session.add(contact)
        db_session.commit()

        assert contact.pipeline_stage == stage
