# Specification: User Authentication & Account Management

## Goal
Provide secure session-based authentication and basic account management as the foundational feature for SimpleCRM, enabling users to register, login, manage profiles, and logout with 7-day session persistence.

## User Stories
- As a freelancer, I want to create an account with minimal friction so that I can start using SimpleCRM immediately without email verification delays
- As a solo consultant, I want to stay logged in for 7 days so that I don't need to re-authenticate every time I access the application
- As a user, I want to view and update my profile information so that I can keep my account details current

## Specific Requirements

**User Registration with Auto-Login**
- Registration form accepts full name, email address, and password (minimum 2 characters)
- Email uniqueness enforced server-side with case-insensitive validation
- Upon successful registration, user is automatically logged in with a 7-day session
- User is redirected to dashboard after registration completes
- No email verification required - immediate app access
- Password hashed using bcrypt or argon2 before database storage
- Server-side validation returns clear error messages for duplicate email or invalid input
- Client-side validation provides immediate feedback on field blur events

**Session-Based Login**
- Login form accepts email and password credentials
- Successful authentication creates server-side session valid for 7 days
- Session token generated using cryptographically secure random bytes (minimum 32 bytes)
- Session stored in SQLite sessions table with user_id foreign key and expires_at timestamp
- After successful login, user redirected to dashboard placeholder page
- Invalid credentials return generic "Invalid email or password" message (security best practice)
- No rate limiting or account lockout in MVP (documented as out of scope)
- Session token transmitted via HTTP-only secure cookie or Authorization header

**User Profile Management**
- Profile page displays current user's full name and email (read-only view section)
- Edit form allows updating full name, email, and/or password independently
- Partial updates supported - can update single field without providing all fields
- Email change maintains uniqueness constraint excluding current user
- Password updates require minimum 2 characters and are hashed before storage
- Success feedback displayed after successful profile update
- Validation errors displayed inline near relevant form fields
- Profile page requires valid session - protected route

**User Logout**
- Logout button/link available in navigation component
- Logout action deletes only current session from sessions table
- After logout, user redirected to login page
- No "log out all devices" functionality in MVP
- Logged-out users attempting to access protected pages redirected to login with appropriate message

**Session Management & Validation**
- Middleware extracts session token from request (cookie or Authorization header)
- Session validation checks: token exists in database, not expired (expires_at > current_time), user_id is valid
- Valid session attaches user object to request context for downstream use
- Invalid or expired session returns 401 Unauthorized and redirects to login
- Session duration fixed at 7 days from creation time
- Expired sessions cleaned up opportunistically during validation or via background task

**Dashboard Placeholder**
- Dashboard page serves as post-login landing destination
- Displays welcome message with user's full name ("Welcome, [Full Name]")
- Includes navigation component with user info and logout link
- Protected route requiring valid authentication session
- Minimal functionality - serves as foundation for future dashboard features
- Page structure follows Vue 3 Composition API patterns

**Database Schema - User Model**
- Table name: users (plural convention)
- id: Integer primary key, auto-increment
- email: String(255), unique constraint, not null, indexed for lookup performance
- full_name: String(255), not null
- hashed_password: String(255), not null, never returned in API responses
- created_at: DateTime, not null, default current timestamp
- updated_at: DateTime, not null, default current timestamp, auto-update on modification
- SQLAlchemy model with relationship to sessions table

**Database Schema - Session Model**
- Table name: sessions (plural convention)
- id: Integer primary key, auto-increment
- session_token: String(255), unique constraint, not null, indexed for fast lookup
- user_id: Integer, foreign key to users.id, not null, indexed, cascade delete on user deletion
- expires_at: DateTime, not null, indexed for efficient expiration queries
- created_at: DateTime, not null, default current timestamp
- SQLAlchemy model with relationship back to User model

**API Endpoint - POST /api/auth/register**
- Request body: JSON with full_name (string), email (string), password (string)
- Validates email format, uniqueness, password minimum length, full_name presence
- Returns 201 Created with user object (id, email, full_name) and session_token on success
- Returns 400 Bad Request for validation failures with specific error messages
- Returns 409 Conflict when email already exists
- Returns 500 Internal Server Error for unexpected failures
- Creates user record with hashed password and session record in single database transaction
- Pydantic schema validates request body structure and types

**API Endpoint - POST /api/auth/login**
- Request body: JSON with email (string), password (string)
- Validates credentials by looking up user and verifying hashed password
- Returns 200 OK with user object (id, email, full_name) and session_token on success
- Returns 400 Bad Request for missing or malformed fields
- Returns 401 Unauthorized for invalid credentials with generic message
- Returns 500 Internal Server Error for unexpected failures
- Creates new session record with 7-day expiration on successful authentication
- Does not delete existing sessions - multiple concurrent sessions allowed

**API Endpoint - POST /api/auth/logout**
- Requires valid session token in cookie or Authorization header
- Deletes current session from sessions table by matching session_token
- Returns 200 OK with success message JSON
- Returns 401 Unauthorized if no valid session provided
- Does not delete other sessions belonging to same user
- Frontend clears session token from storage after successful logout

**API Endpoint - GET /api/users/me**
- Requires valid session token via middleware authentication
- Returns 200 OK with current user profile: id, email, full_name, created_at, updated_at
- Returns 401 Unauthorized if session invalid or expired
- Excludes hashed_password from response schema
- Uses session middleware to identify current user from session_token

**API Endpoint - PUT /api/users/me**
- Requires valid session token via middleware authentication
- Request body: JSON with optional fields full_name, email, password (partial updates)
- Validates provided fields: email format/uniqueness, password length, full_name non-empty
- Returns 200 OK with updated user object (id, email, full_name, updated_at) on success
- Returns 400 Bad Request for validation failures
- Returns 401 Unauthorized if session invalid
- Returns 409 Conflict if email change conflicts with another user's email
- Only updates fields present in request body - allows single-field updates
- Password hashed before storage if provided

**Frontend - Registration Page (/register)**
- Form with three input fields: Full Name (text), Email (email), Password (password)
- Register button submits form via POST /api/auth/register
- Link to login page for existing users
- Client-side validation on blur: email format, password length, full_name presence
- Displays validation errors inline below each field
- Displays general API errors in message box above form
- On success: stores session token, updates auth state, redirects to /dashboard
- Uses Vue 3 Composition API with reactive form state
- Styled with Tailwind CSS utility classes

**Frontend - Login Page (/login)**
- Form with two input fields: Email (email), Password (password)
- Login button submits form via POST /api/auth/login
- Link to registration page for new users
- Client-side validation on blur: email format, password non-empty
- Displays validation errors inline below each field
- Displays authentication errors in message box above form
- On success: stores session token, updates auth state, redirects to /dashboard
- Public route - authenticated users redirected to dashboard if visiting this page
- Uses Vue 3 Composition API with composable for auth service

**Frontend - Profile Page (/profile)**
- Protected route requiring authentication via route guard
- Display section shows current full_name and email (read-only)
- Edit form with three fields: Full Name, Email, Password (all optional for partial updates)
- Save button submits changes via PUT /api/users/me
- Client-side validation before submission
- Success message displayed after successful update
- Validation errors displayed inline per field
- Password field empty by default - only updated if user provides new password
- Uses composable for user profile service API calls
- Styled with Tailwind CSS following consistent design patterns

**Frontend - Dashboard Page (/dashboard)**
- Protected route requiring authentication via route guard
- Welcome message: "Welcome, [User's Full Name]" using current user data from auth state
- Navigation component with user info display and logout link
- Placeholder content indicating future dashboard features
- Serves as landing page after login/registration
- Layout structure follows consistent page template pattern
- Uses auth composable to access current user information

**Frontend - Route Guards**
- beforeEach navigation guard checks authentication status
- Protected routes (/dashboard, /profile) require valid session
- Unauthenticated access to protected routes redirects to /login
- Public routes (/login, /register) redirect authenticated users to /dashboard
- Route guard checks session validity by verifying token exists and not expired
- Failed session validation clears auth state and redirects to login

**Frontend - Authentication Composable**
- Composable manages current user state and authentication status
- Provides: currentUser (reactive ref), isAuthenticated (computed), login(), register(), logout(), fetchCurrentUser()
- Stores session token in localStorage or sessionStorage
- Includes session token in API request headers
- Handles 401 responses globally by clearing auth state and redirecting
- Exports reactive state for use across components
- Implements single source of truth for authentication state

**Frontend - Navigation Component**
- Displays user's full name when authenticated
- Shows logout button/link when authenticated
- Logout click calls logout() from auth composable
- Navigates to appropriate pages based on auth state
- Reusable component included in authenticated page layouts
- Styled consistently with Tailwind CSS

**Password Security Implementation**
- Use bcrypt with minimum 12 salt rounds or argon2 for hashing
- Never store plain text passwords in database or logs
- Hash passwords immediately upon receipt in backend
- Verify passwords using timing-safe comparison (bcrypt.checkpw or equivalent)
- Never return hashed passwords in API responses (exclude from Pydantic schemas)
- Password requirements: minimum 2 characters (no complexity rules for MVP simplicity)

**Session Token Generation**
- Generate tokens using secrets.token_urlsafe(32) or equivalent cryptographically secure method
- Ensure minimum 32 bytes of randomness (token length approximately 43 characters base64-encoded)
- Check uniqueness before inserting into sessions table
- Store token in database for server-side validation
- Transmit via HTTP-only secure cookie (preferred) or Authorization header
- Set cookie attributes: HttpOnly=true, Secure=true (HTTPS), SameSite=Lax

**Validation Rules Summary**
- Full Name: Required, non-empty after trim, max 255 characters
- Email: Required, valid format (contains @, valid structure), unique (case-insensitive), max 255 characters
- Password: Required on registration/login, minimum 2 characters, no maximum (hashed), no complexity requirements
- Server-side validation always performed regardless of client-side validation
- Client-side validation provides immediate UX feedback but not relied upon for security
- Error messages specific to field and actionable for user

**Error Response Format**
- Consistent JSON structure: {"error": {"message": "User-friendly message", "field": "field_name", "code": "ERROR_CODE"}}
- HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 409 Conflict, 500 Internal Server Error
- User-facing messages never expose technical details or security information
- Generic messages for authentication failures to prevent email enumeration
- Field-specific errors returned when validation fails on specific inputs

**Command-Line Account Deletion Script**
- Python script at backend/scripts/delete_user.py
- Usage: python backend/scripts/delete_user.py --email user@example.com
- Accepts email as required command-line argument
- Looks up user by email (case-insensitive)
- Displays user details if found: id, email, full_name, created_at
- Deletes all associated sessions (cascade or explicit)
- Deletes user record from database
- Displays success message on completion
- Handles errors: database connection failures, user not found, invalid email format
- No user confirmation prompt - immediate deletion
- Exit codes: 0 for success, 1 for errors

## Visual Design
No visual assets provided. UI will follow SimpleCRM's clean, minimal design using Tailwind CSS utility classes with focus on usability and clarity.

## Existing Code to Leverage

**FastAPI Framework Patterns**
- Use FastAPI's dependency injection system for database sessions and authentication middleware
- Leverage Pydantic models for automatic request validation and serialization
- Utilize FastAPI's exception handlers for consistent error responses
- Take advantage of automatic OpenAPI/Swagger documentation generation
- Follow FastAPI router organization patterns for modular endpoint definitions

**SQLAlchemy ORM Best Practices**
- Use declarative base for model definitions with clear relationships
- Implement created_at and updated_at timestamps on all models per standards
- Define appropriate indexes on frequently queried columns (email, session_token, user_id, expires_at)
- Use foreign key constraints with cascade behaviors for data integrity
- Leverage SQLAlchemy sessions with context managers for proper transaction handling

**Vue 3 Composition API Patterns**
- Create reusable composables for authentication state and API services
- Use reactive refs and computed properties for state management
- Implement composables as single source of truth for shared state
- Follow Vue Router conventions for route definitions and navigation guards
- Structure components with clear separation: template, script setup, style

**Python Security Libraries**
- Use bcrypt library (import bcrypt) with bcrypt.hashpw() and bcrypt.checkpw()
- Use secrets module for cryptographically secure token generation (secrets.token_urlsafe())
- Leverage Python's hashlib for any additional hashing needs
- Consider passlib as alternative password hashing library with unified interface

**Tailwind CSS Utility Patterns**
- Apply consistent spacing, color, and typography utilities across forms
- Use Tailwind form plugin classes for input styling consistency
- Implement responsive design with Tailwind's mobile-first breakpoint utilities
- Create consistent button styles using Tailwind color and padding utilities
- Apply focus states and transitions for better user experience

## Out of Scope
- Email verification workflow or confirmation emails
- Password reset or "forgot password" functionality
- Social login integration (Google, GitHub, Facebook, etc.)
- Two-factor authentication (2FA) or multi-factor authentication
- Profile pictures, avatars, or file uploads
- In-app account deletion interface or self-service account deletion
- "Log out all devices" or "log out everywhere" functionality
- Rate limiting on login attempts or endpoint throttling
- Account lockout after failed login attempts or brute force protection
- Password complexity requirements beyond 2 character minimum
- Password strength indicator or real-time password validation feedback
- "Remember me" checkbox or variable session duration options
- Email notifications for login, profile changes, or security events
- User roles, permissions, or access control systems
- Multi-tenancy, organization accounts, or team features
- Session activity logs or login history tracking
- Account recovery questions or alternative authentication methods
- CAPTCHA or bot prevention mechanisms
- IP-based access restrictions or geolocation features
- Audit logging for user actions beyond basic timestamps
