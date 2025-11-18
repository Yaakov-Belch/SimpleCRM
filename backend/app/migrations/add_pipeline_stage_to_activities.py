"""
Migration: Add pipeline_stage column to activities table.

This migration adds a pipeline_stage column to the activities table to track
the pipeline stage at the time of each activity. This enables tracking stage
changes over time through the activity timeline.

Date: 2025-11-18
"""

from sqlalchemy import create_engine, inspect, text

from app.config import settings


def upgrade():
    """
    Add pipeline_stage column to activities table.

    - Adds column: pipeline_stage (VARCHAR(50), NOT NULL, DEFAULT 'Lead')
    - Creates index on pipeline_stage for query performance
    """
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)

    # Check if column already exists
    columns = [col['name'] for col in inspector.get_columns('activities')]
    if 'pipeline_stage' in columns:
        print("Column 'pipeline_stage' already exists in activities table. Skipping migration.")
        return

    with engine.connect() as conn:
        # Add pipeline_stage column with default value
        conn.execute(text(
            "ALTER TABLE activities ADD COLUMN pipeline_stage VARCHAR(50) NOT NULL DEFAULT 'Lead'"
        ))

        # Create index on pipeline_stage for query performance
        conn.execute(text(
            "CREATE INDEX ix_activities_pipeline_stage ON activities (pipeline_stage)"
        ))

        conn.commit()

    print("Successfully added pipeline_stage column to activities table.")


def downgrade():
    """
    Remove pipeline_stage column from activities table.

    Rollback strategy for reverting this migration.
    """
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)

    # Check if column exists
    columns = [col['name'] for col in inspector.get_columns('activities')]
    if 'pipeline_stage' not in columns:
        print("Column 'pipeline_stage' does not exist in activities table. Skipping rollback.")
        return

    with engine.connect() as conn:
        # Drop index first
        conn.execute(text(
            "DROP INDEX IF EXISTS ix_activities_pipeline_stage"
        ))

        # Remove pipeline_stage column
        # Note: SQLite doesn't support DROP COLUMN directly, need to recreate table
        # For simplicity in this migration, we document the limitation
        # In production, would use a more robust approach

        # Create backup table without pipeline_stage
        conn.execute(text("""
            CREATE TABLE activities_backup AS
            SELECT id, contact_id, type, subject, notes, activity_date, created_at, updated_at
            FROM activities
        """))

        # Drop original table
        conn.execute(text("DROP TABLE activities"))

        # Rename backup to original
        conn.execute(text("ALTER TABLE activities_backup RENAME TO activities"))

        # Recreate indexes (excluding pipeline_stage)
        conn.execute(text("CREATE INDEX ix_activities_contact_id ON activities (contact_id)"))
        conn.execute(text("CREATE INDEX ix_activities_type ON activities (type)"))
        conn.execute(text("CREATE INDEX ix_activities_activity_date ON activities (activity_date)"))

        conn.commit()

    print("Successfully removed pipeline_stage column from activities table.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python add_pipeline_stage_to_activities.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "upgrade":
        upgrade()
    elif command == "downgrade":
        downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python add_pipeline_stage_to_activities.py [upgrade|downgrade]")
        sys.exit(1)
