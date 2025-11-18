"""Tests for Contact current_pipeline_stage derivation and pipeline stats."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Activity, Base, Contact, User
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


def test_contact_current_pipeline_stage_from_latest_activity(db_session, test_user):
    """Test that Contact.current_pipeline_stage is computed from latest activity."""
    # Create contact
    contact = Contact(
        name="John Doe",
        email="john@example.com",
        user_id=test_user.id,
        pipeline_stage="Lead"  # Old field - will be overridden by property
    )
    db_session.add(contact)
    db_session.commit()

    # Create activities with different stages over time
    activity1 = Activity(
        contact_id=contact.id,
        type="Note",
        subject="First contact",
        activity_date=datetime.utcnow() - timedelta(days=3),
        pipeline_stage="Lead"
    )
    activity2 = Activity(
        contact_id=contact.id,
        type="Call",
        subject="Follow-up call",
        activity_date=datetime.utcnow() - timedelta(days=1),
        pipeline_stage="Qualified"
    )
    activity3 = Activity(
        contact_id=contact.id,
        type="Meeting",
        subject="Proposal meeting",
        activity_date=datetime.utcnow(),
        pipeline_stage="Proposal"
    )
    db_session.add_all([activity1, activity2, activity3])
    db_session.commit()

    # Refresh contact to get latest data
    db_session.refresh(contact)

    # Current pipeline stage should be from the most recent activity
    assert contact.current_pipeline_stage == "Proposal"


def test_contact_current_pipeline_stage_defaults_to_lead(db_session, test_user):
    """Test that contact with no activities defaults to Lead."""
    # Create contact with no activities
    contact = Contact(
        name="Jane Smith",
        email="jane@example.com",
        user_id=test_user.id,
        pipeline_stage="Client"  # Old field - will be overridden by property
    )
    db_session.add(contact)
    db_session.commit()

    # Refresh contact
    db_session.refresh(contact)

    # Should default to "Lead" when no activities exist
    assert contact.current_pipeline_stage == "Lead"


def test_pipeline_stats_returns_active_passive_counts(db_session, test_user):
    """Test that get_pipeline_stats returns active and passive stage counts."""
    # Create contacts with various stages
    contacts = [
        Contact(name="Lead 1", email="lead1@example.com", user_id=test_user.id),
        Contact(name="Lead 2", email="lead2@example.com", user_id=test_user.id),
        Contact(name="Qualified 1", email="qualified1@example.com", user_id=test_user.id),
        Contact(name="Proposal 1", email="proposal1@example.com", user_id=test_user.id),
        Contact(name="Client 1", email="client1@example.com", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Create activities to set pipeline stages
    activities = [
        Activity(contact_id=contacts[0].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contacts[1].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contacts[2].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Qualified"),
        Activity(contact_id=contacts[3].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Proposal"),
        Activity(contact_id=contacts[4].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Client"),
    ]
    for activity in activities:
        db_session.add(activity)
    db_session.commit()

    # Get pipeline stats
    stats = ContactService.get_pipeline_stats(db_session, test_user.id)

    # Verify structure includes active/passive separation
    assert "active_stages" in stats
    assert "passive_stages" in stats
    assert "active_count" in stats
    assert "passive_count" in stats

    # Verify active stage counts
    assert stats["active_stages"]["Lead"] == 2
    assert stats["active_stages"]["Qualified"] == 1
    assert stats["active_stages"]["Proposal"] == 1
    assert stats["active_stages"]["Client"] == 1

    # Verify totals
    assert stats["active_count"] == 5
    assert stats["passive_count"] == 0


def test_pipeline_stats_includes_passive_stages(db_session, test_user):
    """Test that pipeline stats includes passive stage counts."""
    # Create contacts with passive stages
    contacts = [
        Contact(name="Qualified Out 1", email="qo1@example.com", user_id=test_user.id),
        Contact(name="Lost Proposal 1", email="lp1@example.com", user_id=test_user.id),
        Contact(name="Work Completed 1", email="wc1@example.com", user_id=test_user.id),
        Contact(name="Archived 1", email="ar1@example.com", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Create activities with passive stages
    activities = [
        Activity(contact_id=contacts[0].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Qualified Out"),
        Activity(contact_id=contacts[1].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lost Proposal"),
        Activity(contact_id=contacts[2].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Work Completed"),
        Activity(contact_id=contacts[3].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Archived"),
    ]
    for activity in activities:
        db_session.add(activity)
    db_session.commit()

    # Get pipeline stats
    stats = ContactService.get_pipeline_stats(db_session, test_user.id)

    # Verify passive stage counts
    assert stats["passive_stages"]["Qualified Out"] == 1
    assert stats["passive_stages"]["Lost Proposal"] == 1
    assert stats["passive_stages"]["Work Completed"] == 1
    assert stats["passive_stages"]["Archived"] == 1

    # Verify totals
    assert stats["active_count"] == 0
    assert stats["passive_count"] == 4


def test_filter_counts_reflect_search_query(db_session, test_user):
    """Test that filter counts are updated based on search query."""
    # Create contacts
    contacts = [
        Contact(name="Alice Anderson", email="alice@example.com", company="Alpha Corp", user_id=test_user.id),
        Contact(name="Bob Brown", email="bob@beta.com", company="Beta Inc", user_id=test_user.id),
        Contact(name="Charlie Chen", email="charlie@gamma.com", company="Gamma LLC", user_id=test_user.id),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Create activities
    activities = [
        Activity(contact_id=contacts[0].id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contacts[1].id, type="Call", activity_date=datetime.utcnow(), pipeline_stage="Qualified"),
        Activity(contact_id=contacts[2].id, type="Meeting", activity_date=datetime.utcnow(), pipeline_stage="Proposal"),
    ]
    for activity in activities:
        db_session.add(activity)
    db_session.commit()

    # Get filter counts without search
    counts_all = ContactService.get_filter_counts(db_session, test_user.id, search=None)
    assert counts_all["stage_counts"]["Lead"] == 1
    assert counts_all["stage_counts"]["Qualified"] == 1
    assert counts_all["stage_counts"]["Proposal"] == 1

    # Get filter counts with search query "alice"
    counts_filtered = ContactService.get_filter_counts(db_session, test_user.id, search="alice")
    assert counts_filtered["stage_counts"]["Lead"] == 1
    assert counts_filtered["stage_counts"].get("Qualified", 0) == 0
    assert counts_filtered["stage_counts"].get("Proposal", 0) == 0


def test_filter_counts_includes_activity_type_counts(db_session, test_user):
    """Test that filter counts includes activity type counts."""
    # Create contact
    contact = Contact(
        name="Test Contact",
        email="test@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Create activities of different types
    activities = [
        Activity(contact_id=contact.id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contact.id, type="Note", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contact.id, type="Call", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contact.id, type="Meeting", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
        Activity(contact_id=contact.id, type="Email", activity_date=datetime.utcnow(), pipeline_stage="Lead"),
    ]
    for activity in activities:
        db_session.add(activity)
    db_session.commit()

    # Get filter counts
    counts = ContactService.get_filter_counts(db_session, test_user.id, search=None)

    # Verify activity type counts
    assert "activity_type_counts" in counts
    assert counts["activity_type_counts"]["Note"] == 2
    assert counts["activity_type_counts"]["Call"] == 1
    assert counts["activity_type_counts"]["Meeting"] == 1
    assert counts["activity_type_counts"]["Email"] == 1
