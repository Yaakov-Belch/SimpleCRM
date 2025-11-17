# Task Breakdown: Contact Management System

## Overview
Total Task Groups: 5
Total Estimated Tasks: 26

## Task List

### Database Layer

#### Task Group 1: Contact Model and Database Schema
**Dependencies:** None (leverages existing User model and authentication system)

- [ ] 1.0 Complete database layer for contacts
  - [ ] 1.1 Write 2-8 focused tests for Contact model functionality
    - Limit to 2-8 highly focused tests maximum
    - Test only critical model behaviors: contact creation with required fields, email format validation, user association, pipeline stage enum validation
    - Skip exhaustive coverage of all edge cases and optional field combinations
    - File: `backend/tests/test_models/test_contact.py`
  - [ ] 1.2 Create Contact model with all required fields and validations
    - Fields: id (primary key), name (required, max 255), email (required, max 255), phone (optional, max 50), company (optional, max 255), job_title (optional, max 255), website (optional, max 500), notes (optional, max 5000), pipeline_stage (enum: Lead, Qualified, Proposal, Client), user_id (foreign key), created_at, updated_at
    - Validations: NOT NULL on name and email, email format validation, URL validation for website
    - File: `backend/app/models/contact.py`
    - Reuse pattern from: `backend/app/models/user.py`
  - [ ] 1.3 Create database migration for contacts table
    - Add indexes on: user_id, email, name, company, pipeline_stage for query performance
    - Foreign key: user_id references users(id) with CASCADE delete
    - NOT NULL constraints on name and email columns
    - File: `backend/alembic/versions/[timestamp]_create_contacts_table.py`
    - Follow migration patterns from existing User table migrations
  - [ ] 1.4 Set up bidirectional relationship between Contact and User
    - Contact belongs_to User (many-to-one via user_id foreign key)
    - User has_many Contacts (one-to-many relationship)
    - Add relationship() definitions in both models
  - [ ] 1.5 Ensure database layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify migration runs successfully with `alembic upgrade head`
    - Verify rollback works with `alembic downgrade -1`
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Contact model enforces required fields and validations
- Migration creates table with proper indexes and constraints
- Bidirectional relationship between Contact and User works
- Migration is reversible

---

### Backend Service and Schema Layer

#### Task Group 2: Pydantic Schemas and Validation
**Dependencies:** Task Group 1

- [ ] 2.0 Complete Pydantic schemas for Contact API
  - [ ] 2.1 Write 2-8 focused tests for schema validation
    - Limit to 2-8 highly focused tests maximum
    - Test only critical validations: required fields, email format (EmailStr), field length limits, pipeline_stage enum validation
    - Skip exhaustive testing of all field combinations
    - File: `backend/tests/test_schemas/test_contact.py`
  - [ ] 2.2 Create ContactCreateSchema for contact creation
    - Fields: name (required, max_length=255), email (required, EmailStr, max_length=255), phone (optional, max_length=50), company (optional, max_length=255), job_title (optional, max_length=255), website (optional, HttpUrl, max_length=500), notes (optional, max_length=5000), pipeline_stage (enum: Lead, Qualified, Proposal, Client, default="Lead")
    - Use Pydantic Field() with validators
    - File: `backend/app/schemas/contact.py`
    - Reuse pattern from: `backend/app/schemas/user.py`
  - [ ] 2.3 Create ContactUpdateSchema for partial updates
    - All fields optional (Optional[]) for partial update support
    - Same validators as ContactCreateSchema
    - At least one field must be provided (custom validator)
  - [ ] 2.4 Create ContactResponseSchema for API responses
    - Include all fields from ContactCreateSchema plus: id, user_id, created_at, updated_at
    - Add model_config = ConfigDict(from_attributes=True) for ORM conversion
  - [ ] 2.5 Create ContactListResponseSchema for paginated lists
    - Fields: contacts (list of ContactResponseSchema), total (int), page (int), limit (int), has_more (bool)
  - [ ] 2.6 Ensure schema tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify email validation works with EmailStr
    - Verify pipeline_stage enum validation
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Schemas enforce field length limits and format validation
- Pipeline stage enum validation works correctly
- Partial updates work with ContactUpdateSchema
- ORM-to-schema conversion works with ContactResponseSchema

---

#### Task Group 3: Contact Service Layer
**Dependencies:** Task Groups 1, 2

- [ ] 3.0 Complete Contact service layer with business logic
  - [ ] 3.1 Write 2-8 focused tests for ContactService methods
    - Limit to 2-8 highly focused tests maximum
    - Test only critical service methods: create_contact, get_contacts_for_user with search/filter, update_contact, delete_contact
    - Skip exhaustive testing of all parameter combinations
    - File: `backend/tests/test_services/test_contact_service.py`
  - [ ] 3.2 Create ContactService class with static methods
    - Follow pattern from: `backend/app/services/user_service.py`
    - All methods accept db: Session as first parameter
    - File: `backend/app/services/contact_service.py`
  - [ ] 3.3 Implement create_contact method
    - Accept: db, user_id, contact_data (ContactCreateSchema)
    - Validate user_id exists
    - Create contact with user association
    - Return created Contact model instance
  - [ ] 3.4 Implement get_contact_by_id method
    - Accept: db, contact_id, user_id
    - Filter by both contact_id and user_id for ownership verification
    - Return Contact or None if not found/unauthorized
  - [ ] 3.5 Implement get_contacts_for_user method with pagination, search, and filter
    - Accept: db, user_id, page (default=1), limit (default=50, max=100), search (optional), stage (optional)
    - Filter by user_id for data isolation
    - Implement case-insensitive search using func.lower() on name, email, company (OR logic)
    - Filter by pipeline_stage if stage provided and not "All"
    - Combine search and filter with AND logic
    - Return tuple: (list of Contacts, total count)
  - [ ] 3.6 Implement update_contact method
    - Accept: db, contact_id, user_id, update_data (ContactUpdateSchema)
    - Verify ownership (user_id match)
    - Support partial updates (only update provided fields)
    - Return updated Contact or None if not found/unauthorized
  - [ ] 3.7 Implement delete_contact method
    - Accept: db, contact_id, user_id
    - Verify ownership (user_id match)
    - Hard delete (permanent removal)
    - Return True if deleted, False if not found/unauthorized
  - [ ] 3.8 Ensure service layer tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify user data isolation (users can't access other users' contacts)
    - Verify search and filter logic works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- All service methods enforce user ownership verification
- Search performs case-insensitive OR search across name, email, company
- Filter combines with search using AND logic
- Pagination works correctly with total count

---

### API Layer

#### Task Group 4: Contact API Endpoints
**Dependencies:** Task Groups 1, 2, 3

- [ ] 4.0 Complete Contact REST API endpoints
  - [ ] 4.1 Write 2-8 focused tests for API endpoints
    - Limit to 2-8 highly focused tests maximum
    - Test only critical endpoints: POST /api/contacts (create), GET /api/contacts (list with search/filter), GET /api/contacts/:id (single), PUT /api/contacts/:id (update), DELETE /api/contacts/:id (delete)
    - Test authentication requirement (401 without token)
    - Test ownership verification (404 for other user's contact)
    - Skip exhaustive testing of all scenarios
    - File: `backend/tests/test_routers/test_contacts.py`
  - [ ] 4.2 Create contacts router with APIRouter configuration
    - Configure: APIRouter(prefix="/api/contacts", tags=["contacts"])
    - Import get_current_user dependency from app.dependencies
    - File: `backend/app/routers/contacts.py`
    - Follow pattern from: `backend/app/routers/users.py`
  - [ ] 4.3 Implement POST /api/contacts endpoint (create contact)
    - Requires authentication: current_user = Depends(get_current_user)
    - Accept ContactCreateSchema in request body
    - Call ContactService.create_contact with current_user.id
    - Return 201 Created with ContactResponseSchema
    - Handle validation errors with 400 Bad Request
    - Include comprehensive docstring with request/response examples
  - [ ] 4.4 Implement GET /api/contacts endpoint (list contacts)
    - Requires authentication
    - Accept query parameters: page (int, default=1), limit (int, default=50), search (optional string), stage (optional string)
    - Call ContactService.get_contacts_for_user with current_user.id and query params
    - Return 200 OK with ContactListResponseSchema (contacts list, pagination metadata)
    - Handle invalid query params with 400 Bad Request
  - [ ] 4.5 Implement GET /api/contacts/:id endpoint (get single contact)
    - Requires authentication
    - Path parameter: contact_id (int)
    - Call ContactService.get_contact_by_id with contact_id and current_user.id
    - Return 200 OK with ContactResponseSchema if found and owned
    - Return 404 Not Found if not found or not owned (don't expose existence)
  - [ ] 4.6 Implement PUT /api/contacts/:id endpoint (update contact)
    - Requires authentication
    - Path parameter: contact_id (int)
    - Accept ContactUpdateSchema in request body
    - Call ContactService.update_contact with contact_id, current_user.id, and update data
    - Return 200 OK with ContactResponseSchema if successful
    - Return 404 Not Found if not found or not owned
    - Handle validation errors with 400 Bad Request
  - [ ] 4.7 Implement DELETE /api/contacts/:id endpoint (delete contact)
    - Requires authentication
    - Path parameter: contact_id (int)
    - Call ContactService.delete_contact with contact_id and current_user.id
    - Return 204 No Content if successful
    - Return 404 Not Found if not found or not owned
  - [ ] 4.8 Register contacts router in main.py
    - Import contacts router
    - Add: app.include_router(contacts.router)
    - File: `backend/app/main.py`
  - [ ] 4.9 Ensure API layer tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify all endpoints require authentication
    - Verify ownership checks work (users can't access other users' contacts)
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- All CRUD operations work correctly
- Proper HTTP status codes returned (201, 200, 204, 400, 401, 404)
- Authentication required for all endpoints
- User ownership enforced on all operations
- Search and filter query parameters work
- Router registered in main.py

---

### Frontend Layer

#### Task Group 5: Frontend API Service and Composables
**Dependencies:** Task Group 4

- [ ] 5.0 Complete frontend API integration
  - [ ] 5.1 Add contact API methods to api.js service
    - Methods: createContact, getContacts, getContactById, updateContact, deleteContact
    - Use existing apiGet, apiPost, apiPut, apiDelete functions
    - Include query parameter handling for list endpoint (page, limit, search, stage)
    - File: `frontend/src/services/api.js`
    - Follow pattern from existing user API methods
  - [ ] 5.2 Create useContacts composable for state management
    - Reactive state: contacts (ref), selectedContact (ref), isLoading (ref), error (ref), pagination (ref with page, limit, total, hasMore)
    - Methods: fetchContacts, selectContact, clearSelection
    - Handle API errors with user-friendly messages
    - File: `frontend/src/composables/useContacts.js`

**Acceptance Criteria:**
- API service methods make correct HTTP calls with proper parameters
- Composable manages contact list state reactively
- Error handling provides user-friendly messages
- Pagination state tracks current page and total count

---

#### Task Group 6: Contact List View and Search/Filter UI
**Dependencies:** Task Groups 4, 5

- [ ] 6.0 Complete contact list view with search and filter
  - [ ] 6.1 Write 2-8 focused tests for ContactsView component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors: component renders with contact list, search input updates results (debounced), filter dropdown updates results, pagination controls work
    - Skip exhaustive testing of all user interactions
    - File: `frontend/tests/views/ContactsView.spec.js`
  - [ ] 6.2 Create ContactsView.vue with master-detail layout
    - Layout: NavigationBar at top, main content area with 2-column layout (contact list left 60%, preview panel right 40%)
    - Use Tailwind classes: min-h-screen bg-gray-50, max-w-7xl mx-auto, grid grid-cols-3 gap-6
    - File: `frontend/src/views/ContactsView.vue`
    - Follow layout pattern from: `frontend/src/views/DashboardView.vue`
  - [ ] 6.3 Implement search input field
    - Input field with placeholder "Search by name, email, or company..."
    - Debounced search with 300ms delay using lodash.debounce or custom debounce
    - Update URL query parameter ?search=term
    - Trigger API call on search change
    - Clear search button (X icon) when search has value
  - [ ] 6.4 Implement pipeline stage filter dropdown
    - Options: All, Lead, Qualified, Proposal, Client
    - Default: All
    - Update URL query parameter ?stage=value
    - Trigger API call on stage change
    - Style with existing form input patterns
  - [ ] 6.5 Build contact list table
    - Columns: Name, Email, Company, Pipeline Stage
    - Display contacts from useContacts composable
    - Clickable rows that call selectContact method
    - Highlight selected row with bg-blue-50 border-blue-500
    - Show loading spinner when isLoading is true
    - Show "No contacts found" message when list is empty after search/filter
    - Use Tailwind table classes: table-auto, divide-y, divide-gray-200
  - [ ] 6.6 Implement pagination controls
    - Display at bottom of contact list
    - Show: Previous button, page numbers (current and adjacent), Next button
    - Update URL query parameter ?page=number
    - Disable Previous when on first page, Next when on last page
    - Show total count: "Showing X-Y of Z contacts"
    - Style with existing button patterns
  - [ ] 6.7 Add "New Contact" button
    - Position at top-right of contact list area
    - Navigate to /contacts/new route on click
    - Style with primary blue button (bg-blue-600 hover:bg-blue-700)
  - [ ] 6.8 Implement URL query parameter synchronization
    - Read query params on component mount (page, search, stage)
    - Update URL when search, filter, or page changes (use vue-router)
    - Enable browser back/forward navigation
    - Enable bookmarking of filtered/searched views
  - [ ] 6.9 Ensure ContactsView tests pass
    - Run ONLY the 2-8 tests written in 6.1
    - Verify search debounce works (300ms delay)
    - Verify filter updates results
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 6.1 pass
- Contact list displays in table format with proper columns
- Search input triggers debounced API calls
- Filter dropdown updates results immediately
- Pagination controls work and update URL
- Selected contact row is highlighted
- URL query parameters enable bookmarking and navigation
- New Contact button navigates correctly

---

#### Task Group 7: Contact Preview Panel
**Dependencies:** Task Groups 5, 6

- [ ] 7.0 Complete contact preview panel
  - [ ] 7.1 Write 2-8 focused tests for ContactPreview component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors: panel displays contact details, Edit button navigates to edit route, Delete button shows confirmation
    - Skip exhaustive testing of all field display variations
    - File: `frontend/tests/components/ContactPreview.spec.js`
  - [ ] 7.2 Create ContactPreview.vue component
    - Accept props: contact (object or null)
    - Display all contact fields with labels: Name, Email, Phone, Company, Job Title, Website (as clickable link), Notes (multi-line), Pipeline Stage (with colored badge)
    - Show formatted timestamps: Created At, Updated At
    - Show empty state message when contact is null: "Select a contact to view details"
    - File: `frontend/src/components/ContactPreview.vue`
  - [ ] 7.3 Add Edit and Delete action buttons to preview panel
    - Edit button: Navigate to /contacts/:id/edit route
    - Delete button: Emit delete event (handle in parent component)
    - Position buttons at top-right of panel
    - Style with secondary (Edit) and danger (Delete) button styles
  - [ ] 7.4 Style preview panel with consistent design
    - Container: bg-white shadow rounded-lg p-6
    - Field labels: text-sm font-medium text-gray-700
    - Field values: text-base text-gray-900
    - Empty state: centered text with icon
    - Pipeline stage badge: colored pill (Lead=yellow, Qualified=blue, Proposal=purple, Client=green)
    - Website as clickable link with external icon
  - [ ] 7.5 Integrate preview panel in ContactsView
    - Position in right column (40% width) using grid layout
    - Pass selectedContact from useContacts composable
    - Make panel sticky (sticky top-6) so it stays visible during scroll
    - Update preview reactively when selectedContact changes
  - [ ] 7.6 Ensure ContactPreview tests pass
    - Run ONLY the 2-8 tests written in 7.1
    - Verify empty state displays correctly
    - Verify contact details display correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 7.1 pass
- Preview panel displays all contact fields with proper formatting
- Empty state shows when no contact selected
- Action buttons work correctly
- Panel is sticky and stays visible during scroll
- Pipeline stage displays with colored badge

---

#### Task Group 8: Contact Create/Edit Forms
**Dependencies:** Task Groups 5, 7

- [ ] 8.0 Complete contact create and edit forms
  - [ ] 8.1 Write 2-8 focused tests for ContactForm component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors: form renders with fields, form submission creates/updates contact, validation shows errors for required fields
    - Skip exhaustive testing of all field validations
    - File: `frontend/tests/components/ContactForm.spec.js`
  - [ ] 8.2 Create ContactForm.vue component for create/edit operations
    - Props: contactId (optional, for edit mode), initialData (optional)
    - Mode detection: edit mode if contactId provided, create mode otherwise
    - File: `frontend/src/components/ContactForm.vue`
    - Reuse FormInput component from: `frontend/src/components/FormInput.vue`
  - [ ] 8.3 Add form fields using FormInput component
    - Name: FormInput with type="text", required
    - Email: FormInput with type="email", required
    - Phone: FormInput with type="tel"
    - Company: FormInput with type="text"
    - Job Title: FormInput with type="text"
    - Website: FormInput with type="url"
    - Notes: textarea element (not FormInput) with rows="4"
    - Pipeline Stage: select dropdown with options: Lead, Qualified, Proposal, Client
  - [ ] 8.4 Implement client-side validation
    - Required fields: name, email (show "This field is required")
    - Email format validation using regex or HTML5 validation
    - Field length limits matching backend schema (name: 255, email: 255, etc.)
    - URL format validation for website field
    - Display field-level error messages below inputs (follow LoginView pattern)
    - Store errors in ref object: errors = ref({})
  - [ ] 8.5 Implement form submission logic
    - Create mode: Call api.createContact with form data
    - Edit mode: Call api.updateContact with contactId and form data
    - Handle loading state with isSubmitting ref (disable button during submit)
    - Handle success: Show success notification, navigate to /contacts with new/updated contact selected
    - Handle errors: Display API error messages in errors ref
    - Use try-catch with ApiError exception handling
  - [ ] 8.6 Create ContactCreateView.vue wrapper
    - Simple view that includes ContactForm component in create mode
    - Add NavigationBar and page title "New Contact"
    - File: `frontend/src/views/ContactCreateView.vue`
  - [ ] 8.7 Create ContactEditView.vue wrapper
    - Simple view that includes ContactForm component in edit mode
    - Get contactId from route params
    - Fetch contact data on mount and pass as initialData
    - Add NavigationBar and page title "Edit Contact"
    - Show loading spinner while fetching contact data
    - Handle 404 error if contact not found
    - File: `frontend/src/views/ContactEditView.vue`
  - [ ] 8.8 Style forms with consistent design
    - Follow existing form styling from: `frontend/src/views/LoginView.vue`
    - Container: bg-white shadow rounded-lg p-6 max-w-2xl mx-auto
    - Input spacing: space-y-4
    - Submit button: bg-blue-600 hover:bg-blue-700 w-full
    - Cancel button: secondary style, link to /contacts
  - [ ] 8.9 Ensure ContactForm tests pass
    - Run ONLY the 2-8 tests written in 8.1
    - Verify form validation works for required fields
    - Verify form submission calls correct API method
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 8.1 pass
- Form component works in both create and edit modes
- Client-side validation shows field-level errors
- Form submission creates/updates contact via API
- Success redirects to contact list with new/updated contact selected
- Loading states prevent double-submission

---

#### Task Group 9: Delete Confirmation Modal
**Dependencies:** Task Group 7

- [ ] 9.0 Complete delete confirmation functionality
  - [ ] 9.1 Write 2-8 focused tests for ConfirmDialog component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors: dialog displays with message, Cancel button closes dialog, Confirm button emits confirm event
    - Skip exhaustive testing of all variations
    - File: `frontend/tests/components/ConfirmDialog.spec.js`
  - [ ] 9.2 Create reusable ConfirmDialog.vue component
    - Props: isOpen (boolean), title (string), message (string), confirmText (string, default="Confirm"), cancelText (string, default="Cancel")
    - Emits: confirm, cancel
    - Modal overlay with backdrop (fixed inset-0 bg-gray-500 bg-opacity-75)
    - Modal dialog centered with white card (max-w-md)
    - Close on backdrop click or Cancel button
    - File: `frontend/src/components/ConfirmDialog.vue`
  - [ ] 9.3 Implement delete confirmation in ContactsView
    - State: showDeleteConfirm (ref), contactToDelete (ref)
    - Delete button in preview panel sets contactToDelete and opens dialog
    - Confirmation message: "Are you sure you want to delete {contact.name}?"
    - On confirm: Call api.deleteContact, remove from list, clear preview, show success notification
    - On cancel: Close dialog, clear contactToDelete
  - [ ] 9.4 Style modal with accessibility considerations
    - Use semantic HTML: dialog or div with role="dialog"
    - Focus trap within modal (focus stays inside when open)
    - Close on Escape key press
    - Confirm button with danger style (bg-red-600 hover:bg-red-700)
    - Cancel button with secondary style
  - [ ] 9.5 Ensure ConfirmDialog tests pass
    - Run ONLY the 2-8 tests written in 9.1
    - Verify dialog opens and closes correctly
    - Verify confirm action emits event
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 9.1 pass
- Delete confirmation dialog displays contact name
- Cancel button closes dialog without deleting
- Confirm button deletes contact and updates UI
- Success notification shown after deletion
- Preview panel cleared after deletion

---

#### Task Group 10: Navigation and Routes Integration
**Dependencies:** Task Groups 6, 8

- [ ] 10.0 Complete routing and navigation setup
  - [ ] 10.1 Add contact routes to router configuration
    - /contacts - ContactsView
    - /contacts/new - ContactCreateView
    - /contacts/:id/edit - ContactEditView
    - All routes require authentication (use existing auth guard)
    - File: `frontend/src/router/index.js`
  - [ ] 10.2 Add "Contacts" navigation link to NavigationBar
    - Add link to /contacts route
    - Position after Dashboard link
    - Highlight active route with existing pattern
    - File: `frontend/src/components/NavigationBar.vue`
  - [ ] 10.3 Test navigation flows manually
    - Navigate from Dashboard to Contacts
    - Create new contact from Contacts view
    - Edit contact from preview panel
    - Delete contact and verify redirect
    - Use browser back/forward buttons with query params
    - Verify authentication guard works (redirects to login if not authenticated)

**Acceptance Criteria:**
- All contact routes registered and accessible
- Navigation link in NavigationBar works
- Authentication guard protects all contact routes
- Browser back/forward buttons work with query params
- Active route highlighted in navigation

---

### Testing and Integration

#### Task Group 11: Test Review and Critical Gap Analysis
**Dependencies:** Task Groups 1-10

- [ ] 11.0 Review existing tests and fill critical gaps only
  - [ ] 11.1 Review tests from Task Groups 1-10
    - Review database layer tests (Task 1.1)
    - Review schema tests (Task 2.1)
    - Review service layer tests (Task 3.1)
    - Review API endpoint tests (Task 4.1)
    - Review ContactsView tests (Task 6.1)
    - Review ContactPreview tests (Task 7.1)
    - Review ContactForm tests (Task 8.1)
    - Review ConfirmDialog tests (Task 9.1)
    - Total existing tests: approximately 16-32 tests
  - [ ] 11.2 Analyze test coverage gaps for Contact Management System only
    - Identify critical end-to-end user workflows that lack test coverage
    - Focus ONLY on gaps related to this feature's requirements
    - Prioritize: complete CRUD workflow, search with filter workflow, user data isolation
    - Do NOT assess entire application test coverage
    - Do NOT test edge cases unless business-critical
  - [ ] 11.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration tests for end-to-end workflows:
      - Full CRUD cycle: create contact -> view in list -> edit -> delete
      - Search and filter: search by name -> filter by stage -> paginate results
      - User isolation: verify user can't access another user's contacts
      - Authentication: verify all endpoints require valid session
    - Do NOT write comprehensive coverage for all scenarios
    - Skip: performance tests, accessibility tests, mobile responsiveness
    - Files: `backend/tests/integration/test_contact_workflows.py`, `frontend/tests/integration/contact_workflows.spec.js`
  - [ ] 11.4 Run feature-specific tests only
    - Run ONLY tests related to Contact Management System feature
    - Backend: `pytest backend/tests/test_models/test_contact.py backend/tests/test_schemas/test_contact.py backend/tests/test_services/test_contact_service.py backend/tests/test_routers/test_contacts.py backend/tests/integration/test_contact_workflows.py`
    - Frontend: `npm test -- ContactsView ContactPreview ContactForm ConfirmDialog contact_workflows`
    - Expected total: approximately 26-42 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical user workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 26-42 tests total)
- Critical end-to-end workflows covered: full CRUD cycle, search/filter, user isolation
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on Contact Management System feature
- All backend tests pass independently
- All frontend tests pass independently

---

### Manual Testing and Documentation

#### Task Group 12: Manual Testing and Final Verification
**Dependencies:** Task Groups 1-11

- [ ] 12.0 Perform manual end-to-end testing
  - [ ] 12.1 Test complete CRUD workflow manually
    - Create new contact with all fields
    - Verify contact appears in list
    - Search for contact by name, email, company
    - Filter contacts by each pipeline stage
    - Edit contact and verify changes
    - Delete contact and confirm removal
  - [ ] 12.2 Test user data isolation manually
    - Log in as User A, create contacts
    - Log out, log in as User B
    - Verify User B cannot see User A's contacts
    - Create contacts for User B
    - Log back in as User A, verify contacts are separate
  - [ ] 12.3 Test pagination with large dataset
    - Create 60+ contacts (script or manual)
    - Verify pagination shows correct page numbers
    - Navigate through pages
    - Verify "Previous" and "Next" buttons work
    - Verify page count is accurate
  - [ ] 12.4 Test URL query parameter bookmarking
    - Perform search and filter
    - Copy URL from browser
    - Open URL in new tab
    - Verify search and filter state preserved
    - Test browser back/forward buttons
  - [ ] 12.5 Test error handling and edge cases
    - Try to create contact without required fields
    - Try to submit invalid email format
    - Try to access another user's contact by ID (via URL manipulation)
    - Try to access contact routes without authentication
    - Test API error responses (network errors, server errors)
  - [ ] 12.6 Test UI responsiveness and styling (desktop only)
    - Verify layout works on desktop screen sizes (1024px+)
    - Verify preview panel is sticky during scroll
    - Verify buttons have proper hover states
    - Verify form inputs have proper focus states
    - Verify loading spinners appear during API calls
  - [ ] 12.7 Document any bugs or issues found
    - Create list of bugs found during manual testing
    - Prioritize: critical (blocking), high (major functionality), medium (minor issues), low (cosmetic)
    - Fix critical and high priority bugs before feature completion
    - Log medium and low priority for future sprints

**Acceptance Criteria:**
- All manual test scenarios pass successfully
- User data isolation verified (users can only see own contacts)
- CRUD operations work end-to-end
- Search, filter, and pagination work correctly
- URL bookmarking and navigation work
- Error handling displays user-friendly messages
- No critical or high priority bugs remain
- UI is visually consistent with existing pages

---

## Execution Order

Recommended implementation sequence:

1. **Database Layer** (Task Group 1)
   - Establish data model foundation
   - Create migrations for contacts table
   - ~2-8 tests written

2. **Backend Service and Schema Layer** (Task Groups 2-3)
   - Define API contracts with Pydantic schemas
   - Implement business logic in service layer
   - ~4-16 tests written (cumulative: 6-24)

3. **API Layer** (Task Group 4)
   - Expose REST endpoints for frontend consumption
   - ~2-8 tests written (cumulative: 8-32)

4. **Frontend API Integration** (Task Group 5)
   - Create API service methods and composables
   - No tests written at this stage (composables are simple wrappers)

5. **Frontend UI - List and Search** (Task Group 6)
   - Build contact list view with search/filter
   - ~2-8 tests written (cumulative: 10-40)

6. **Frontend UI - Preview Panel** (Task Group 7)
   - Add preview panel for quick contact details
   - ~2-8 tests written (cumulative: 12-48)

7. **Frontend UI - Forms** (Task Group 8)
   - Build create/edit forms
   - ~2-8 tests written (cumulative: 14-56)

8. **Frontend UI - Delete Confirmation** (Task Group 9)
   - Add delete confirmation modal
   - ~2-8 tests written (cumulative: 16-64)

9. **Navigation and Routes** (Task Group 10)
   - Wire up all routes and navigation
   - No tests written (integration covered in next group)

10. **Testing and Integration** (Task Group 11)
    - Review all tests written so far (16-32 tests)
    - Add up to 10 integration tests for critical workflows
    - Run feature-specific test suite (26-42 tests total)

11. **Manual Testing and Verification** (Task Group 12)
    - Perform end-to-end manual testing
    - Verify all user workflows work correctly
    - Fix critical bugs found

---

## Test Writing Summary

Following the focused test-driven approach outlined in `/home/yaakov/git/SimpleCRM/agent-os/standards/testing/test-writing.md`:

- **Task Groups 1-4 (Backend):** Each writes 2-8 focused tests = 8-32 tests
- **Task Groups 6-9 (Frontend):** Each writes 2-8 focused tests = 8-32 tests
- **Task Group 11 (Integration):** Adds maximum 10 tests for critical gaps
- **Total Expected:** 26-42 tests for entire Contact Management System feature

This minimal, strategic testing approach ensures:
- Critical user workflows are covered
- Development velocity remains high
- Test maintenance burden stays low
- Only business-critical paths are tested during development

---

## Notes

- All file paths are absolute paths from project root: `/home/yaakov/git/SimpleCRM/`
- Follow existing code patterns from User authentication system
- Reuse FormInput component for form fields
- Reuse NavigationBar component for page navigation
- Use Tailwind CSS for all styling (follow existing page styles)
- Use SQLAlchemy for database operations
- Use FastAPI for REST API endpoints
- Use Vue.js 3 Composition API for frontend
- Hard delete contacts (permanent removal from database)
- Enforce user data isolation on all operations
- Search is case-insensitive OR search across name, email, company
- Filter combines with search using AND logic
- Pipeline stages: Lead, Qualified, Proposal, Client
- Pagination default: 50 contacts per page, max 100
- Debounce search input: 300ms delay
- Mobile optimization is out of scope (desktop only)
