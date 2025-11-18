"""Tests for Contact schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.contact import ContactCreateSchema, ContactResponseSchema, ContactUpdateSchema


def test_contact_create_schema_with_required_fields():
    """Test ContactCreateSchema with only required fields."""
    data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    schema = ContactCreateSchema(**data)

    assert schema.name == "John Doe"
    assert schema.email == "john@example.com"
    assert schema.pipeline_stage == "Lead"  # Default value


def test_contact_create_schema_with_all_fields():
    """Test ContactCreateSchema with all fields."""
    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+1234567890",
        "company": "Acme Corp",
        "job_title": "CEO",
        "website": "https://example.com",
        "notes": "Important client",
        "pipeline_stage": "Client"
    }
    schema = ContactCreateSchema(**data)

    assert schema.name == "Jane Smith"
    assert schema.email == "jane@example.com"
    assert schema.phone == "+1234567890"
    assert schema.company == "Acme Corp"
    assert schema.job_title == "CEO"
    assert str(schema.website) == "https://example.com/"  # HttpUrl adds trailing slash
    assert schema.notes == "Important client"
    assert schema.pipeline_stage == "Client"


def test_contact_create_schema_email_validation():
    """Test that invalid email format raises validation error."""
    data = {
        "name": "Test User",
        "email": "invalid-email"
    }

    with pytest.raises(ValidationError) as exc_info:
        ContactCreateSchema(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("email",) for error in errors)


def test_contact_create_schema_name_max_length():
    """Test name max length validation."""
    data = {
        "name": "A" * 256,  # Exceeds max_length of 255
        "email": "test@example.com"
    }

    with pytest.raises(ValidationError) as exc_info:
        ContactCreateSchema(**data)

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_contact_update_schema_partial_update():
    """Test ContactUpdateSchema allows partial updates."""
    data = {
        "name": "Updated Name"
    }
    schema = ContactUpdateSchema(**data)

    assert schema.name == "Updated Name"
    assert schema.email is None
    assert schema.phone is None


def test_contact_update_schema_all_fields_optional():
    """Test that all fields in ContactUpdateSchema are optional."""
    schema = ContactUpdateSchema()

    assert schema.name is None
    assert schema.email is None
    assert schema.pipeline_stage is None


def test_contact_pipeline_stage_enum_validation():
    """Test pipeline_stage validates against allowed values."""
    valid_stages = ["Lead", "Qualified", "Proposal", "Client"]

    for stage in valid_stages:
        data = {
            "name": "Test",
            "email": "test@example.com",
            "pipeline_stage": stage
        }
        schema = ContactCreateSchema(**data)
        assert schema.pipeline_stage == stage
