"""Tests for Activity model pipeline_stage functionality."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Base, Contact, User


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


def test_activity_creation_with_default_pipeline_stage(db_session, test_contact):
    """Test activity creation with default pipeline_stage='Lead'."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="First activity",
        activity_date=datetime.utcnow()
    )
    db_session.add(activity)
    db_session.commit()

    assert activity.id is not None
    assert activity.pipeline_stage == "Lead"


def test_activity_creation_with_explicit_pipeline_stage(db_session, test_contact):
    """Test activity creation with explicit pipeline_stage value."""
    activity = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Qualified call",
        activity_date=datetime.utcnow(),
        pipeline_stage="Qualified"
    )
    db_session.add(activity)
    db_session.commit()

    assert activity.id is not None
    assert activity.pipeline_stage == "Qualified"


def test_activity_with_all_active_pipeline_stages(db_session, test_contact):
    """Test activities can be created with all active pipeline stages."""
    active_stages = ["Lead", "Qualified", "Proposal", "Client"]

    for stage in active_stages:
        activity = Activity(
            contact_id=test_contact.id,
            type="Note",
            subject=f"Activity at {stage}",
            activity_date=datetime.utcnow(),
            pipeline_stage=stage
        )
        db_session.add(activity)

    db_session.commit()

    # Verify all activities were created with correct stages
    activities = db_session.query(Activity).filter(Activity.contact_id == test_contact.id).all()
    assert len(activities) == 4

    created_stages = [a.pipeline_stage for a in activities]
    for stage in active_stages:
        assert stage in created_stages


def test_activity_with_all_passive_pipeline_stages(db_session, test_contact):
    """Test activities can be created with all passive pipeline stages."""
    passive_stages = ["Qualified Out", "Lost Proposal", "Work Completed", "Archived"]

    for stage in passive_stages:
        activity = Activity(
            contact_id=test_contact.id,
            type="Note",
            subject=f"Activity at {stage}",
            activity_date=datetime.utcnow(),
            pipeline_stage=stage
        )
        db_session.add(activity)

    db_session.commit()

    # Verify all activities were created with correct stages
    activities = db_session.query(Activity).filter(Activity.contact_id == test_contact.id).all()
    assert len(activities) == 4

    created_stages = [a.pipeline_stage for a in activities]
    for stage in passive_stages:
        assert stage in created_stages


def test_activity_pipeline_stage_queryable(db_session, test_contact):
    """Test activities can be queried by pipeline_stage."""
    # Create activities with different stages
    activity1 = Activity(
        contact_id=test_contact.id,
        type="Note",
        subject="Lead activity",
        activity_date=datetime.utcnow(),
        pipeline_stage="Lead"
    )
    activity2 = Activity(
        contact_id=test_contact.id,
        type="Call",
        subject="Qualified activity",
        activity_date=datetime.utcnow(),
        pipeline_stage="Qualified"
    )
    activity3 = Activity(
        contact_id=test_contact.id,
        type="Meeting",
        subject="Another lead activity",
        activity_date=datetime.utcnow(),
        pipeline_stage="Lead"
    )
    db_session.add(activity1)
    db_session.add(activity2)
    db_session.add(activity3)
    db_session.commit()

    # Query by pipeline_stage
    lead_activities = db_session.query(Activity).filter(
        Activity.contact_id == test_contact.id,
        Activity.pipeline_stage == "Lead"
    ).all()
    assert len(lead_activities) == 2

    qualified_activities = db_session.query(Activity).filter(
        Activity.contact_id == test_contact.id,
        Activity.pipeline_stage == "Qualified"
    ).all()
    assert len(qualified_activities) == 1


def test_multiple_contacts_with_different_pipeline_stages(db_session, test_user):
    """Test multiple contacts can have activities with different pipeline stages."""
    # Create two contacts
    contact1 = Contact(
        name="Contact One",
        email="contact1@example.com",
        user_id=test_user.id
    )
    contact2 = Contact(
        name="Contact Two",
        email="contact2@example.com",
        user_id=test_user.id
    )
    db_session.add(contact1)
    db_session.add(contact2)
    db_session.commit()

    # Create activities for contact 1 at Lead
    activity1 = Activity(
        contact_id=contact1.id,
        type="Note",
        subject="Contact 1 activity",
        activity_date=datetime.utcnow(),
        pipeline_stage="Lead"
    )

    # Create activities for contact 2 at Client
    activity2 = Activity(
        contact_id=contact2.id,
        type="Meeting",
        subject="Contact 2 activity",
        activity_date=datetime.utcnow(),
        pipeline_stage="Client"
    )
    db_session.add(activity1)
    db_session.add(activity2)
    db_session.commit()

    # Verify each contact has correct pipeline stage in their activities
    assert activity1.pipeline_stage == "Lead"
    assert activity2.pipeline_stage == "Client"
