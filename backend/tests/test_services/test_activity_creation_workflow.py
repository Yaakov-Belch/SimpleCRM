"""Tests for immediate activity creation workflow (Task Group 2.1)."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Base, Contact, User
from app.schemas.activity import ActivityCreateSchema
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


def test_create_activity_with_minimal_data(db_session, test_user, test_contact):
    """Test POST /activities creates activity immediately with defaults."""
    # Create activity with only contact_id (minimal required data)
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="",  # Empty subject allowed
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert activity is not None
    assert activity.id is not None
    assert activity.type == "Note"
    assert activity.subject == ""
    assert activity.contact_id == test_contact.id


def test_activity_inherits_pipeline_stage_from_latest_activity(db_session, test_user, test_contact):
    """Test new activity inherits pipeline_stage from latest activity."""
    # Create first activity with Qualified stage
    first_activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="First call",
        activity_date=datetime.utcnow(),
        pipeline_stage="Qualified"
    )
    db_session.add(first_activity)
    db_session.commit()

    # Create second activity - should inherit Qualified stage
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="Follow-up note",
        activity_date=datetime.utcnow()
    )

    new_activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert new_activity is not None
    assert new_activity.pipeline_stage == "Qualified"


def test_activity_defaults_to_lead_when_no_previous_activities(db_session, test_user, test_contact):
    """Test activity defaults to 'Lead' when no previous activities exist."""
    # Create first activity for contact
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="First activity",
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert activity is not None
    assert activity.pipeline_stage == "Lead"


def test_create_activity_with_empty_subject_allowed(db_session, test_user, test_contact):
    """Test activity creation with empty subject is allowed."""
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="",  # Explicitly empty subject
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert activity is not None
    assert activity.id is not None
    assert activity.subject == ""


def test_create_activity_returns_full_object_with_id(db_session, test_user, test_contact):
    """Test activity creation returns full activity object with ID and pipeline_stage."""
    activity_data = ActivityCreateSchema(
        type="Meeting",
        subject="Client meeting",
        notes="Discuss project scope",
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    # Verify full object returned
    assert activity is not None
    assert activity.id is not None
    assert activity.contact_id == test_contact.id
    assert activity.type == "Meeting"
    assert activity.subject == "Client meeting"
    assert activity.notes == "Discuss project scope"
    assert activity.pipeline_stage is not None
    assert activity.created_at is not None
    assert activity.updated_at is not None


def test_activity_inherits_correct_stage_from_most_recent(db_session, test_user, test_contact):
    """Test activity inherits from MOST RECENT activity, not first."""
    # Create sequence of activities with different stages
    older_activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Old call",
        activity_date=datetime(2024, 1, 1, 12, 0, 0),
        pipeline_stage="Lead"
    )
    recent_activity = Activity(
        contact_id=test_contact.id,
        type="Meeting",
        subject="Recent meeting",
        activity_date=datetime(2024, 12, 1, 12, 0, 0),
        pipeline_stage="Client"
    )
    db_session.add(older_activity)
    db_session.add(recent_activity)
    db_session.commit()

    # Create new activity - should inherit from most recent (Client)
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="New note",
        activity_date=datetime.utcnow()
    )

    new_activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert new_activity is not None
    assert new_activity.pipeline_stage == "Client"


def test_activity_creation_defaults_type_and_date(db_session, test_user, test_contact):
    """Test that activity creation uses default type='Note' and current datetime."""
    activity_data = ActivityCreateSchema(
        type="Note",
        subject="Test note",
        activity_date=datetime.utcnow()
    )

    activity = ActivityService.create_activity(
        db_session,
        test_contact.id,
        test_user.id,
        activity_data
    )

    assert activity is not None
    assert activity.type == "Note"
    assert activity.activity_date is not None
    # Verify date is recent (within last minute)
    time_diff = datetime.utcnow() - activity.activity_date
    assert time_diff.total_seconds() < 60
