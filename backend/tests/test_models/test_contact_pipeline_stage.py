"""Tests for Contact model pipeline_stage functionality."""

import pytest
from sqlalchemy import create_engine
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


def test_pipeline_stage_default_value(db_session, test_user):
    """Test that new contacts default to 'Lead' stage."""
    contact = Contact(
        name="Test Contact",
        email="test@example.com",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    assert contact.pipeline_stage == "Lead"


def test_pipeline_stage_accepts_valid_values(db_session, test_user):
    """Test that all valid pipeline stages are accepted."""
    valid_stages = ["Lead", "Qualified", "Proposal", "Client"]

    for stage in valid_stages:
        contact = Contact(
            name=f"Contact {stage}",
            email=f"{stage.lower()}@example.com",
            pipeline_stage=stage,
            user_id=test_user.id
        )
        db_session.add(contact)
        db_session.commit()

        assert contact.pipeline_stage == stage
        assert contact.id is not None


def test_pipeline_stage_indexed(db_session):
    """Test that pipeline_stage column has an index for efficient querying."""
    # Get the table metadata
    from sqlalchemy import inspect
    inspector = inspect(db_session.bind)
    indexes = inspector.get_indexes("contacts")

    # Check if there's an index on pipeline_stage
    pipeline_stage_indexed = False
    for index in indexes:
        if "pipeline_stage" in index["column_names"]:
            pipeline_stage_indexed = True
            break

    assert pipeline_stage_indexed, "pipeline_stage should be indexed"


def test_pipeline_stage_update(db_session, test_user):
    """Test updating a contact's pipeline stage."""
    contact = Contact(
        name="Test Contact",
        email="test@example.com",
        pipeline_stage="Lead",
        user_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()

    # Update to Qualified
    contact.pipeline_stage = "Qualified"
    db_session.commit()
    db_session.refresh(contact)

    assert contact.pipeline_stage == "Qualified"

    # Update to Proposal
    contact.pipeline_stage = "Proposal"
    db_session.commit()
    db_session.refresh(contact)

    assert contact.pipeline_stage == "Proposal"

    # Update to Client
    contact.pipeline_stage = "Client"
    db_session.commit()
    db_session.refresh(contact)

    assert contact.pipeline_stage == "Client"


def test_pipeline_stage_field_is_required(db_session, test_user):
    """Test that pipeline_stage field has NOT NULL constraint in model definition."""
    # Verify the column definition has nullable=False
    from app.models.contact import Contact as ContactModel
    pipeline_stage_column = ContactModel.__table__.columns['pipeline_stage']

    assert pipeline_stage_column.nullable is False, "pipeline_stage should have nullable=False"
    assert pipeline_stage_column.default.arg == "Lead", "pipeline_stage should default to 'Lead'"
