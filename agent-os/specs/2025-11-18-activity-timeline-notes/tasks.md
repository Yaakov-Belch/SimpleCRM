# Task Breakdown: Activity Timeline & Notes

## Overview
Total Tasks: 4 major task groups with 38 granular sub-tasks

## Task List

### Database Layer

#### Task Group 1: Data Models and Migrations
**Dependencies:** None

- [x] 1.0 Complete database layer
  - [x] 1.1 Write 2-8 focused tests for Activity and Attachment models
    - Limit to 2-8 highly focused tests maximum
    - Test only critical model behaviors (e.g., activity creation with valid type, contact relationship, attachment file metadata)
    - Skip exhaustive coverage of all methods and edge cases
  - [x] 1.2 Create Activity model (backend/app/models/activity.py)
    - Fields: id (int, PK), contact_id (FK to contacts), type (enum: Call|Meeting|Email|Note), subject (varchar 255), notes (text), activity_date (datetime), created_at (datetime), updated_at (datetime)
    - Validations: type must be one of allowed enum values, subject max 255 chars
    - Foreign key: contact_id with CASCADE delete behavior
    - Indexes: contact_id, type, activity_date for query performance
    - Relationship: belongs_to Contact
    - Follow pattern from: backend/app/models/contact.py
  - [x] 1.3 Create Attachment model (backend/app/models/attachment.py)
    - Fields: id (int, PK), activity_id (FK to activities), original_filename (varchar 255), stored_filename (varchar 255), file_path (varchar 500), file_size (bigint), mime_type (varchar 100), uploaded_at (datetime)
    - Foreign key: activity_id with CASCADE delete behavior
    - Indexes: activity_id for query performance
    - Relationship: belongs_to Activity
    - Follow pattern from: backend/app/models/contact.py
  - [x] 1.4 Set up model relationships
    - Contact has_many Activities (one-to-many)
    - Activity has_many Attachments (one-to-many)
    - Activity belongs_to Contact
    - Attachment belongs_to Activity
    - Verify CASCADE delete behavior
  - [x] 1.5 Create database migration
    - Migration file: Create activities table with all fields and indexes
    - Migration file: Create attachments table with all fields and indexes
    - Add foreign key constraints with CASCADE delete
    - Follow migration pattern from existing migrations
    - Test migration up and down (reversibility)
  - [x] 1.6 Update Contact model to add activities relationship
    - Add relationship: activities = relationship("Activity", back_populates="contact", cascade="all, delete-orphan")
    - File: backend/app/models/contact.py
  - [x] 1.7 Ensure database layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify migrations run successfully
    - Verify relationships work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Activity model has correct fields, validations, and relationships
- Attachment model has correct fields and relationships
- Migrations run successfully (up and down)
- CASCADE delete behavior works (deleting contact deletes activities, deleting activity deletes attachments)
- Foreign key constraints enforced at database level

---

### API Layer

#### Task Group 2: Pydantic Schemas
**Dependencies:** Task Group 1

- [x] 2.0 Complete Pydantic schemas for request/response validation
  - [x] 2.1 Create Activity schemas (backend/app/schemas/activity.py)
    - ActivityCreateSchema: type (Literal["Call", "Meeting", "Email", "Note"]), subject (str, max 255), notes (Optional[str]), activity_date (datetime)
    - ActivityUpdateSchema: same fields as create but all optional
    - ActivityResponseSchema: all fields including id, contact_id, created_at, updated_at with model_config from_attributes=True
    - ActivityListResponseSchema: list of activities with pagination metadata (activities, total, page, limit, has_more)
    - Follow pattern from: backend/app/schemas/contact.py
  - [x] 2.2 Create Attachment schemas (backend/app/schemas/attachment.py)
    - AttachmentResponseSchema: id, activity_id, original_filename, stored_filename, file_size, mime_type, uploaded_at with model_config from_attributes=True
    - Follow pattern from: backend/app/schemas/contact.py
  - [x] 2.3 Update schemas __init__.py
    - Export all new schemas in backend/app/schemas/__init__.py
    - Follow existing pattern for imports/exports

**Acceptance Criteria:**
- All schemas defined with proper Pydantic validation
- Activity type uses Literal enum for validation
- Subject field enforces 255 character max
- Schemas follow existing patterns from contact.py
- Schemas properly exported from __init__.py

---

#### Task Group 3: Service Layer
**Dependencies:** Task Groups 1-2

- [x] 3.0 Complete service layer business logic
  - [x] 3.1 Write 2-8 focused tests for ActivityService
    - Limit to 2-8 highly focused tests maximum
    - Test only critical service methods (e.g., create activity, get activities for contact, update activity, delete activity)
    - Skip exhaustive testing of all edge cases
  - [x] 3.2 Create ActivityService (backend/app/services/activity_service.py)
    - Method: create_activity(db, contact_id, user_id, activity_data) -> Activity
      - Verify contact ownership before creating activity
      - Return None if contact not found or not owned by user
    - Method: get_activities_for_contact(db, contact_id, user_id) -> list[Activity]
      - Verify contact ownership
      - Return activities sorted by activity_date desc
      - Include attachments relationship
    - Method: get_all_activities_for_user(db, user_id, activity_type=None, search=None) -> list[Activity]
      - Get all activities across all user's contacts
      - Filter by type if provided
      - Search in subject and notes if search term provided
      - Sort by activity_date desc
    - Method: get_activity_by_id(db, activity_id, user_id) -> Optional[Activity]
      - Verify activity belongs to user's contact
      - Return None if not found or not owned
    - Method: update_activity(db, activity_id, user_id, update_data) -> Optional[Activity]
      - Verify ownership through contact relationship
      - Update in place (no history)
      - Return None if not found or not owned
    - Method: delete_activity(db, activity_id, user_id) -> bool
      - Verify ownership through contact relationship
      - Hard delete (attachments cascade automatically)
      - Return True if deleted, False if not found/not owned
    - Follow pattern from: backend/app/services/contact_service.py
  - [x] 3.3 Write 2-8 focused tests for AttachmentService
    - Limit to 2-8 highly focused tests maximum
    - Test only critical service methods (e.g., save attachment metadata, get attachment, delete attachment)
    - Skip exhaustive testing of file operations edge cases
  - [x] 3.4 Create AttachmentService (backend/app/services/attachment_service.py)
    - Method: save_attachment_metadata(db, activity_id, original_filename, stored_filename, file_path, file_size, mime_type) -> Attachment
      - Create attachment record in database
    - Method: get_attachment_by_id(db, attachment_id, activity_id, user_id) -> Optional[Attachment]
      - Verify attachment belongs to activity that belongs to user's contact
      - Return None if not found or not owned
    - Method: delete_attachment(db, attachment_id, user_id) -> bool
      - Verify ownership through activity->contact chain
      - Delete database record and file from filesystem
      - Return True if deleted, False if not found/not owned
    - Method: sanitize_filename(filename) -> str (static method)
      - Replace unsafe characters (/, \, :, *, ?, ", <, >, |, null bytes, whitespace) with '-'
      - Preserve file extension
    - Method: get_upload_directory(activity_id) -> Path (static method)
      - Return Path object for /home/yaakov/git/SimpleCRM/backend/uploads/activities/{activity_id}/
      - Create directory if it doesn't exist
    - Follow static method pattern from ContactService
  - [x] 3.5 Ensure service layer tests pass
    - Run ONLY the 2-8 tests written in 3.1 and 3.3
    - Verify critical service methods work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass (ActivityService)
- The 2-8 tests written in 3.3 pass (AttachmentService)
- All service methods implement ownership verification
- ActivityService handles filtering and searching
- AttachmentService handles file path sanitization
- Services follow existing ContactService patterns

---

#### Task Group 4: API Endpoints
**Dependencies:** Task Groups 1-3

- [x] 4.0 Complete API endpoints
  - [x] 4.1 Write 2-8 focused tests for activity API endpoints
    - Limit to 2-8 highly focused tests maximum
    - Test only critical API operations (e.g., create activity for contact, get activities, update activity, delete activity)
    - Skip exhaustive testing of all HTTP status codes and scenarios
  - [x] 4.2 Create activities router (backend/app/routers/activities.py)
    - GET /api/contacts/{contact_id}/activities - List activities for a contact
      - Query params: None (returns all activities sorted by date desc)
      - Response: ActivityListResponseSchema (no pagination for simplicity)
      - Error: 404 if contact not found/not owned, 401 if not authenticated
    - POST /api/contacts/{contact_id}/activities - Create activity for a contact
      - Body: ActivityCreateSchema
      - Response: ActivityResponseSchema (201 Created)
      - Error: 400 if invalid data, 404 if contact not found, 401 if not authenticated
    - GET /api/activities - List all activities across all contacts for user
      - Query params: type (optional filter), search (optional search in subject/notes)
      - Response: list[ActivityResponseSchema]
      - Error: 401 if not authenticated
    - GET /api/activities/{activity_id} - Get single activity by ID
      - Response: ActivityResponseSchema
      - Error: 404 if not found/not owned, 401 if not authenticated
    - PUT /api/activities/{activity_id} - Update activity
      - Body: ActivityUpdateSchema
      - Response: ActivityResponseSchema
      - Error: 400 if invalid, 404 if not found/not owned, 401 if not authenticated
    - DELETE /api/activities/{activity_id} - Delete activity
      - Response: 204 No Content
      - Error: 404 if not found/not owned, 401 if not authenticated
    - Use APIRouter with prefix="/api" and tags=["activities"]
    - Use Depends(get_current_user) and Depends(get_db)
    - Follow pattern from: backend/app/routers/contacts.py
    - Include detailed docstrings with auth, parameters, responses, error examples
  - [x] 4.3 Write 2-8 focused tests for attachment API endpoints
    - Limit to 2-8 highly focused tests maximum
    - Test only critical operations (e.g., upload file, download file, delete attachment)
    - Skip exhaustive testing of all file types and edge cases
  - [x] 4.4 Create attachments router (backend/app/routers/attachments.py)
    - POST /api/activities/{activity_id}/attachments - Upload file attachment
      - Content-Type: multipart/form-data
      - Form field: file (UploadFile)
      - Save to: /home/yaakov/git/SimpleCRM/backend/uploads/activities/{activity_id}/
      - Generate unique stored_filename (e.g., uuid + extension)
      - Store metadata in database via AttachmentService
      - Response: AttachmentResponseSchema (201 Created)
      - Error: 400 if no file, 404 if activity not found/not owned, 500 for file system errors
    - GET /api/activities/{activity_id}/attachments/{attachment_id} - Download file
      - Serve file with FileResponse
      - Content-Disposition header with sanitized original_filename
      - Error: 404 if not found/not owned or file doesn't exist
    - DELETE /api/activities/{activity_id}/attachments/{attachment_id} - Delete attachment
      - Delete file from filesystem and database record
      - Response: 204 No Content
      - Error: 404 if not found/not owned
    - Use APIRouter with prefix="/api" and tags=["attachments"]
    - Use Depends(get_current_user) and Depends(get_db)
    - Follow pattern from: backend/app/routers/contacts.py
    - Include detailed docstrings
  - [x] 4.5 Register routers in main application
    - Import routers in backend/app/main.py
    - Register with app.include_router(activities.router)
    - Register with app.include_router(attachments.router)
    - Follow existing router registration pattern
  - [x] 4.6 Ensure API layer tests pass
    - Run ONLY the 2-8 tests written in 4.1 and 4.3
    - Verify critical API endpoints work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass (activities endpoints)
- The 2-8 tests written in 4.3 pass (attachments endpoints)
- All endpoints implement proper authentication checks
- All endpoints return appropriate HTTP status codes
- File upload/download works correctly
- Attachment filenames are sanitized for security
- Routers registered in main.py

---

### Frontend Components

#### Task Group 5: Reusable Markdown Editor Component
**Dependencies:** Task Groups 1-4 (API must be available)

- [x] 5.0 Create reusable markdown editor component
  - [x] 5.1 Install required frontend dependencies
    - npm install marked dompurify
    - npm install --save-dev @types/dompurify (if using TypeScript)
  - [x] 5.2 Write 2-8 focused tests for MarkdownEditor component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical component behaviors (e.g., text input updates model, preview renders markdown, toggle works on mobile)
    - Skip exhaustive testing of all markdown features
  - [x] 5.3 Create MarkdownEditor.vue (frontend/src/components/MarkdownEditor.vue)
    - Props: modelValue (string), placeholder (string, default "Write markdown...")
    - Emits: update:modelValue
    - Features:
      - Split-pane layout: left textarea for input, right div for preview
      - Live preview with 300ms debounce
      - Mobile toggle button to switch between "Write" and "Preview" modes
      - Use marked library with gfm: true option
      - Sanitize HTML output with DOMPurify
      - Render preview with v-html
    - Styling: Tailwind CSS, follow existing component patterns
    - Use Vue 3 Composition API (ref, computed, watch)
    - Follow pattern from: frontend/src/components/ContactForm.vue
  - [x] 5.4 Ensure MarkdownEditor tests pass
    - Run ONLY the 2-8 tests written in 5.2
    - Verify critical component behaviors work
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 5.2 pass
- MarkdownEditor is a reusable component with v-model support
- Live preview updates as user types (debounced)
- Markdown renders correctly with GFM support
- HTML output is sanitized with DOMPurify
- Mobile toggle between Write/Preview modes works
- Component follows existing Vue patterns

---

#### Task Group 6: Activity Timeline Components
**Dependencies:** Task Groups 1-5

- [x] 6.0 Create activity timeline UI components
  - [x] 6.1 Write 2-8 focused tests for ActivityTimeline component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors (e.g., fetches activities on mount, filters by type, searches content)
    - Skip exhaustive testing of all UI states
  - [x] 6.2 Create ActivityTimeline.vue (frontend/src/components/ActivityTimeline.vue)
    - Props: contactId (number, required)
    - State: activities (ref), loading (ref), filterType (ref, default "All"), searchTerm (ref)
    - Methods:
      - fetchActivities() - GET /api/contacts/{contactId}/activities
      - filterByType(type) - Update filterType and filter local activities array
      - searchActivities(term) - Filter activities by searching subject and notes
      - handleActivityCreated(activity) - Add new activity to list and re-sort
      - handleActivityUpdated(activity) - Update activity in list
      - handleActivityDeleted(activityId) - Remove activity from list
    - Layout:
      - Header with "Add Activity" button (opens ActivityForm modal)
      - Filter controls: dropdown for type (All, Call, Meeting, Email, Note)
      - Search input for content search
      - Activity list (iterate with ActivityItem component)
      - Empty state when no activities: "No activities yet. Start tracking interactions with this contact."
    - Styling: Tailwind CSS, follow existing component patterns
    - Use Composition API
    - Follow pattern from: frontend/src/views/ContactsView.vue for list management
  - [x] 6.3 Write 2-8 focused tests for ActivityItem component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors (e.g., displays activity data, edit button opens form, delete button removes activity)
    - Skip exhaustive testing of all display states
  - [x] 6.4 Create ActivityItem.vue (frontend/src/components/ActivityItem.vue)
    - Props: activity (object, required)
    - Emits: edit(activity), delete(activityId)
    - Layout:
      - Type badge with color coding (Call=blue, Meeting=green, Email=purple, Note=gray)
      - Subject as heading (font-bold, text-lg)
      - Activity date as subheading (text-sm, text-gray-600)
      - Rendered markdown content (use v-html with DOMPurify)
      - Attachment list with download links (if attachments exist)
      - Edit and Delete icon buttons (visible on hover)
    - Features:
      - Expandable/collapsible content section (optional, for long notes)
      - Markdown HTML sanitized with DOMPurify before rendering
    - Styling: Tailwind CSS, card layout with shadow and rounded corners
    - Follow pattern from existing components
  - [x] 6.5 Write 2-8 focused tests for ActivityForm component
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors (e.g., creates new activity, updates existing activity, validates required fields)
    - Skip exhaustive testing of all form validation scenarios
  - [x] 6.6 Create ActivityForm.vue (frontend/src/components/ActivityForm.vue)
    - Props: contactId (number), activity (object, optional - for edit mode)
    - Emits: saved(activity), cancelled
    - State: formData (reactive), errors (ref), loading (ref), uploadedFiles (ref)
    - Fields:
      - Activity Type (dropdown: Call, Meeting, Email, Note)
      - Subject (text input, required, max 255)
      - Activity Date (datetime-local input, required)
      - Notes (MarkdownEditor component)
      - File attachments (file input + list of uploaded files with delete)
    - Validation:
      - Subject required and max 255 chars
      - Activity type required
      - Activity date required
    - Methods:
      - validateForm() - Check all required fields
      - handleSubmit() - POST or PUT to API
      - handleFileUpload(file) - POST /api/activities/{activityId}/attachments
      - handleFileDelete(attachmentId) - DELETE /api/activities/{activityId}/attachments/{attachmentId}
    - Layout: Modal or slide-over panel
    - Action buttons: Save, Cancel, Delete (if editing)
    - Styling: Tailwind CSS
    - Follow pattern from: frontend/src/components/ContactForm.vue
  - [x] 6.7 Ensure activity components tests pass
    - Run ONLY the 2-8 tests written in 6.1, 6.3, and 6.5
    - Verify critical component behaviors work
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 6.1 pass (ActivityTimeline)
- The 2-8 tests written in 6.3 pass (ActivityItem)
- The 2-8 tests written in 6.5 pass (ActivityForm)
- ActivityTimeline fetches and displays activities for a contact
- Filter and search functionality works
- ActivityItem displays activity with rendered markdown
- Attachments display with download links
- ActivityForm creates and updates activities
- File upload/delete functionality works
- Form validation prevents invalid submissions

---

#### Task Group 7: Contact Preview Integration
**Dependencies:** Task Groups 1-6

- [x] 7.0 Integrate timeline into ContactPreview component
  - [x] 7.1 Write 2-8 focused tests for ContactPreview tab integration
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors (e.g., Timeline tab is default, tab switching works, components render)
    - Skip exhaustive testing of all tab interactions
  - [x] 7.2 Modify ContactPreview.vue (frontend/src/components/ContactPreview.vue)
    - Add state: activeTab (ref, default "timeline")
    - Add tabbed interface:
      - Tab headers: "Timeline" and "Contact Info"
      - Tab content areas
      - Timeline tab renders ActivityTimeline component with :contactId
      - Contact Info tab renders existing contact details view
    - Tab switching:
      - Click handlers to update activeTab
      - Active tab styling (border-bottom or background highlight)
      - Conditional rendering based on activeTab
    - Preserve existing contact data and emit patterns
    - Styling: Tailwind CSS tabs pattern
    - Reference existing ContactPreview structure
  - [x] 7.3 Ensure ContactPreview integration tests pass
    - Run ONLY the 2-8 tests written in 7.1
    - Verify tab switching works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 7.1 pass
- ContactPreview shows tabbed interface
- Timeline tab is the default active tab
- Tab switching preserves contact selection
- ActivityTimeline component renders in Timeline tab
- Existing Contact Info view preserved in second tab
- No data reloaded unnecessarily on tab switch

---

### Testing & Integration

#### Task Group 8: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-7

- [x] 8.0 Review existing tests and fill critical gaps only
  - [x] 8.1 Review tests from Task Groups 1-7
    - Review the 2-8 tests written for database models (Task 1.1)
    - Review the 2-8 tests written for ActivityService (Task 3.1)
    - Review the 2-8 tests written for AttachmentService (Task 3.3)
    - Review the 2-8 tests written for activities API endpoints (Task 4.1)
    - Review the 2-8 tests written for attachments API endpoints (Task 4.3)
    - Review the 2-8 tests written for MarkdownEditor component (Task 5.2)
    - Review the 2-8 tests written for ActivityTimeline component (Task 6.1)
    - Review the 2-8 tests written for ActivityItem component (Task 6.3)
    - Review the 2-8 tests written for ActivityForm component (Task 6.5)
    - Review the 2-8 tests written for ContactPreview integration (Task 7.1)
    - Total existing tests: approximately 20-80 tests
  - [x] 8.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows that lack test coverage
    - Focus ONLY on gaps related to Activity Timeline & Notes feature
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows over unit test gaps
    - Key workflows to verify:
      - Complete activity lifecycle (create -> view -> edit -> delete)
      - File attachment lifecycle (upload -> download -> delete)
      - Markdown rendering with XSS prevention
      - Cross-contact activity queries
      - Filter and search functionality
      - Ownership verification across activity->contact chain
      - CASCADE delete behavior (contact deletion removes activities and attachments)
  - [x] 8.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration points and end-to-end workflows
    - Do NOT write comprehensive coverage for all scenarios
    - Skip edge cases unless business-critical
    - Suggested priority tests:
      - E2E: Create contact -> Add activity with attachment -> View timeline -> Download file
      - E2E: Edit activity markdown notes -> Verify XSS prevention in rendered output
      - Integration: Delete contact -> Verify activities and attachments cascade deleted
      - Integration: Search activities across multiple contacts
      - Integration: Filter activities by type across timeline
      - Security: Verify user cannot access other user's activities
      - Security: Verify filename sanitization prevents directory traversal
  - [x] 8.4 Run feature-specific tests only
    - Run ONLY tests related to Activity Timeline & Notes feature
    - Backend tests: pytest -k "activity or attachment" (approximate filter)
    - Frontend tests: npm run test -- ActivityTimeline ActivityItem ActivityForm MarkdownEditor ContactPreview
    - Expected total: approximately 30-90 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical workflows pass
    - Fix any failing tests

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 30-90 tests total)
- Critical user workflows for Activity Timeline & Notes are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this feature's requirements
- End-to-end workflows verified (create -> read -> update -> delete)
- Security tests verify ownership and XSS prevention
- CASCADE delete behavior verified

---

### Documentation & Cleanup

#### Task Group 9: Documentation and Final Verification
**Dependencies:** All previous task groups

- [x] 9.0 Complete documentation and final verification
  - [x] 9.1 Create/update API documentation
    - Document all new endpoints in API docs (if separate docs exist)
    - Verify all endpoint docstrings are complete and accurate
    - Document request/response schemas
    - Document error codes and messages
  - [x] 9.2 Update README or developer documentation
    - Document new feature: Activity Timeline & Notes
    - Document markdown library choice (marked + DOMPurify)
    - Document file storage location and structure
    - Document any new environment variables or configuration
  - [x] 9.3 Verify file upload directory exists and permissions
    - Ensure /home/yaakov/git/SimpleCRM/backend/uploads/ directory exists
    - Verify write permissions for web server user
    - Add .gitignore entry for uploads directory (keep directory, ignore files)
  - [x] 9.4 Manual end-to-end testing
    - Test complete activity lifecycle in browser
    - Test file upload/download/delete in browser
    - Test markdown rendering with various GFM features
    - Test filter and search functionality
    - Test mobile responsive layout
    - Test tab switching in ContactPreview
    - Verify XSS prevention (try injecting script tags in markdown)
    - Verify ownership restrictions (cannot access other user's activities)
  - [x] 9.5 Code cleanup and formatting
    - Run Python formatter (Black) on all new backend files
    - Run Python linter (Ruff) and fix any issues
    - Run ESLint on all new frontend files
    - Run Prettier on all new frontend files
    - Remove any console.log statements or debug code
    - Remove any unused imports
  - [x] 9.6 Final feature verification checklist
    - [ ] All API endpoints working and returning correct status codes
    - [ ] All database migrations applied successfully
    - [ ] All CASCADE delete behaviors working
    - [ ] Markdown rendering with GFM support working
    - [ ] XSS prevention with DOMPurify working
    - [ ] File upload/download/delete working
    - [ ] Filename sanitization preventing directory traversal
    - [ ] Filter by activity type working
    - [ ] Search by content working
    - [ ] Timeline as default tab in ContactPreview
    - [ ] Mobile responsive layout working
    - [ ] All tests passing
    - [ ] No console errors or warnings

**Acceptance Criteria:**
- API documentation complete and accurate
- Developer documentation updated with new feature
- File upload directory configured with correct permissions
- Manual testing completed successfully for all key workflows
- Code formatted and linted with no errors
- All items in final verification checklist completed
- Feature ready for user acceptance testing

---

## Execution Order

Recommended implementation sequence:

1. **Database Layer** (Task Group 1)
   - Foundation for all other components
   - Models and migrations must be in place first
   - Estimated time: 3-4 hours

2. **API Layer - Schemas** (Task Group 2)
   - Defines data contracts for API
   - Required before service and router implementation
   - Estimated time: 1-2 hours

3. **API Layer - Services** (Task Group 3)
   - Business logic layer
   - Required before routers can function
   - Estimated time: 4-5 hours

4. **API Layer - Routers** (Task Group 4)
   - HTTP endpoints
   - Completes backend implementation
   - Estimated time: 4-5 hours

5. **Frontend - Markdown Editor** (Task Group 5)
   - Reusable component needed by ActivityForm
   - Can be developed independently
   - Estimated time: 2-3 hours

6. **Frontend - Activity Components** (Task Group 6)
   - Main feature UI components
   - Depends on API being available
   - Estimated time: 6-8 hours

7. **Frontend - Integration** (Task Group 7)
   - Integrate timeline into ContactPreview
   - Final UI integration step
   - Estimated time: 1-2 hours

8. **Testing & Gap Analysis** (Task Group 8)
   - Review all tests and fill critical gaps
   - Run feature-specific test suite
   - Estimated time: 3-4 hours

9. **Documentation & Final Verification** (Task Group 9)
   - Documentation, cleanup, and manual testing
   - Ensures feature is production-ready
   - Estimated time: 2-3 hours

**Total Estimated Time: 26-36 hours**

---

## Important Notes

### Testing Strategy
- Each task group writes 2-8 focused tests maximum during development
- Tests should cover only critical behaviors, not exhaustive coverage
- Final test review (Task Group 8) adds maximum 10 additional tests if needed
- Total expected tests: 30-90 tests for this entire feature
- Do NOT aim for 100% code coverage - focus on critical user workflows

### Security Considerations
- **XSS Prevention**: Always sanitize markdown HTML output with DOMPurify before rendering
- **Directory Traversal**: Validate all file paths stay within uploads directory
- **Filename Sanitization**: Replace unsafe characters in filenames for downloads
- **Ownership Verification**: All API endpoints verify user owns the contact associated with activity
- **No File Type Restrictions**: Accept all file types as per user requirement (security trade-off accepted)

### File Storage Management
- Files stored at: /home/yaakov/git/SimpleCRM/backend/uploads/activities/{activity_id}/
- Create activity-specific subdirectories dynamically on first upload
- Generate unique stored_filename (e.g., UUID + extension) to prevent collisions
- Store original_filename in database for user-friendly downloads
- CASCADE delete: Deleting activity should also delete all files from filesystem

### Markdown Implementation
- Library: marked (with gfm: true option for GitHub-Flavored Markdown)
- Sanitization: DOMPurify for XSS prevention
- Preview: Live preview with 300ms debounce for performance
- Mobile: Toggle between Write/Preview modes on smaller screens
- Features: Headers, emphasis, lists, links, code blocks, blockquotes, tables, strikethrough, task lists

### Pattern Adherence
- Backend follows: Contact model/service/router patterns
- Frontend follows: Vue 3 Composition API with Tailwind CSS
- Database follows: SQLAlchemy with timestamps and CASCADE deletes
- API follows: RESTful design with proper HTTP status codes
- All code follows existing SimpleCRM conventions and standards

### Dependencies Between Task Groups
- Task Group 2 depends on Task Group 1 (schemas need models)
- Task Group 3 depends on Task Groups 1-2 (services need models and schemas)
- Task Group 4 depends on Task Groups 1-3 (routers need services)
- Task Group 5 can start after Task Group 4 (frontend needs API)
- Task Group 6 depends on Task Groups 4-5 (components need API and MarkdownEditor)
- Task Group 7 depends on Task Group 6 (integration needs components)
- Task Group 8 depends on Task Groups 1-7 (test review needs all implementation complete)
- Task Group 9 depends on all previous groups (documentation and verification is final step)
