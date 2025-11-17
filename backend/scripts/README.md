# SimpleCRM Admin Scripts

This directory contains administrative command-line tools for managing SimpleCRM.

## Prerequisites

- Python 3.11 or higher
- Backend dependencies installed: `pip install -r requirements.txt`
- Database configured via `.env` file or environment variables

## Available Scripts

### delete_user.py

Delete a user account and all associated data (sessions) from the database.

**Usage:**

```bash
python backend/scripts/delete_user.py --email user@example.com
```

**Description:**

This script deletes a user account by email address. It will:
1. Look up the user by email (case-insensitive)
2. Display user details (ID, email, full name, created date)
3. Delete all associated sessions
4. Delete the user record
5. Display success/error message

**Important Notes:**

- **No confirmation prompt** - deletion is immediate
- Email lookup is case-insensitive
- All associated sessions are deleted automatically
- Operation is transactional (all or nothing)

**Arguments:**

- `--email` (required): Email address of the user to delete

**Environment Variables:**

The script uses the same configuration as the main application:

- `DATABASE_URL` - Database connection string (default: `sqlite:///./simplecrm.db`)
- Other app settings are loaded from `.env` file if present

**Exit Codes:**

- `0` - Success: User deleted successfully
- `1` - Error: User not found, database error, or invalid input

**Examples:**

```bash
# Delete user by email
python backend/scripts/delete_user.py --email john@example.com

# Delete user (case-insensitive)
python backend/scripts/delete_user.py --email JOHN@EXAMPLE.COM

# Using from project root with virtual environment
source backend/venv/bin/activate
python backend/scripts/delete_user.py --email user@test.com
```

**Error Scenarios:**

1. **User not found:**
   ```
   Error: User with email 'nonexistent@example.com' not found in database.
   ```

2. **Invalid email format:**
   ```
   Error: Invalid email format: invalidemail
   Email must contain @ symbol and have valid structure
   ```

3. **Database connection failure:**
   ```
   Error: Failed to connect to database
   Database URL: sqlite:///./simplecrm.db
   Details: [error details]
   ```

**Success Output:**

```
User found:
  ID: 42
  Email: user@example.com
  Full Name: John Doe
  Created At: 2025-11-17 10:30:45.123456

Associated sessions to be deleted: 3

Success: User 'user@example.com' and all associated data have been deleted.
```

## Development

To add new admin scripts:

1. Create a new Python file in this directory
2. Make it executable: `chmod +x script_name.py`
3. Add shebang: `#!/usr/bin/env python3`
4. Include comprehensive docstring with usage examples
5. Use argparse for command-line arguments
6. Handle errors gracefully with clear messages
7. Use appropriate exit codes (0 for success, 1 for errors)
8. Document the script in this README

## Security Considerations

- Admin scripts have direct database access
- Use with caution in production environments
- Consider implementing audit logging for deletions
- Ensure scripts are not accessible to unauthorized users
- Review and test scripts in development before production use

## Testing

To test admin scripts:

1. Create test users via registration API or database
2. Run script with test data
3. Verify results in database
4. Test error scenarios (invalid input, missing users, etc.)

Example test workflow:

```bash
# Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, create test user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"password123"}'

# Delete test user
python scripts/delete_user.py --email test@example.com

# Verify deletion
# Try to login - should fail with "Invalid email or password"
```
