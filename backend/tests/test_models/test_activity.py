"""Tests for Activity and Attachment models."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Attachment, Base, Contact, User


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


def test_activity_creation_with_valid_type(db_session, test_contact):
    """Test creating an activity with a valid type."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Follow-up call",
        notes="Discussed project requirements",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    assert activity.id is not None
    assert activity.type == "Call"
    assert activity.subject == "Follow-up call"
    assert activity.contact_id == test_contact.id


def test_activity_contact_relationship(db_session, test_contact):
    """Test activity belongs to contact relationship."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Meeting",
        subject="Project kickoff",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    # Test relationship
    assert activity.contact == test_contact
    assert activity in test_contact.activities


def test_contact_cascade_deletes_activities(db_session, test_contact):
    """Test that deleting a contact cascades to delete activities."""
    # Create multiple activities
    activity1 = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Call 1",
        activity_date=datetime.utcnow()
    )
    activity2 = Activity(
        contact_id=test_contact.id,
        type="Email",
        subject="Email 1",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity1)
    db_session.add(activity2)
    db_session.commit()

    contact_id = test_contact.id

    # Verify activities exist
    activities = db_session.query(Activity).filter(Activity.contact_id == contact_id).all()
    assert len(activities) == 2

    # Delete contact
    db_session.delete(test_contact)
    db_session.commit()

    # Verify activities were cascade deleted
    activities = db_session.query(Activity).filter(Activity.contact_id == contact_id).all()
    assert len(activities) == 0


def test_attachment_creation_with_metadata(db_session, test_contact):
    """Test creating an attachment with file metadata."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="Documentation",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    attachment = Attachment(
        activity_id=activity.id,
        original_filename="document.pdf",
        stored_filename="abc123-document.pdf",
        file_path="/uploads/activities/1/abc123-document.pdf",
        file_size=1024000,
        mime_type="application/pdf"
    )
    db_session.add(attachment)
    db_session.commit()

    assert attachment.id is not None
    assert attachment.original_filename == "document.pdf"
    assert attachment.file_size == 1024000
    assert attachment.activity_id == activity.id


def test_activity_cascade_deletes_attachments(db_session, test_contact):
    """Test that deleting an activity cascades to delete attachments."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Email",
        subject="Contract",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    # Create multiple attachments
    attachment1 = Attachment(
        activity_id=activity.id,
        original_filename="contract.pdf",
        stored_filename="uuid1-contract.pdf",
        file_path="/uploads/1/uuid1-contract.pdf",
        file_size=500000,
        mime_type="application/pdf"
    )
    attachment2 = Attachment(
        activity_id=activity.id,
        original_filename="terms.docx",
        stored_filename="uuid2-terms.docx",
        file_path="/uploads/1/uuid2-terms.docx",
        file_size=200000,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    db_session.add(attachment1)
    db_session.add(attachment2)
    db_session.commit()

    activity_id = activity.id

    # Verify attachments exist
    attachments = db_session.query(Attachment).filter(Attachment.activity_id == activity_id).all()
    assert len(attachments) == 2

    # Delete activity
    db_session.delete(activity)
    db_session.commit()

    # Verify attachments were cascade deleted
    attachments = db_session.query(Attachment).filter(Attachment.activity_id == activity_id).all()
    assert len(attachments) == 0


def test_activity_attachment_relationship(db_session, test_contact):
    """Test bidirectional relationship between activity and attachments."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Meeting",
        subject="Presentation",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    attachment = Attachment(
        activity_id=activity.id,
        original_filename="slides.pptx",
        stored_filename="uuid-slides.pptx",
        file_path="/uploads/1/uuid-slides.pptx",
        file_size=3000000,
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    db_session.add(attachment)
    db_session.commit()

    # Test relationship
    assert attachment.activity == activity
    assert attachment in activity.attachments


def test_activity_all_types(db_session, test_contact):
    """Test creating activities with all four valid types."""
    types = ["Call", "Meeting", "Email", "Note"]

    for activity_type in types:
        activity = Activity(
            contact_id=test_contact.id,
            type=activity_type,
            subject=f"Test {activity_type}",
            activity_date=datetime.utcnow()
        )
        db_session.add(activity)

    db_session.commit()

    # Verify all activities were created
    activities = db_session.query(Activity).filter(Activity.contact_id == test_contact.id).all()
    assert len(activities) == 4

    created_types = [a.type for a in activities]
    for activity_type in types:
        assert activity_type in created_types
