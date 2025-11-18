"""
Migration: Make subject column nullable in activities table.

This migration modifies the subject column in activities table to allow NULL
values and set a default empty string, enabling immediate activity creation
with minimal data (empty activities workflow).

Date: 2025-11-18
"""

from sqlalchemy import create_engine, inspect, text

from app.config import settings


def upgrade():
    """
    Modify subject column in activities table to be nullable.

    - Changes column: subject (VARCHAR(255), NULL, DEFAULT '')
    - Allows empty activities to be created
    """
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)

    # Check if activities table exists
    if 'activities' not in inspector.get_table_names():
        print("Table 'activities' does not exist. Skipping migration.")
        return

    with engine.connect() as conn:
        # SQLite doesn't support ALTER COLUMN directly, need to recreate table
        # Create new table with nullable subject
        conn.execute(text("""
            CREATE TABLE activities_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                subject VARCHAR(255) DEFAULT '',
                notes TEXT,
                activity_date DATETIME NOT NULL,
                pipeline_stage VARCHAR(50) NOT NULL DEFAULT 'Lead',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE
            )
        """))

        # Copy data from old table to new table
        conn.execute(text("""
            INSERT INTO activities_new (
                id, contact_id, type, subject, notes, activity_date,
                pipeline_stage, created_at, updated_at
            )
            SELECT
                id, contact_id, type,
                COALESCE(subject, '') as subject,
                notes, activity_date, pipeline_stage, created_at, updated_at
            FROM activities
        """))

        # Drop old table
        conn.execute(text("DROP TABLE activities"))

        # Rename new table to original name
        conn.execute(text("ALTER TABLE activities_new RENAME TO activities"))

        # Recreate indexes
        conn.execute(text("CREATE INDEX ix_activities_contact_id ON activities (contact_id)"))
        conn.execute(text("CREATE INDEX ix_activities_type ON activities (type)"))
        conn.execute(text("CREATE INDEX ix_activities_activity_date ON activities (activity_date)"))
        conn.execute(text("CREATE INDEX ix_activities_pipeline_stage ON activities (pipeline_stage)"))

        conn.commit()

    print("Successfully made subject column nullable in activities table.")


def downgrade():
    """
    Revert subject column in activities table to NOT NULL.

    Rollback strategy for reverting this migration.
    WARNING: This will set empty subjects to 'Untitled' to satisfy NOT NULL constraint.
    """
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)

    # Check if activities table exists
    if 'activities' not in inspector.get_table_names():
        print("Table 'activities' does not exist. Skipping rollback.")
        return

    with engine.connect() as conn:
        # Update empty subjects to 'Untitled' before making column NOT NULL
        conn.execute(text("""
            UPDATE activities
            SET subject = 'Untitled'
            WHERE subject IS NULL OR subject = ''
        """))

        # Create new table with NOT NULL subject
        conn.execute(text("""
            CREATE TABLE activities_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                notes TEXT,
                activity_date DATETIME NOT NULL,
                pipeline_stage VARCHAR(50) NOT NULL DEFAULT 'Lead',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE
            )
        """))

        # Copy data from old table to new table
        conn.execute(text("""
            INSERT INTO activities_new (
                id, contact_id, type, subject, notes, activity_date,
                pipeline_stage, created_at, updated_at
            )
            SELECT
                id, contact_id, type, subject, notes, activity_date,
                pipeline_stage, created_at, updated_at
            FROM activities
        """))

        # Drop old table
        conn.execute(text("DROP TABLE activities"))

        # Rename new table to original name
        conn.execute(text("ALTER TABLE activities_new RENAME TO activities"))

        # Recreate indexes
        conn.execute(text("CREATE INDEX ix_activities_contact_id ON activities (contact_id)"))
        conn.execute(text("CREATE INDEX ix_activities_type ON activities (type)"))
        conn.execute(text("CREATE INDEX ix_activities_activity_date ON activities (activity_date)"))
        conn.execute(text("CREATE INDEX ix_activities_pipeline_stage ON activities (pipeline_stage)"))

        conn.commit()

    print("Successfully reverted subject column to NOT NULL in activities table.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python make_activity_subject_nullable.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "upgrade":
        upgrade()
    elif command == "downgrade":
        downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python make_activity_subject_nullable.py [upgrade|downgrade]")
        sys.exit(1)
