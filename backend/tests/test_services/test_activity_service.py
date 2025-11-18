"""Tests for ActivityService."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Base, Contact, User
from app.schemas.activity import ActivityCreateSchema, ActivityUpdateSchema
from app.services.activity_service import ActivityService


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


def test_create_activity_success(db_session, test_user, test_contact):
    """Test creating an activity for owned contact."""
    activity_data = ActivityCreateSchema(
        type="Call",
        subject="Follow-up call",
        notes="Discussed project requirements",
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert activity is not None
    assert activity.type == "Call"
    assert activity.subject == "Follow-up call"
    assert activity.contact_id == test_contact.id


def test_create_activity_unauthorized(db_session, test_contact):
    """Test creating activity for contact not owned by user."""
    activity_data = ActivityCreateSchema(
        type="Call",
        subject="Test",
        activity_date=datetime.utcnow()
    )

    # Try to create activity with wrong user_id
    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        99999,  # Non-existent user
        activity_data
    )

    assert activity is None


def test_get_activities_for_contact(db_session, test_user, test_contact):
    """Test getting activities for a contact."""
    # Create multiple activities
    for i in range(3):
        activity = Activity(
            contact_id=test_contact.id,
            type="Call",
            subject=f"Activity {i}",
            activity_date=datetime.utcnow()
        )
        db_session.add(activity)
    db_session.commit()

    activities = ActivityService.get_activities_for_contact(
        db_session,
        test_contact.id,
        test_user.id
    )

    assert activities is not None
    assert len(activities) == 3


def test_get_all_activities_with_filter(db_session, test_user, test_contact):
    """Test getting all activities with type filter."""
    # Create activities of different types
    db_session.add_all([
        Activity(
            contact_id=test_contact.id,
            type="Call",
            subject="Call 1",
            activity_date=datetime.utcnow()
        ),
        Activity(
            contact_id=test_contact.id,
            type="Call",
            subject="Call 2",
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

    # Get only Call activities
    activities = ActivityService.get_all_activities_for_user(
        db_session,
        test_user.id,
        activity_type="Call"
    )

    assert len(activities) == 2
    assert all(a.type == "Call" for a in activities)


def test_update_activity(db_session, test_user, test_contact):
    """Test updating an activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Original subject",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    update_data = ActivityUpdateSchema(
        subject="Updated subject"
    )

    updated = ActivityService.update_activity(
        db_session,
        activity.id,
        test_user.id,
        update_data
    )

    assert updated is not None
    assert updated.subject == "Updated subject"
    assert updated.type == "Call"  # Unchanged


def test_delete_activity(db_session, test_user, test_contact):
    """Test deleting an activity."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="To be deleted",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    activity_id = activity.id

    # Delete activity
    result = ActivityService.delete_activity(
        db_session,
        activity_id,
        test_user.id
    )

    assert result is True

    # Verify activity was deleted
    deleted_activity = db_session.query(Activity).filter(Activity.id == activity_id).first()
    assert deleted_activity is None


def test_search_activities(db_session, test_user, test_contact):
    """Test searching activities by content."""
    db_session.add_all([
        Activity(
            contact_id=test_contact.id,
            type="Note",
            subject="Project requirements",
            notes="Important details about the project",
            activity_date=datetime.utcnow()
        ),
        Activity(
            contact_id=test_contact.id,
            type="Call",
            subject="Random call",
            notes="Nothing important",
            activity_date=datetime.utcnow()
        )
    ])
    db_session.commit()

    # Search for "project"
    activities = ActivityService.get_all_activities_for_user(
        db_session,
        test_user.id,
        search="project"
    )

    assert len(activities) == 1
    assert "requirements" in activities[0].subject
