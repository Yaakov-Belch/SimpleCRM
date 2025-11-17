# SimpleCRM Database Schema

This document describes the database schema for SimpleCRM's user authentication system.

## Database Technology

- **Type:** SQLite
- **ORM:** SQLAlchemy
- **Location:** `backend/simplecrm.db`
- **Connection String:** `sqlite:///./simplecrm.db`

## Tables Overview

The authentication system uses two main tables:
1. `users` - Stores user account information
2. `sessions` - Stores active user sessions for authentication

## Entity Relationship Diagram

```
┌─────────────────────────┐
│        users            │
├─────────────────────────┤
│ id (PK)                 │
│ email (UNIQUE)          │
│ full_name               │
│ hashed_password         │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────────┐
│      sessions           │
├─────────────────────────┤
│ id (PK)                 │
│ session_token (UNIQUE)  │
│ user_id (FK)            │
│ expires_at              │
│ created_at              │
└─────────────────────────┘
```

## Table: `users`

Stores user account information including credentials and profile data.

### Schema

| Column Name      | Type         | Constraints                          | Description                                    |
|------------------|--------------|--------------------------------------|------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTOINCREMENT           | Unique identifier for the user                 |
| `email`          | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED            | User's email address (case-insensitive unique) |
| `full_name`      | VARCHAR(255) | NOT NULL                             | User's full name                               |
| `hashed_password`| VARCHAR(255) | NOT NULL                             | Bcrypt hashed password (never exposed in API)  |
| `created_at`     | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP  | Timestamp when user was created                |
| `updated_at`     | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP | Timestamp of last update |

### Indexes

- `ix_users_email` - B-tree index on `email` column for fast email lookups
- Primary key index on `id` (automatic)

### Constraints

- **Email Uniqueness:** Email addresses are unique (case-insensitive comparison)
- **Email Validation:** Email format validated at application layer (Pydantic)
- **Password Security:** Passwords hashed with bcrypt (12 rounds) before storage

### Relationships

- **One-to-Many with sessions:** Each user can have multiple active sessions
  - Relationship: `User.sessions` → `Session.user`
  - Cascade: Sessions are deleted when user is deleted (`CASCADE`)

### Example Row

```json
{
  "id": 1,
  "email": "john@example.com",
  "full_name": "John Doe",
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ufWy.Lgr6fiu",
  "created_at": "2025-11-17 10:30:45.123456",
  "updated_at": "2025-11-17 10:30:45.123456"
}
```

### Notes

- Email lookups are always case-insensitive using `func.lower(User.email) == email.lower()`
- `hashed_password` is never included in API responses (excluded in Pydantic schemas)
- `updated_at` automatically updates when any field is modified

---

## Table: `sessions`

Stores active authentication sessions for users.

### Schema

| Column Name      | Type         | Constraints                          | Description                                    |
|------------------|--------------|--------------------------------------|------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTOINCREMENT           | Unique identifier for the session              |
| `session_token`  | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED            | Cryptographically secure random token          |
| `user_id`        | INTEGER      | FOREIGN KEY(users.id), NOT NULL, INDEXED | References the user who owns this session   |
| `expires_at`     | DATETIME     | NOT NULL, INDEXED                    | Timestamp when session expires                 |
| `created_at`     | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP  | Timestamp when session was created             |

### Indexes

- `ix_sessions_session_token` - B-tree index on `session_token` for fast lookups
- `ix_sessions_user_id` - B-tree index on `user_id` for user session queries
- `ix_sessions_expires_at` - B-tree index on `expires_at` for expiration queries
- Primary key index on `id` (automatic)

### Constraints

- **Token Uniqueness:** Session tokens are unique across all sessions
- **Foreign Key:** `user_id` references `users.id` with CASCADE DELETE
  - When a user is deleted, all their sessions are automatically deleted
- **Expiration:** Sessions expire after 7 days (configurable via `SESSION_DURATION_DAYS`)

### Relationships

- **Many-to-One with users:** Each session belongs to one user
  - Relationship: `Session.user` → `User.sessions`
  - Foreign Key: `user_id` → `users.id`
  - Cascade: `ON DELETE CASCADE` (sessions deleted when user deleted)

### Example Row

```json
{
  "id": 1,
  "session_token": "1kGLQ31Ec-4knNEbLIC3CsD1qVP9UmdNDpYZMoj0ThA",
  "user_id": 1,
  "expires_at": "2025-11-24 10:30:45.123456",
  "created_at": "2025-11-17 10:30:45.123456"
}
```

### Notes

- Session tokens generated using `secrets.token_urlsafe(32)` (cryptographically secure)
- Tokens are ~43 characters long (base64-encoded)
- Multiple concurrent sessions allowed per user
- Expired sessions validated during authentication middleware
- Sessions can be cleaned up opportunistically or via background task

---

## Data Flow & Lifecycle

### User Registration Flow

1. User submits registration form with `full_name`, `email`, `password`
2. Application validates input (email format, password length, email uniqueness)
3. Password hashed with bcrypt (12 rounds)
4. User record created in `users` table
5. Session record created in `sessions` table (7-day expiration)
6. Both operations committed in single transaction
7. User automatically logged in with session token

### Login Flow

1. User submits email and password
2. Application looks up user by email (case-insensitive)
3. Password verified using bcrypt timing-safe comparison
4. New session record created in `sessions` table (7-day expiration)
5. Existing sessions remain active (multiple concurrent sessions allowed)
6. Session token returned to user

### Authentication Flow

1. Client includes session token in `Authorization` header (`Bearer {token}`)
2. Middleware extracts token and looks up session in `sessions` table
3. Session validated: exists, not expired (`expires_at > current_time`)
4. User loaded from `users` table via `session.user_id`
5. User object attached to request context for downstream use
6. Invalid/expired sessions return 401 Unauthorized

### Logout Flow

1. User sends logout request with session token
2. Application looks up session by token in `sessions` table
3. Session record deleted from database
4. Other sessions for same user remain active
5. Success message returned

### Profile Update Flow

1. User authenticated via session token
2. Update data submitted (partial updates supported)
3. If email changed, uniqueness validated (excluding current user)
4. If password changed, new password hashed with bcrypt
5. User record updated in `users` table
6. `updated_at` timestamp automatically updated
7. Updated user data returned (excluding `hashed_password`)

### User Deletion Flow (Admin Script)

1. Admin runs `delete_user.py --email user@example.com`
2. User looked up by email (case-insensitive)
3. All associated sessions deleted from `sessions` table
4. User record deleted from `users` table
5. Both operations committed in single transaction
6. Cascade delete ensures referential integrity

---

## Security Considerations

### Password Security

- Passwords hashed with bcrypt using 12 salt rounds
- Minimum password length: 8 characters (enforced by Pydantic schema)
- Plain text passwords never stored in database or logs
- Timing-safe password verification using `bcrypt.checkpw()`
- `hashed_password` field never exposed in API responses

### Session Security

- Session tokens generated using `secrets.token_urlsafe(32)` (cryptographically secure)
- Minimum 32 bytes of randomness (~43 characters base64-encoded)
- Tokens unique across all sessions (uniqueness enforced by database)
- Sessions expire after 7 days (configurable)
- Expired sessions rejected during authentication

### Email Security

- Email uniqueness enforced (case-insensitive)
- Email format validated at application layer
- Failed login returns generic message to prevent email enumeration
- Email lookups use indexed columns for performance

### Database Security

- SQLAlchemy ORM used (prevents SQL injection)
- Foreign key constraints enforce referential integrity
- Cascade deletes prevent orphaned sessions
- Indexes improve query performance without exposing sensitive data

---

## Migration & Initialization

### Initial Schema Creation

The database schema is created automatically on application startup:

```python
# In app/main.py
from app.database import engine, Base
from app.models import User, Session

Base.metadata.create_all(bind=engine)
```

### Schema Updates

For future schema changes:

1. Use Alembic for database migrations
2. Create migration scripts in `backend/alembic/versions/`
3. Test migrations in development before production
4. Document breaking changes in migration notes

### Development Setup

```bash
# Database created automatically on first run
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Database file created at: backend/simplecrm.db
```

### Production Considerations

- Consider using PostgreSQL for production (better concurrency, performance)
- Implement connection pooling for multi-process deployments
- Add database backups and recovery procedures
- Monitor session table growth and implement cleanup
- Consider adding audit logging for user/session changes

---

## Queries & Performance

### Common Queries

**Find user by email (case-insensitive):**
```python
from sqlalchemy import func
user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
```

**Validate session:**
```python
from datetime import datetime
session = db.query(Session).filter(
    Session.session_token == token,
    Session.expires_at > datetime.utcnow()
).first()
```

**Get user with sessions:**
```python
user = db.query(User).options(joinedload(User.sessions)).filter(User.id == user_id).first()
```

**Delete expired sessions (cleanup):**
```python
from datetime import datetime
db.query(Session).filter(Session.expires_at <= datetime.utcnow()).delete()
db.commit()
```

### Index Usage

All indexed columns are used in WHERE clauses for optimal query performance:

- `users.email` - Indexed for email lookups during login and registration
- `sessions.session_token` - Indexed for session validation
- `sessions.user_id` - Indexed for user session queries
- `sessions.expires_at` - Indexed for expiration cleanup queries

---

## Maintenance

### Session Cleanup

Expired sessions should be cleaned up periodically:

```python
from datetime import datetime
from app.database import SessionLocal
from app.models.session import Session

db = SessionLocal()
deleted = db.query(Session).filter(Session.expires_at <= datetime.utcnow()).delete()
db.commit()
print(f"Deleted {deleted} expired sessions")
```

### Database Backup

```bash
# Backup SQLite database
cp backend/simplecrm.db backend/simplecrm.db.backup

# Restore from backup
cp backend/simplecrm.db.backup backend/simplecrm.db
```

### Monitoring

Monitor these metrics:
- Total users count
- Active sessions count
- Expired sessions awaiting cleanup
- User growth rate
- Average sessions per user

```python
# Get statistics
total_users = db.query(User).count()
active_sessions = db.query(Session).filter(Session.expires_at > datetime.utcnow()).count()
expired_sessions = db.query(Session).filter(Session.expires_at <= datetime.utcnow()).count()
```

---

## Future Enhancements

Potential schema improvements for future versions:

1. **Add user roles/permissions table** for access control
2. **Add password reset tokens table** for password recovery
3. **Add audit log table** for tracking user actions
4. **Add login attempt tracking** for security monitoring
5. **Add user preferences table** for customization
6. **Add email verification tokens table** for email confirmation
7. **Add OAuth provider table** for social login integration
8. **Add session metadata** (IP address, user agent, device info)

---

## References

- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Bcrypt Documentation: https://github.com/pyca/bcrypt/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLite Documentation: https://www.sqlite.org/docs.html
