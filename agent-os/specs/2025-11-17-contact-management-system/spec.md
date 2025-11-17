# Specification: Contact Management System

## Goal
Build a complete CRUD contact management system with searchable list view, quick preview panel, pipeline stage tracking, and user-specific data isolation that integrates seamlessly with the existing authentication system.

## User Stories
- As a user, I want to create, view, update, and delete contacts with fields like name, email, phone, company, job title, website, notes, and pipeline stage so that I can manage my business relationships effectively
- As a user, I want to search contacts by name, email, or company and filter by pipeline stage so that I can quickly find the contacts I need
- As a user, I want to view contact details in a quick preview panel without leaving the contact list page so that I can efficiently browse through my contacts

## Specific Requirements

**Contact Data Model**
- Create a Contact model with fields: name (required), email (required, validated format), phone, company (text field), job_title, website (URL validation), notes (text area), pipeline_stage (enum: Lead, Qualified, Proposal, Client), user_id (foreign key to User)
- Include created_at and updated_at timestamp fields following existing User model pattern
- Add database indexes on user_id, email, name, company, and pipeline_stage for query performance
- Enforce NOT NULL constraint on name and email fields at database level
- Implement foreign key relationship with CASCADE delete behavior to User model

**CRUD API Endpoints**
- POST /api/contacts - Create new contact (requires authentication, associates with current user, returns 201 on success)
- GET /api/contacts - List all contacts for current user with pagination, search, and filter query parameters (page, limit, search, stage)
- GET /api/contacts/:id - Get single contact by ID (verify ownership by current user, return 404 if not found or unauthorized)
- PUT /api/contacts/:id - Update contact by ID (verify ownership, support partial updates, return 200 on success)
- DELETE /api/contacts/:id - Hard delete contact by ID (verify ownership, permanently remove from database, return 204 on success)
- All endpoints follow RESTful conventions and use plural resource naming (/contacts)

**Request/Response Schemas**
- Create Pydantic schemas: ContactCreateSchema (name, email, phone, company, job_title, website, notes, pipeline_stage), ContactUpdateSchema (all fields optional for partial updates), ContactResponseSchema (all fields plus id, user_id, created_at, updated_at)
- Use Pydantic's EmailStr validator for email field
- Use Field validators with min_length/max_length constraints (name: max 255, email: max 255, company: max 255, job_title: max 255, website: max 500, notes: max 5000)
- Implement enum validation for pipeline_stage with allowed values: Lead, Qualified, Proposal, Client

**Contact Service Layer**
- Create ContactService class following existing UserService pattern with static methods
- Implement methods: create_contact, get_contact_by_id, get_contacts_for_user (with pagination, search, filter), update_contact, delete_contact
- Use SQLAlchemy queries with proper filtering by user_id to enforce data isolation
- Implement case-insensitive search using func.lower() for name, email, and company fields
- Add pagination logic with default limit of 50 contacts per page

**Authentication and Authorization**
- Reuse existing get_current_user dependency from app/dependencies.py for all contact endpoints
- Ensure all contact operations are scoped to the authenticated user (user_id filter on queries)
- Return 401 Unauthorized for missing/invalid/expired session tokens
- Return 404 Not Found when contact doesn't exist or doesn't belong to current user (don't expose existence to unauthorized users)

**Contact List View (Frontend)**
- Create ContactsView.vue page with master-detail layout (contact list on left/main area, preview panel on right/side)
- Display contacts in a paginated table with columns: Name, Email, Company, Pipeline Stage
- Include search input field that searches across name, email, and company fields simultaneously
- Add pipeline stage filter dropdown with options: All, Lead, Qualified, Proposal, Client
- Implement pagination controls (Previous, Next, page numbers) at bottom of list
- Update URL query parameters for search, filter, and page to enable bookmarking and back/forward navigation

**Quick Preview Panel**
- Display preview panel on the right side of contact list that shows full contact details when a contact is clicked
- Show all contact fields: name, email, phone, company, job_title, website, notes, pipeline_stage, created_at, updated_at
- Include Edit and Delete action buttons in preview panel
- Update preview panel content without page navigation using Vue reactivity
- Highlight selected contact row in the list view
- Show empty state message when no contact is selected

**Contact Create/Edit Forms**
- Create ContactForm.vue component for both create and edit operations (reuse component with different modes)
- Reuse existing FormInput.vue component for text fields following LoginView.vue pattern
- Include dropdown/select input for pipeline_stage field with four options
- Include textarea input for notes field with appropriate styling
- Implement client-side validation: required fields (name, email), email format, field length limits
- Show field-level error messages using existing error display patterns
- Submit form via API (POST for create, PUT for edit) and handle success/error responses
- Navigate to contact list with newly created/updated contact selected after successful submission

**Search and Filtering Logic**
- Implement debounced search (300ms delay) to avoid excessive API calls while user is typing
- Send search and filter parameters as query strings to GET /api/contacts endpoint
- Backend performs OR search across name, email, and company fields when search term provided
- Backend filters by pipeline_stage when stage filter is not "All"
- Combine search and filter conditions with AND logic
- Display "No contacts found" message when search/filter returns empty results

**Delete Confirmation**
- Show confirmation modal/dialog before executing delete operation
- Display contact name in confirmation message: "Are you sure you want to delete [Contact Name]?"
- Include Cancel and Delete buttons in confirmation dialog
- Execute hard delete via DELETE /api/contacts/:id on confirmation
- Remove contact from list view and clear preview panel after successful deletion
- Show success notification message after deletion

**Styling and UI Consistency**
- Follow existing Tailwind CSS design patterns from LoginView.vue and DashboardView.vue
- Use consistent color scheme: blue-600 for primary actions, gray tones for backgrounds and text
- Apply shadow and rounded corners to cards and containers (shadow, rounded-lg classes)
- Maintain existing form styling with focus states (focus:ring-2, focus:ring-blue-500)
- Reuse NavigationBar component and integrate contact navigation link
- Ensure responsive design works on desktop screens (mobile optimization is out of scope)

## Visual Design
No visual assets provided. Follow existing page layouts and component styling from authentication features.

## Existing Code to Leverage

**User Model and Database Patterns (/home/yaakov/git/SimpleCRM/backend/app/models/user.py)**
- Use SQLAlchemy Base class from app.database module
- Follow column definition patterns: Column(Type, constraints) with created_at and updated_at timestamps
- Implement foreign key relationships using Column(Integer, ForeignKey()) with proper cascade behavior
- Define relationship() for bidirectional access between Contact and User models
- Use __tablename__ convention (plural, lowercase) and include indexes on frequently queried columns

**Authentication Dependencies (/home/yaakov/git/SimpleCRM/backend/app/dependencies.py)**
- Reuse get_current_user() dependency function that extracts Bearer token from Authorization header and validates session
- Import and use as Depends(get_current_user) in all protected contact route handlers
- Leverage returned User object to get user_id for contact ownership filtering
- Follow existing 401 HTTPException pattern for authentication failures

**API Router Patterns (/home/yaakov/git/SimpleCRM/backend/app/routers/users.py)**
- Create new contacts.py router file following same structure with APIRouter(prefix="/api/contacts", tags=["contacts"])
- Use appropriate HTTP methods and status codes (201 for create, 200 for update, 204 for delete, 404 for not found)
- Include comprehensive docstrings with request/response examples following existing pattern
- Handle service layer exceptions and convert to appropriate HTTPException responses
- Import and register router in app/main.py

**Service Layer Patterns (/home/yaakov/git/SimpleCRM/backend/app/services/user_service.py)**
- Create ContactService class with @staticmethod methods following UserService structure
- Accept db: DBSession as first parameter in all service methods
- Use db.query(Model).filter().first() pattern for single record retrieval
- Use db.add(), db.commit(), db.refresh() for create/update operations
- Use db.delete() for delete operations
- Return model instances directly from service methods

**Pydantic Schema Patterns (/home/yaakov/git/SimpleCRM/backend/app/schemas/user.py)**
- Create schemas directory file for contact schemas following user schema structure
- Use Field() with validators (min_length, max_length) for string fields
- Use Optional[] type hints for nullable/optional fields
- Include model_config = ConfigDict(from_attributes=True) for response schemas to enable ORM model conversion
- Separate schemas for create, update, and response operations

**Frontend FormInput Component (/home/yaakov/git/SimpleCRM/frontend/src/components/FormInput.vue)**
- Reuse FormInput.vue component for text, email, and url input fields in contact forms
- Pass label, type, v-model, error, and required props following existing usage
- Implement @blur validation handlers for inline field validation
- Component already handles error display and required field indicators

**Frontend API Service (/home/yaakov/git/SimpleCRM/frontend/src/services/api.js)**
- Use existing apiGet, apiPost, apiPut, apiDelete functions for all contact API calls
- API functions automatically include Authorization header with session token from localStorage
- Handle ApiError exceptions in try-catch blocks and display user-friendly error messages
- Follow existing error handling patterns from LoginView.vue

**Frontend View Patterns (/home/yaakov/git/SimpleCRM/frontend/src/views/LoginView.vue, DashboardView.vue)**
- Structure pages with consistent layout: min-h-screen bg-gray-50 wrapper, max-w-7xl mx-auto container, bg-white shadow rounded-lg cards
- Include NavigationBar component at top of authenticated pages
- Use ref() for reactive state, computed() for derived values, and async/await for API calls
- Implement form validation with separate validation functions and errors ref object
- Show loading states with isSubmitting ref and disabled button states

## Out of Scope
- Activity timeline and interaction history tracking (deferred to Feature #4)
- Automated follow-up reminders and notifications (deferred to Feature #5)
- Revenue tracking fields like deal value, actual revenue, or close date (deferred to Feature #6)
- AI-powered features including interaction parsing and proposal generation (Phase 2)
- Separate Company entity with relational database structure (company remains simple text field)
- Pipeline stage history tracking and audit trail
- Soft-delete functionality with archive/restore capabilities
- Advanced search with multi-field filters, saved searches, or custom sorting (deferred to Feature #13)
- Tags, custom fields, or contact categories beyond specified fields
- Bulk operations on multiple contacts like bulk delete or bulk edit (deferred to Feature #14)
- Export functionality for contacts to CSV or other formats (deferred to Feature #18)
- Drag-and-drop pipeline interface for moving contacts between stages (deferred to Feature #12)
- Email integration, calendar sync, or external service connections (Phase 3)
- Mobile-specific responsive design optimizations (deferred to Feature #19)
- Contact duplicate detection or merge functionality
