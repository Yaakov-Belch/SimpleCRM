"""Integration tests for UX Improvements feature (Task Group 7.3).

This test file covers critical end-to-end workflows for the UX improvements feature:
- Activity creation to timeline display to stage badge rendering
- Contact filtering by Active/Passive tabs
- Filter count updates on search query change
- Contact current_pipeline_stage reflects latest activity
- Activity inherits pipeline_stage from previous activity
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Activity, Contact, User


@pytest.fixture
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def authenticated_user(client, db: DBSession):
    """Create and authenticate a test user."""
    # Register user
    register_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
    )

    assert register_response.status_code == 201
    session_token = register_response.json()["session_token"]
    user_id = register_response.json()["user"]["id"]

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    return {
        "user": user,
        "session_token": session_token,
        "headers": {"Authorization": f"Bearer {session_token}"}
    }


def test_activity_creation_updates_contact_current_pipeline_stage(client, db: DBSession, authenticated_user):
    """
    Test end-to-end: Create activities and verify contact's current_pipeline_stage
    updates to reflect the most recent activity's stage.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "John Doe",
            "email": "john@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact = contact_response.json()
    contact_id = contact["id"]

    # Step 2: Get contact - should have current_pipeline_stage="Lead" (no activities yet)
    get_contact_response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert get_contact_response.status_code == 200
    contact_data = get_contact_response.json()
    assert contact_data["current_pipeline_stage"] == "Lead"

    # Step 3: Create first activity with stage="Qualified"
    activity1_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Call",
            "subject": "Initial call",
            "activity_date": datetime.utcnow().isoformat(),
            "pipeline_stage": "Qualified"
        }
    )

    assert activity1_response.status_code == 201
    activity1 = activity1_response.json()
    assert activity1["pipeline_stage"] == "Qualified"

    # Step 4: Get contact again - should now have current_pipeline_stage="Qualified"
    get_contact_response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert get_contact_response.status_code == 200
    contact_data = get_contact_response.json()
    assert contact_data["current_pipeline_stage"] == "Qualified"

    # Step 5: Create second activity with stage="Proposal"
    activity2_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Meeting",
            "subject": "Proposal meeting",
            "activity_date": datetime.utcnow().isoformat(),
            "pipeline_stage": "Proposal"
        }
    )

    assert activity2_response.status_code == 201
    activity2 = activity2_response.json()
    assert activity2["pipeline_stage"] == "Proposal"

    # Step 6: Get contact final time - should now have current_pipeline_stage="Proposal"
    get_contact_response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert get_contact_response.status_code == 200
    contact_data = get_contact_response.json()
    assert contact_data["current_pipeline_stage"] == "Proposal"


def test_activity_inherits_pipeline_stage_from_most_recent_activity(client, db: DBSession, authenticated_user):
    """
    Test integration: When creating a new activity without specifying pipeline_stage,
    it should inherit from the most recent activity for that contact.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Step 2: Create first activity with explicit pipeline_stage="Qualified"
    activity1_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Call",
            "subject": "Qualification call",
            "activity_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "pipeline_stage": "Qualified"
        }
    )

    assert activity1_response.status_code == 201
    assert activity1_response.json()["pipeline_stage"] == "Qualified"

    # Step 3: Create second activity with explicit pipeline_stage="Client"
    activity2_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Meeting",
            "subject": "Contract signed",
            "activity_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "pipeline_stage": "Client"
        }
    )

    assert activity2_response.status_code == 201
    assert activity2_response.json()["pipeline_stage"] == "Client"

    # Step 4: Create third activity WITHOUT specifying pipeline_stage
    # Should inherit "Client" from most recent activity
    activity3_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Note",
            "subject": "Follow-up note",
            "activity_date": datetime.utcnow().isoformat()
        }
    )

    assert activity3_response.status_code == 201
    activity3 = activity3_response.json()
    assert activity3["pipeline_stage"] == "Client"  # Inherited from activity2


def test_filter_counts_update_based_on_search_query(client, db: DBSession, authenticated_user):
    """
    Test end-to-end: Filter counts should reflect the current search query,
    not just total counts.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create multiple contacts with different stages
    contacts_data = [
        {"name": "Alice Anderson", "email": "alice@alpha.com", "company": "Alpha Corp"},
        {"name": "Bob Brown", "email": "bob@beta.com", "company": "Beta Inc"},
        {"name": "Charlie Chen", "email": "charlie@alpha.com", "company": "Gamma LLC"},
    ]

    contact_ids = []
    for contact_data in contacts_data:
        response = client.post("/api/contacts", headers=headers, json=contact_data)
        assert response.status_code == 201
        contact_ids.append(response.json()["id"])

    # Step 2: Create activities to set different pipeline stages
    stages = ["Lead", "Qualified", "Proposal"]
    for i, (contact_id, stage) in enumerate(zip(contact_ids, stages)):
        activity_response = client.post(
            f"/api/contacts/{contact_id}/activities",
            headers=headers,
            json={
                "type": "Note",
                "subject": f"Activity for {stage}",
                "activity_date": datetime.utcnow().isoformat(),
                "pipeline_stage": stage
            }
        )
        assert activity_response.status_code == 201

    # Step 3: Get filter counts without search query
    counts_all_response = client.get("/api/contacts/filter-counts", headers=headers)
    assert counts_all_response.status_code == 200
    counts_all = counts_all_response.json()

    # Should have all three stages represented
    assert counts_all["stage_counts"]["Lead"] == 1
    assert counts_all["stage_counts"]["Qualified"] == 1
    assert counts_all["stage_counts"]["Proposal"] == 1

    # Step 4: Get filter counts with search query "alice"
    counts_filtered_response = client.get(
        "/api/contacts/filter-counts?search=alice",
        headers=headers
    )
    assert counts_filtered_response.status_code == 200
    counts_filtered = counts_filtered_response.json()

    # Should only show counts for contacts matching "alice"
    assert counts_filtered["stage_counts"]["Lead"] == 1  # Alice Anderson
    assert counts_filtered["stage_counts"].get("Qualified", 0) == 0
    assert counts_filtered["stage_counts"].get("Proposal", 0) == 0


def test_active_passive_contact_filtering(client, db: DBSession, authenticated_user):
    """
    Test end-to-end: Contacts should be correctly filtered by Active/Passive tabs
    based on their current_pipeline_stage.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create contacts with various stages
    contacts_data = [
        {"name": "Active Lead", "email": "lead@example.com"},
        {"name": "Active Qualified", "email": "qualified@example.com"},
        {"name": "Active Proposal", "email": "proposal@example.com"},
        {"name": "Active Client", "email": "client@example.com"},
        {"name": "Passive Qualified Out", "email": "qout@example.com"},
        {"name": "Passive Lost Proposal", "email": "lost@example.com"},
        {"name": "Passive Work Completed", "email": "completed@example.com"},
        {"name": "Passive Archived", "email": "archived@example.com"},
    ]

    stages = [
        "Lead", "Qualified", "Proposal", "Client",
        "Qualified Out", "Lost Proposal", "Work Completed", "Archived"
    ]

    contact_ids = []
    for contact_data in contacts_data:
        response = client.post("/api/contacts", headers=headers, json=contact_data)
        assert response.status_code == 201
        contact_ids.append(response.json()["id"])

    # Step 2: Create activities to set pipeline stages
    for contact_id, stage in zip(contact_ids, stages):
        activity_response = client.post(
            f"/api/contacts/{contact_id}/activities",
            headers=headers,
            json={
                "type": "Note",
                "subject": f"Activity at {stage}",
                "activity_date": datetime.utcnow().isoformat(),
                "pipeline_stage": stage
            }
        )
        assert activity_response.status_code == 201

    # Step 3: Get pipeline stats
    stats_response = client.get("/api/contacts/pipeline-stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()

    # Verify active stages count
    assert stats["active_count"] == 4
    assert stats["active_stages"]["Lead"] == 1
    assert stats["active_stages"]["Qualified"] == 1
    assert stats["active_stages"]["Proposal"] == 1
    assert stats["active_stages"]["Client"] == 1

    # Verify passive stages count
    assert stats["passive_count"] == 4
    assert stats["passive_stages"]["Qualified Out"] == 1
    assert stats["passive_stages"]["Lost Proposal"] == 1
    assert stats["passive_stages"]["Work Completed"] == 1
    assert stats["passive_stages"]["Archived"] == 1


def test_empty_activity_creation_immediate_workflow(client, db: DBSession, authenticated_user):
    """
    Test end-to-end: User clicks "New Activity", activity is created immediately
    with empty subject, and appears in timeline.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "Test Contact",
            "email": "test@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Step 2: Create activity with minimal data (simulating "New Activity" button click)
    activity_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Note",
            "subject": "",  # Empty subject allowed
            "activity_date": datetime.utcnow().isoformat()
        }
    )

    assert activity_response.status_code == 201
    activity = activity_response.json()
    assert activity["id"] is not None
    assert activity["subject"] == ""
    assert activity["type"] == "Note"
    assert activity["pipeline_stage"] == "Lead"  # Default for first activity

    # Step 3: Get activities for contact - should include the empty activity
    activities_response = client.get(
        f"/api/contacts/{contact_id}/activities",
        headers=headers
    )

    assert activities_response.status_code == 200
    activities = activities_response.json()["activities"]
    assert len(activities) == 1
    assert activities[0]["id"] == activity["id"]
    assert activities[0]["subject"] == ""


def test_pipeline_stage_badge_display_logic(client, db: DBSession, authenticated_user):
    """
    Test integration: Pipeline stage badges should only display when the stage
    differs from the previous activity.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "Badge Test Contact",
            "email": "badge@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Step 2: Create activities with stage changes
    activities_to_create = [
        {"stage": "Lead", "date_offset": -5},
        {"stage": "Lead", "date_offset": -4},  # Same as previous
        {"stage": "Qualified", "date_offset": -3},  # Stage change
        {"stage": "Qualified", "date_offset": -2},  # Same as previous
        {"stage": "Proposal", "date_offset": -1},  # Stage change
    ]

    created_activities = []
    for i, activity_data in enumerate(activities_to_create):
        activity_response = client.post(
            f"/api/contacts/{contact_id}/activities",
            headers=headers,
            json={
                "type": "Note",
                "subject": f"Activity {i + 1}",
                "activity_date": (datetime.utcnow() + timedelta(days=activity_data["date_offset"])).isoformat(),
                "pipeline_stage": activity_data["stage"]
            }
        )
        assert activity_response.status_code == 201
        created_activities.append(activity_response.json())

    # Step 3: Get all activities for contact
    activities_response = client.get(
        f"/api/contacts/{contact_id}/activities",
        headers=headers
    )

    assert activities_response.status_code == 200
    activities = activities_response.json()["activities"]

    # Activities should be sorted by date descending
    assert len(activities) == 5

    # Verify stages are as expected
    assert activities[0]["pipeline_stage"] == "Proposal"
    assert activities[1]["pipeline_stage"] == "Qualified"
    assert activities[2]["pipeline_stage"] == "Qualified"
    assert activities[3]["pipeline_stage"] == "Lead"
    assert activities[4]["pipeline_stage"] == "Lead"

    # Frontend logic would determine badge display based on comparing
    # each activity's stage with the previous one in the timeline


def test_contact_stage_derived_from_most_recent_activity_with_multiple_updates(client, db: DBSession, authenticated_user):
    """
    Test integration: Contact's current_pipeline_stage always reflects the
    most recent activity, even after multiple activity creations and updates.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "Multi-Update Contact",
            "email": "multiupdate@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Step 2: Create initial activity at Lead
    activity1_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Note",
            "subject": "Initial note",
            "activity_date": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "pipeline_stage": "Lead"
        }
    )
    assert activity1_response.status_code == 201

    # Verify contact stage
    contact_check = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert contact_check.json()["current_pipeline_stage"] == "Lead"

    # Step 3: Create second activity at Qualified
    activity2_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Call",
            "subject": "Qualification call",
            "activity_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "pipeline_stage": "Qualified"
        }
    )
    assert activity2_response.status_code == 201

    # Verify contact stage updated
    contact_check = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert contact_check.json()["current_pipeline_stage"] == "Qualified"

    # Step 4: Create third activity at Proposal
    activity3_response = client.post(
        f"/api/contacts/{contact_id}/activities",
        headers=headers,
        json={
            "type": "Meeting",
            "subject": "Proposal meeting",
            "activity_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "pipeline_stage": "Proposal"
        }
    )
    assert activity3_response.status_code == 201

    # Verify contact stage updated
    contact_check = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert contact_check.json()["current_pipeline_stage"] == "Proposal"

    # Step 5: Update the most recent activity's stage to Client
    activity3_id = activity3_response.json()["id"]
    update_response = client.put(
        f"/api/activities/{activity3_id}",
        headers=headers,
        json={
            "pipeline_stage": "Client"
        }
    )
    assert update_response.status_code == 200

    # Verify contact stage reflects the update
    contact_check = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert contact_check.json()["current_pipeline_stage"] == "Client"


def test_activity_type_counts_for_timeline_filter(client, db: DBSession, authenticated_user):
    """
    Test integration: Activity type counts should be available for timeline
    filter dropdown display.
    """
    headers = authenticated_user["headers"]
    user = authenticated_user["user"]

    # Step 1: Create a contact
    contact_response = client.post(
        "/api/contacts",
        headers=headers,
        json={
            "name": "Activity Types Contact",
            "email": "types@example.com"
        }
    )

    assert contact_response.status_code == 201
    contact_id = contact_response.json()["id"]

    # Step 2: Create activities of different types
    activity_types = [
        "Call", "Call", "Call",
        "Meeting", "Meeting",
        "Email",
        "Note", "Note", "Note", "Note"
    ]

    for i, activity_type in enumerate(activity_types):
        activity_response = client.post(
            f"/api/contacts/{contact_id}/activities",
            headers=headers,
            json={
                "type": activity_type,
                "subject": f"Activity {i + 1}",
                "activity_date": datetime.utcnow().isoformat()
            }
        )
        assert activity_response.status_code == 201

    # Step 3: Get filter counts which includes activity type counts
    counts_response = client.get("/api/contacts/filter-counts", headers=headers)
    assert counts_response.status_code == 200
    counts = counts_response.json()

    # Verify activity type counts
    assert "activity_type_counts" in counts
    assert counts["activity_type_counts"]["Call"] == 3
    assert counts["activity_type_counts"]["Meeting"] == 2
    assert counts["activity_type_counts"]["Email"] == 1
    assert counts["activity_type_counts"]["Note"] == 4
