# Specification: Activity Timeline & Notes

## Goal
Enable users to track all interactions and notes for each contact through a timeline-based activity management system with markdown-formatted notes and file attachments.

## User Stories
- As a CRM user, I want to log calls, meetings, emails, and general notes for my contacts so that I can track all interactions in one place
- As a CRM user, I want to view a chronological timeline of activities when I open a contact so that I can quickly see the history of interactions
- As a CRM user, I want to attach files to activities and use markdown formatting in my notes so that I can keep rich documentation

## Specific Requirements

**Activity Timeline as Default View**
- Modify ContactPreview.vue to implement a tabbed interface with "Timeline" and "Contact Info" tabs
- Timeline tab displays the activity list and is the default active tab when opening a contact
- Contact Info tab shows the existing contact details view (current ContactPreview implementation)
- Tab switching preserves contact selection and does not reload data unnecessarily

**Activity CRUD Operations**
- Create activities with four types: Call, Meeting, Email, General Note
- Each activity has: type (enum), subject (string), notes (markdown text), activity_date (datetime)
- Update activities in-place without tracking edit history
- Delete activities using hard delete (no soft delete or trash functionality)
- All operations scoped to contact-specific activities (GET, POST) and global activity endpoints (PUT, DELETE)

**Markdown Notes with Live Preview**
- Use 'marked' library for markdown parsing with GitHub-Flavored Markdown (GFM) support
- Activity creation/edit form displays split-pane editor: left pane for markdown input textarea, right pane for live preview
- Preview updates as user types with debouncing (300ms) for performance
- On mobile/smaller screens, provide toggle button to switch between "Write" and "Preview" modes
- Display rendered markdown HTML in activity timeline items using DOMPurify for XSS prevention
- Support GFM features: headers, emphasis, lists, links, code blocks, blockquotes, tables, strikethrough, task lists

**File Attachment Management**
- Support multiple file attachments per activity with no restrictions on file types, sizes, or attachment counts
- Store files in local filesystem at /home/yaakov/git/SimpleCRM/backend/uploads/activities/{activity_id}/
- Create activity-specific subdirectories dynamically when first file is uploaded
- Store file metadata in database: original_filename, stored_filename, file_path, file_size, mime_type, uploaded_at
- Sanitize original filenames for download by replacing unsafe characters (/, \, :, *, ?, ", <, >, |, null bytes and white space) with '-'
- Serve files with Content-Disposition header using sanitized original filename
- Upload and download functionality only (no preview or inline display)

**Search and Filtering**
- Filter activities by type (Call, Meeting, Email, General Note) using dropdown or button group
- Search activities by content in subject and notes fields (case-insensitive)
- Display activities sorted by activity_date descending (most recent first)
- No date range filtering required as full list is sorted and visible

**API Endpoints**
- GET /api/contacts/{contact_id}/activities - List all activities for a specific contact
- GET /api/activities - List all activities across all contacts (for reporting or global search)
- POST /api/contacts/{contact_id}/activities - Create new activity for a contact
- PUT /api/activities/{activity_id} - Update an existing activity
- DELETE /api/activities/{activity_id} - Delete an activity (hard delete)
- POST /api/activities/{activity_id}/attachments - Upload file attachment (multipart/form-data)
- GET /api/activities/{activity_id}/attachments/{attachment_id} - Download file attachment
- DELETE /api/activities/{activity_id}/attachments/{attachment_id} - Delete file attachment

**Data Models**
- Activity model: id (int), contact_id (FK to contacts), type (enum: Call|Meeting|Email|Note), subject (varchar 255), notes (text), activity_date (datetime), created_at (datetime), updated_at (datetime)
- Attachment model: id (int), activity_id (FK to activities), original_filename (varchar 255), stored_filename (varchar 255), file_path (varchar 500), file_size (bigint), mime_type (varchar 100), uploaded_at (datetime)
- Foreign key relationships: Contact -> Activities (one-to-many), Activity -> Attachments (one-to-many)
- CASCADE delete behavior: deleting contact deletes all activities, deleting activity deletes all attachments and files

**Frontend Components**
- Create ActivityTimeline.vue component for displaying activity list with filter/search controls
- Create ActivityForm.vue component for creating/editing activities with markdown editor and file upload
- Create ActivityItem.vue component for displaying individual activity with rendered markdown
- Create MarkdownEditor.vue reusable component for markdown input with live preview
- Modify ContactPreview.vue to add tabbed interface (tabs managed with local state)

**Security and Validation**
- Validate activity type against allowed enum values (Call, Meeting, Email, Note)
- Validate subject field max length (255 characters)
- Validate file paths stay within uploads directory to prevent directory traversal
- Sanitize markdown HTML output with DOMPurify to prevent XSS attacks
- Verify activity ownership through contact ownership (user_id check on contact)
- No authentication changes needed (leverage existing session-based auth)

**Error Handling**
- Return 404 when activity or attachment not found
- Return 403 when user attempts to access activity for contact they don't own
- Return 400 for invalid activity type or validation failures
- Return 500 for file system errors during upload/download with appropriate error messages
- Display user-friendly error messages in UI for all failure scenarios

## Visual Design

No visual assets provided. Implementation follows existing SimpleCRM UI patterns.

**Timeline Tab Layout**
- Header with "Add Activity" button aligned right
- Filter controls: activity type dropdown (All, Call, Meeting, Email, Note) and search input
- Activity list with most recent first, each item showing: type icon, subject, date, notes preview
- Empty state when no activities: icon + "No activities yet. Start tracking interactions with this contact."

**Activity Form Layout**
- Modal or slide-over panel for create/edit
- Fields: Activity Type (dropdown), Subject (text input), Activity Date (datetime picker), Notes (markdown editor with split pane)
- File attachments section below notes with upload button and list of attached files
- Action buttons: Save, Cancel (and Delete if editing)

**Activity Item Display**
- Type badge (colored by type: blue=Call, green=Meeting, purple=Email, gray=Note)
- Subject as heading, activity date as subheading
- Rendered markdown content in expandable/collapsible section
- Attachment list with download icons
- Edit and Delete icon buttons on hover

## Existing Code to Leverage

**Contact Model and Service Pattern (backend/app/models/contact.py, backend/app/services/contact_service.py)**
- Use same SQLAlchemy Base class and column patterns (id, created_at, updated_at with datetime.utcnow)
- Follow foreign key pattern with CASCADE deletes (ondelete="CASCADE")
- Use index=True for foreign keys and frequently queried fields
- Implement service layer with static methods for business logic
- Use Pydantic schema validation for request/response

**Contact Router Pattern (backend/app/routers/contacts.py)**
- Follow RESTful endpoint structure with APIRouter, prefix, and tags
- Use FastAPI dependency injection for get_db and get_current_user
- Return appropriate HTTP status codes (200, 201, 204, 400, 404)
- Include detailed docstrings with authentication, parameters, responses, and error examples
- Verify ownership through user_id checks in service layer

**ContactPreview Component (frontend/src/components/ContactPreview.vue)**
- Extend with tabs using local ref state for activeTab
- Preserve existing structure for "Contact Info" tab
- Add "Timeline" tab that renders ActivityTimeline component
- Keep same styling patterns with Tailwind CSS (bg-white, shadow, rounded-lg, p-6)
- Maintain emit patterns for edit, delete, and other actions

**ContactForm Validation Pattern (frontend/src/components/ContactForm.vue)**
- Use Vue 3 Composition API with ref, reactive, computed
- Implement field-level validation functions (validateSubject, etc.)
- Use errors ref object to store field-specific error messages
- Show validation errors on blur and submit
- Display loading/submitting states with disabled buttons

**Database Session Management (backend/app/database.py)**
- Use get_db() dependency function for session lifecycle
- SessionLocal factory pattern with autocommit=False, autoflush=False
- Ensure db.commit() after writes and db.refresh() to get updated data
- Handle exceptions and ensure db.close() in finally block

## Out of Scope
- Soft deletes or trash functionality for activities
- Edit history or version tracking for activity modifications
- Automated activity creation from external sources (email sync, calendar integration)
- Reminders, notifications, or due dates for activities
- Activity templates or predefined note structures
- Bulk operations (bulk delete, bulk edit, bulk export)
- Activity sharing or collaboration between multiple users
- Rich text WYSIWYG editor (markdown only)
- File preview or inline display of attachments (images, PDFs)
- Date range filtering for activities
- Activity categories or custom types beyond the four specified
- User/owner tracking for activity creation (single-user system assumes all activities created by the logged-in user)
