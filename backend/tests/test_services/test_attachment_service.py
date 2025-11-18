"""Tests for AttachmentService."""

from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Attachment, Base, Contact, User
from app.services.attachment_service import AttachmentService


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


def test_save_attachment_metadata(db_session, test_activity):
    """Test saving attachment metadata."""
    attachment = AttachmentService.save_attachment_metadata(
        db_session,
        activity_id=test_activity.id,
        original_filename="document.pdf",
        stored_filename="abc123-document.pdf",
        file_path="/uploads/activities/1/abc123-document.pdf",
        file_size=1024000,
        mime_type="application/pdf"
    )

    assert attachment.id is not None
    assert attachment.original_filename == "document.pdf"
    assert attachment.file_size == 1024000
    assert attachment.activity_id == test_activity.id


def test_get_attachment_by_id(db_session, test_user, test_activity):
    """Test getting attachment by ID with ownership verification."""
    attachment = Attachment(
        activity_id=test_activity.id,
        original_filename="test.txt",
        stored_filename="uuid-test.txt",
        file_path="/uploads/1/uuid-test.txt",
        file_size=100
    )
    db_session.add(attachment)
    db_session.commit()

    retrieved = AttachmentService.get_attachment_by_id(
        db_session,
        attachment.id,
        test_activity.id,
        test_user.id
    )

    assert retrieved is not None
    assert retrieved.id == attachment.id


def test_get_attachment_unauthorized(db_session, test_activity):
    """Test getting attachment with wrong user ID."""
    attachment = Attachment(
        activity_id=test_activity.id,
        original_filename="test.txt",
        stored_filename="uuid-test.txt",
        file_path="/uploads/1/uuid-test.txt",
        file_size=100
    )
    db_session.add(attachment)
    db_session.commit()

    retrieved = AttachmentService.get_attachment_by_id(
        db_session,
        attachment.id,
        test_activity.id,
        99999  # Wrong user_id
    )

    assert retrieved is None


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test unsafe characters
    assert AttachmentService.sanitize_filename("file/with\\slashes.txt") == "file-with-slashes.txt"
    assert AttachmentService.sanitize_filename("file:with*special?.txt") == "file-with-special-.txt"
    assert AttachmentService.sanitize_filename("file<with>pipes|.txt") == "file-with-pipes-.txt"
    assert AttachmentService.sanitize_filename("file with spaces.txt") == "file-with-spaces.txt"

    # Test normal filename
    assert AttachmentService.sanitize_filename("normal-file.pdf") == "normal-file.pdf"


def test_get_upload_directory(tmp_path, monkeypatch):
    """Test getting upload directory path."""
    # Mock the base directory
    monkeypatch.setattr(
        "app.services.attachment_service.Path",
        lambda x: tmp_path if x == "/home/yaakov/git/SimpleCRM/backend/uploads" else Path(x)
    )

    upload_dir = AttachmentService.get_upload_directory(123)

    # Verify path structure
    assert "activities" in str(upload_dir)
    assert "123" in str(upload_dir)


def test_delete_attachment(db_session, test_user, test_activity):
    """Test deleting attachment (database record only, no file)."""
    attachment = Attachment(
        activity_id=test_activity.id,
        original_filename="test.txt",
        stored_filename="uuid-test.txt",
        file_path="/nonexistent/path/file.txt",  # File doesn't exist
        file_size=100
    )
    db_session.add(attachment)
    db_session.commit()

    attachment_id = attachment.id

    result = AttachmentService.delete_attachment(
        db_session,
        attachment_id,
        test_user.id
    )

    assert result is True

    # Verify attachment was deleted from database
    deleted = db_session.query(Attachment).filter(Attachment.id == attachment_id).first()
    assert deleted is None
