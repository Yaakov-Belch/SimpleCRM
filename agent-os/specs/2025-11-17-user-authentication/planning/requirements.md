# Spec Requirements: User Authentication & Account Management

## Initial Description

Implement simple session-based authentication with registration, login, logout, and basic user profile management.

This is the foundational feature for SimpleCRM - all other features depend on having authenticated users. The target users are freelancers and solo consultants who are semi-technical and comfortable with web apps. This is a learning/portfolio project prioritizing simplicity over enterprise-grade complexity.

## Feature Overview

### Purpose
Provide secure user authentication and basic account management capabilities that serve as the foundation for all other SimpleCRM features. Users need to create accounts, log in securely, manage their profile information, and log out when finished.

### Goals
- Enable users to create new accounts with minimal friction (no email verification required)
- Provide secure session-based authentication lasting 7 days
- Allow users to view and edit their basic profile information
- Support simple logout functionality
- Lay the groundwork for all future features that require user context

### Target Users
- Freelancers and independent consultants
- Solo practitioners (lawyers, accountants, coaches, designers)
- Micro service businesses (1-5 person teams)
- Semi-technical users comfortable with web applications

## Requirements Discussion

### First Round Questions

**Q1: Email Verification**
Should users verify their email before accessing the app, or can they use it immediately after registration?

**Answer:** No email verification - immediate access after registration

**Q2: Password Complexity**
What password requirements should we enforce? (e.g., minimum length, special characters, numbers)

**Answer:** No complexity rules - just minimum 2 characters

**Q3: Session Duration**
How long should user sessions last? Should we offer a "remember me" option?

**Answer:** Always 7 days (no "remember me" checkbox needed)

**Q4: Profile Fields**
What user profile information should we collect and allow users to edit? (e.g., name, email, phone, company, profile picture)

**Answer:** Keep it simple - just name, email, password

**Q5: Logout Behavior**
Should logout clear only the current session, or provide option to "log out all devices"?

**Answer:** Just clear current session (no "log out all devices" option)

**Q6: Login Security**
Should we implement rate limiting or account lockout after failed login attempts?

**Answer:** Keep it simple - no rate limiting or account lockout in MVP

**Q7: Post-Login Redirect**
Where should users land after successful login?

**Answer:** Redirect to dashboard (will need placeholder dashboard page)

**Q8: Post-Registration Flow**
After successful registration, should users be auto-logged in, or redirected to login page?

**Answer:** Auto-login and direct to app

**Q9: Out of Scope**
What authentication features should we explicitly exclude from this MVP?

**Answer:** Keep it simple overall. Include command-line script for account deletion (admin tool), but exclude from UI: password reset/forgot password, social login, 2FA, profile pictures, in-app account deletion

**Q10: Visual Assets**
Do you have any design mockups, wireframes, or screenshots?

**Answer:** None provided

### Existing Code to Reference

No similar existing features identified for reference. This is the first feature being implemented in SimpleCRM.

### Follow-up Questions

None required - requirements are clear and comprehensive.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - no visual files to analyze.

## Requirements Summary

### Functional Requirements

#### User Registration
- Users can create new accounts by providing: full name, email address, password
- Email must be unique across the system
- Password must be minimum 2 characters (no complexity requirements)
- Upon successful registration, users are automatically logged in
- After registration and auto-login, users are redirected to dashboard
- No email verification required - immediate app access

#### User Login
- Users log in using email and password credentials
- Successful login creates a session valid for 7 days
- No "remember me" checkbox - all sessions last 7 days by default
- After successful login, users are redirected to dashboard
- Invalid credentials return clear error message
- No rate limiting or account lockout on failed attempts (MVP simplicity)

#### User Profile Management
- Users can view their profile information: full name, email
- Users can edit their profile information: full name, email, password
- Email changes must maintain uniqueness constraint
- Password changes require minimum 2 characters
- Profile updates are validated server-side
- Success/error feedback provided for profile updates

#### User Logout
- Users can log out via logout button/link
- Logout clears only the current session (not all sessions/devices)
- After logout, users are redirected to login page
- Logged-out users cannot access protected pages

#### Session Management
- Sessions are stored server-side (SQLite)
- Session duration: 7 days from login
- Expired sessions require re-authentication
- Protected routes check for valid session
- Invalid/expired sessions redirect to login page

#### Dashboard Placeholder
- Create placeholder dashboard page for post-login redirect
- Basic page structure with navigation
- Displays user's name (e.g., "Welcome, [Full Name]")
- Includes logout button/link
- Serves as landing page and foundation for future dashboard features

### Reusability Opportunities

No existing similar features identified. This is the foundational feature that future features will build upon.

Future features that will reuse authentication components:
- All future pages will use session validation
- Navigation components will display logged-in user info
- All features will use the User model for ownership/association

### Scope Boundaries

**In Scope:**
- User registration (name, email, password)
- User login (email, password)
- Session-based authentication (7-day sessions)
- User profile view and edit (name, email, password)
- User logout (clear current session)
- Protected route middleware
- Placeholder dashboard page
- Command-line script for account deletion (admin tool)
- Server-side validation for all user input
- Clear error messaging for validation failures
- Password hashing using bcrypt or argon2
- Session storage in SQLite

**Out of Scope (Explicitly Excluded from MVP):**
- Email verification workflow
- Password reset / forgot password functionality
- Social login (Google, GitHub, etc.)
- Two-factor authentication (2FA)
- Profile pictures / avatars
- In-app account deletion (UI-based)
- "Log out all devices" functionality
- Rate limiting on login attempts
- Account lockout after failed login attempts
- Password complexity requirements (beyond 2 character minimum)
- "Remember me" checkbox / variable session duration
- Email notifications
- Password strength indicator
- User roles or permissions system
- Multi-tenancy or organization accounts

### Technical Requirements

#### Frontend (Vue.js 3 with Composition API)

**Pages/Views:**
- Login page (`/login`)
  - Email input field
  - Password input field
  - Login button
  - Link to registration page
  - Display validation errors

- Registration page (`/register`)
  - Full name input field
  - Email input field
  - Password input field
  - Register button
  - Link to login page
  - Display validation errors

- Profile page (`/profile`)
  - Display current name and email
  - Edit form for name, email, password
  - Save button
  - Success/error feedback
  - Requires authentication

- Dashboard page (`/dashboard`)
  - Placeholder page showing "Welcome, [User Name]"
  - Navigation with logout link
  - Requires authentication
  - Foundation for future dashboard features

**Components:**
- Form input components (text input, password input)
- Error message display component
- Success message display component
- Navigation component (with user info and logout)
- Protected route wrapper/guard

**Services/Composables:**
- Authentication service (API calls for login, register, logout)
- User profile service (API calls for get/update profile)
- Authentication state management (composable for current user)
- Session validation composable

**Router Configuration:**
- Public routes: `/login`, `/register`
- Protected routes: `/dashboard`, `/profile`
- Route guards checking session validity
- Redirect to login for unauthenticated access
- Redirect to dashboard if authenticated user visits login/register

#### Backend (FastAPI with Python 3.11+)

**API Endpoints:**

- `POST /api/auth/register`
  - Request: `{full_name: string, email: string, password: string}`
  - Response: `{user: {id, email, full_name}, session_token: string}`
  - Creates user, hashes password, creates session, returns user data + session token
  - Status: 201 Created (success), 400 Bad Request (validation error), 409 Conflict (email exists)

- `POST /api/auth/login`
  - Request: `{email: string, password: string}`
  - Response: `{user: {id, email, full_name}, session_token: string}`
  - Validates credentials, creates session, returns user data + session token
  - Status: 200 OK (success), 400 Bad Request (validation error), 401 Unauthorized (invalid credentials)

- `POST /api/auth/logout`
  - Request: Session token in header/cookie
  - Response: `{message: "Logged out successfully"}`
  - Deletes current session
  - Status: 200 OK (success), 401 Unauthorized (no valid session)

- `GET /api/users/me`
  - Request: Session token in header/cookie
  - Response: `{id, email, full_name, created_at, updated_at}`
  - Returns current user's profile information
  - Status: 200 OK (success), 401 Unauthorized (no valid session)

- `PUT /api/users/me`
  - Request: `{full_name?: string, email?: string, password?: string}` + Session token
  - Response: `{id, email, full_name, updated_at}`
  - Updates current user's profile (partial updates allowed)
  - Status: 200 OK (success), 400 Bad Request (validation error), 401 Unauthorized (no valid session), 409 Conflict (email taken)

**Database Models (SQLAlchemy):**

User Model:
- `id`: Integer, Primary Key, Auto-increment
- `email`: String(255), Unique, Not Null, Indexed
- `full_name`: String(255), Not Null
- `hashed_password`: String(255), Not Null
- `created_at`: DateTime, Not Null, Default: Current Timestamp
- `updated_at`: DateTime, Not Null, Default: Current Timestamp, Auto-update on modification

Session Model:
- `id`: Integer, Primary Key, Auto-increment
- `session_token`: String(255), Unique, Not Null, Indexed
- `user_id`: Integer, Foreign Key -> User.id, Not Null, Indexed
- `expires_at`: DateTime, Not Null, Indexed
- `created_at`: DateTime, Not Null, Default: Current Timestamp

**Services/Business Logic:**
- `AuthService`: Handle registration, login, logout, session validation
- `UserService`: Handle profile retrieval and updates
- `PasswordService`: Password hashing and verification using bcrypt or argon2
- `SessionService`: Session creation, validation, deletion, cleanup of expired sessions

**Middleware:**
- Session validation middleware for protected routes
- Extract session token from request (header or cookie)
- Validate session exists and not expired
- Attach user object to request context
- Return 401 if session invalid/expired

**Pydantic Schemas:**
- `UserRegisterSchema`: Validation for registration input
- `UserLoginSchema`: Validation for login input
- `UserUpdateSchema`: Validation for profile update input
- `UserResponseSchema`: Format for user data in responses
- `SessionResponseSchema`: Format for session data in responses

#### Database (SQLite with SQLAlchemy)

**Tables:**
- `users` table (from User model)
- `sessions` table (from Session model)

**Constraints:**
- Unique constraint on `users.email`
- Unique constraint on `sessions.session_token`
- Foreign key constraint: `sessions.user_id` -> `users.id`
- NOT NULL constraints on required fields
- Indexes on: `users.email`, `sessions.session_token`, `sessions.user_id`, `sessions.expires_at`

**Password Security:**
- Use bcrypt or argon2 for password hashing
- Never store plain text passwords
- Hash passwords before database storage
- Verify passwords by comparing hashes

**Session Token Generation:**
- Generate cryptographically secure random tokens
- Ensure uniqueness before storing
- Store token hash (optional security enhancement) or plain token (simpler for MVP)

#### Command-Line Admin Tool

**Account Deletion Script:**
- Python script: `scripts/delete_user.py`
- Usage: `python scripts/delete_user.py --email user@example.com`
- Functionality:
  - Accepts user email as command-line argument
  - Looks up user by email
  - Deletes all associated sessions
  - Deletes user record
  - Cascading delete handled properly
  - Success/error messages
- Location: `backend/scripts/delete_user.py`

### Validation Rules

#### Registration Validation

**Full Name:**
- Required field
- Must not be empty or only whitespace
- Maximum length: 255 characters
- Client-side: Immediate feedback on blur
- Server-side: Validate before database insert

**Email:**
- Required field
- Must be valid email format (contains @, valid domain structure)
- Must be unique (not already registered)
- Case-insensitive uniqueness check
- Maximum length: 255 characters
- Client-side: Format validation on blur
- Server-side: Format validation + uniqueness check

**Password:**
- Required field
- Minimum length: 2 characters
- No maximum length restriction (hashed anyway)
- No complexity requirements (no special chars, numbers, uppercase required)
- Client-side: Length validation on input
- Server-side: Length validation before hashing

#### Login Validation

**Email:**
- Required field
- Must be valid email format
- Client-side: Format validation
- Server-side: Format validation + credential check

**Password:**
- Required field
- Must not be empty
- Client-side: Non-empty check
- Server-side: Credential verification

#### Profile Update Validation

**Full Name (if provided):**
- Must not be empty or only whitespace
- Maximum length: 255 characters
- Client-side: Immediate feedback
- Server-side: Validate before update

**Email (if provided):**
- Must be valid email format
- Must be unique (if changing email)
- Case-insensitive uniqueness check (exclude current user)
- Maximum length: 255 characters
- Client-side: Format validation
- Server-side: Format validation + uniqueness check

**Password (if provided):**
- Minimum length: 2 characters
- No maximum length restriction
- Client-side: Length validation
- Server-side: Length validation before hashing

**Partial Updates:**
- Allow updating only name, only email, only password, or any combination
- Only validate and update fields that are provided
- Do not require all fields to update one field

### Error Handling

#### User-Facing Error Messages

**Registration Errors:**
- "Email address is already registered" (409 Conflict - email exists)
- "Please enter a valid email address" (400 Bad Request - invalid email format)
- "Password must be at least 2 characters" (400 Bad Request - password too short)
- "Full name is required" (400 Bad Request - name missing/empty)
- "An error occurred during registration. Please try again." (500 Internal Server Error)

**Login Errors:**
- "Invalid email or password" (401 Unauthorized - generic message for security)
- "Please enter a valid email address" (400 Bad Request - invalid format)
- "Email and password are required" (400 Bad Request - missing fields)
- "An error occurred during login. Please try again." (500 Internal Server Error)

**Profile Update Errors:**
- "Email address is already in use" (409 Conflict - email taken by another user)
- "Please enter a valid email address" (400 Bad Request - invalid format)
- "Password must be at least 2 characters" (400 Bad Request - password too short)
- "Full name cannot be empty" (400 Bad Request - name empty/whitespace)
- "You must be logged in to update your profile" (401 Unauthorized - session invalid)
- "An error occurred while updating your profile. Please try again." (500 Internal Server Error)

**Session/Authentication Errors:**
- "Your session has expired. Please log in again." (401 Unauthorized - expired session)
- "You must be logged in to access this page" (401 Unauthorized - no session, redirect to login)

#### Error Response Format

All error responses follow consistent JSON format:
```json
{
  "error": {
    "message": "User-friendly error message",
    "field": "field_name",  // Optional: specific field that caused error
    "code": "ERROR_CODE"    // Optional: machine-readable error code
  }
}
```

#### Error Handling Strategy

**Frontend:**
- Display validation errors inline near relevant form fields
- Display general errors in a message box above forms
- Clear previous errors when user starts correcting input
- Handle network errors gracefully with retry option
- Redirect to login page on 401 Unauthorized responses

**Backend:**
- Use FastAPI exception handlers for consistent error responses
- Log errors server-side for debugging (console logging)
- Return appropriate HTTP status codes
- Validate input early and fail fast
- Never expose sensitive information in error messages (no stack traces, database details)
- Generic messages for authentication failures (don't reveal if email exists)

**Session Validation:**
- Check session exists in database
- Check session not expired (expires_at > current time)
- Check session token matches
- Return 401 if any check fails
- Clean up expired sessions periodically (background task or on-demand)

### Security Considerations

**Password Security:**
- Use bcrypt or argon2 for password hashing
- Never log or display passwords
- Never return passwords in API responses
- Hash passwords immediately upon receipt
- Use appropriate salt rounds/iterations (bcrypt: 12 rounds minimum)

**Session Security:**
- Generate cryptographically secure random session tokens (use secrets module)
- Session tokens should be long and unpredictable (minimum 32 bytes)
- Store sessions server-side only
- Set secure HTTP-only cookies for session tokens (if using cookies)
- Set appropriate SameSite cookie attribute
- Expire sessions after 7 days
- Provide logout functionality to invalidate sessions

**API Security:**
- Validate all input server-side
- Sanitize user input to prevent injection attacks
- Use parameterized database queries (SQLAlchemy ORM handles this)
- Return appropriate status codes
- Don't reveal if email exists during login (generic "invalid credentials" message)
- Rate limiting NOT included in MVP (documented as out of scope)

**Data Privacy:**
- Don't log sensitive information (passwords, session tokens)
- Only return necessary user data in API responses
- Exclude hashed_password from all API responses

## Admin Tooling

### Command-Line Account Deletion Script

**Purpose:**
Provide administrators with a safe way to delete user accounts from the command line.

**Script Specifications:**

**File Location:** `backend/scripts/delete_user.py`

**Usage:**
```bash
python backend/scripts/delete_user.py --email user@example.com
```

**Required Arguments:**
- `--email`: Email address of the user account to delete

**Functionality:**
1. Accept email address as command-line argument
2. Connect to database
3. Look up user by email (case-insensitive)
4. If user not found: Display "No user found with email: [email]" and exit
5. If user found: Display user details (id, email, full_name, created_at)
6. No confirmation.
7. All delete requests are immediately executed:
   - Delete all associated sessions (foreign key cascade or explicit deletion)
   - Delete user record
   - Display success message: "User [email] and all associated data deleted successfully"
8. Handle errors gracefully with clear error messages

**Error Handling:**
- Database connection errors: "Failed to connect to database"
- Invalid email format: "Invalid email format provided"
- User not found: "No user found with email: [email]"
- Deletion errors: "Failed to delete user: [error details]"
- Exit with appropriate status codes (0 for success, 1 for errors)

**Security Considerations:**
- Requires file system access to run (inherently restricted to server administrators)
- No authentication required (command-line tool, not web-exposed)
- Confirmation prompt prevents accidental deletions
- Log deletion actions for audit trail (console output sufficient for MVP)

## Dependencies

**Upstream Dependencies (Features this depends on):**
None - this is the foundational feature and the first to be implemented.

**Downstream Dependencies (Features that depend on this):**
All future SimpleCRM features depend on user authentication:
- Contact Management System
- Pipeline Stage Management
- Activity Timeline & Notes
- Follow-Up Reminder System
- Revenue Tracking
- Dashboard & Analytics (full version)
- Email Template Management

All future features will require:
- Valid user session to access
- User ID to associate data with specific users
- Authentication middleware for protected routes
- User context for data filtering and permissions

## Success Criteria

### Definition of Done

This feature is considered complete when all of the following are true:

**Frontend Implementation:**
- Registration page functional with form validation
- Login page functional with credential validation
- Profile page displays and allows editing of user data
- Dashboard placeholder page exists with welcome message
- Navigation includes user name and logout link
- Protected routes redirect unauthenticated users to login
- Authenticated users redirected from login/register to dashboard
- Error messages display clearly for validation failures
- Success messages display for profile updates

**Backend Implementation:**
- All 5 API endpoints implemented and returning correct responses
- User and Session database models created with proper constraints
- Password hashing implemented using bcrypt or argon2
- Session validation middleware protects appropriate endpoints
- Server-side validation for all user input
- Appropriate HTTP status codes returned
- Error responses follow consistent JSON format
- Sessions expire after 7 days
- Command-line deletion script functional

**Testing:**
- Backend unit tests for services (auth, user, password, session)
- Backend integration tests for all API endpoints
- Frontend component tests for forms and validation
- Frontend composable tests for authentication state management
- Manual end-to-end testing of complete user flows

**Documentation:**
- API endpoint documentation (FastAPI auto-generated)
- Command-line script usage documented
- Database schema documented
- Setup instructions for local development

**User Flows Verified:**
1. New user can register, auto-login, and reach dashboard
2. Registered user can log in and reach dashboard
3. Logged-in user can view and edit profile
4. Logged-in user can log out and is redirected to login
5. Unauthenticated user cannot access protected pages
6. Expired sessions redirect to login with appropriate message
7. Administrator can delete user accounts via command-line script

**Quality Checks:**
- No plain text passwords stored or logged
- Email uniqueness enforced
- Session tokens are secure and unpredictable
- Validation errors are clear and helpful
- No sensitive information exposed in error messages
- Code follows project standards (Black formatting, Ruff linting, ESLint)
- All database migrations run successfully
- No console errors in browser (frontend)
- No unhandled exceptions in server logs (backend)

**Acceptance Criteria Met:**
- User can complete registration in under 1 minute
- User can log in in under 30 seconds
- Profile updates save successfully with immediate feedback
- Session remains valid for 7 days without re-authentication
- Logout immediately invalidates session
- All validation errors guide user to correct input
- System handles invalid sessions gracefully
- Admin can delete accounts via command line safely

When all these criteria are met, the feature is ready for integration with future features and the foundation for SimpleCRM is established.
