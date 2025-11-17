#!/usr/bin/env python3
"""
Admin tool for deleting user accounts from SimpleCRM.

This script provides a command-line interface for administrators to delete
user accounts and all associated data (sessions) from the database.

Usage:
    python backend/scripts/delete_user.py --email user@example.com

Requirements:
    - Database must be accessible via DATABASE_URL environment variable
    - User will be deleted immediately without confirmation prompt
    - All associated sessions will be deleted (cascade)

Exit Codes:
    0 - Success: User deleted successfully
    1 - Error: User not found, database error, or invalid input
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.user import User
from app.models.session import Session as SessionModel


def validate_email_format(email: str) -> bool:
    """
    Validate basic email format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email has basic valid format
    """
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if not parts[0] or not parts[1]:
        return False
    return True


def delete_user_by_email(db: Session, email: str) -> bool:
    """
    Delete a user and all associated sessions by email address.

    Args:
        db: SQLAlchemy database session
        email: User's email address (case-insensitive)

    Returns:
        bool: True if user was deleted, False if user not found

    Raises:
        Exception: If database operation fails
    """
    # Look up user by email (case-insensitive)
    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.email) == email.lower()).first()

    if not user:
        return False

    # Display user details before deletion
    print("\nUser found:")
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Full Name: {user.full_name}")
    print(f"  Created At: {user.created_at}")
    print()

    # Count associated sessions
    session_count = db.query(SessionModel).filter(SessionModel.user_id == user.id).count()
    print(f"Associated sessions to be deleted: {session_count}")
    print()

    # Delete all associated sessions explicitly (although CASCADE should handle this)
    db.query(SessionModel).filter(SessionModel.user_id == user.id).delete()

    # Delete user record
    db.delete(user)
    db.commit()

    return True


def main():
    """Main entry point for the delete user script."""
    parser = argparse.ArgumentParser(
        description='Delete a user account and all associated data from SimpleCRM',
        epilog='Example: python backend/scripts/delete_user.py --email user@example.com'
    )
    parser.add_argument(
        '--email',
        required=True,
        help='Email address of the user to delete (case-insensitive)'
    )

    args = parser.parse_args()
    email = args.email.strip()

    # Validate email format
    if not validate_email_format(email):
        print(f"Error: Invalid email format: {email}", file=sys.stderr)
        print("Email must contain @ symbol and have valid structure", file=sys.stderr)
        sys.exit(1)

    # Connect to database
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
    except Exception as e:
        print(f"Error: Failed to connect to database", file=sys.stderr)
        print(f"Database URL: {settings.DATABASE_URL}", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Delete user
    try:
        success = delete_user_by_email(db, email)

        if success:
            print(f"Success: User '{email}' and all associated data have been deleted.")
            sys.exit(0)
        else:
            print(f"Error: User with email '{email}' not found in database.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        db.rollback()
        print(f"Error: Failed to delete user '{email}'", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
