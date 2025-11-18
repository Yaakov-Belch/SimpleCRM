# Spec Requirements: Activity Timeline & Notes

## Initial Description
Activity Timeline & Notes

## Requirements Discussion

### First Round Questions

**Q1: Data Model Design - Is this the structure you have in mind?**
**Answer:** Single-user only (no need to capture user who created activity)

**Q2: Activity Types - Should we start with these core types?**
**Answer:** Four core activity types only: Call, Meeting, Email, and General Note

**Q3: Notes Field - Basic formatting support?**
**Answer:** Notes field should support basic markdown formatting

**Q4: User Interface - Default view for contacts?**
**Answer:** Timeline should be the default view when opening a contact

**Q5: Edit/Delete Behavior - How should we handle activity modifications?**
**Answer:** Hard deletes (not soft deletes), update in place (no edit history tracking)

**Q6: Filtering and Search - What controls do you need?**
**Answer:** Filterable by type and searchable by content. Date range filtering is NOT necessary because the full list is sorted by date.

**Q7: Cross-Contact API - Do you need to query activities across multiple contacts?**
**Answer:** Yes, support GET /api/activities endpoint for all activities across all contacts

**Q8: Future Features - Which of these should we exclude from this spec?**
**Answer:** Exclude all mentioned features EXCEPT: Include file attachments to activities (upload and download, no display/preview)

**Q9: Existing Code to Reference**
**Answer:** Look at existing pages implementation and existing data schemas for patterns

**Q10: Visual Assets**
**Answer:** No visual assets provided

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Contact Management - Path: `/home/yaakov/git/SimpleCRM/backend/app/models/contact.py`
- Feature: Contact Forms - Path: `/home/yaakov/git/SimpleCRM/frontend/src/components/ContactForm.vue`
- Feature: Contact Preview/Detail View - Path: `/home/yaakov/git/SimpleCRM/frontend/src/components/ContactPreview.vue`
- Feature: Contact List View - Path: `/home/yaakov/git/SimpleCRM/frontend/src/views/ContactsView.vue`
- Feature: Contact API Router - Path: `/home/yaakov/git/SimpleCRM/backend/app/routers/contacts.py`
- Feature: Contact Schemas - Path: `/home/yaakov/git/SimpleCRM/backend/app/schemas/contact.py`

**Patterns to follow:**
- Database models use SQLAlchemy with Base class
- Timestamp pattern: `created_at` and `updated_at` with `datetime.utcnow`
- Foreign key pattern: ForeignKey with CASCADE delete
- API routers use FastAPI with Pydantic schemas for validation
- Service layer pattern for business logic
- Vue components use Composition API
- Form validation pattern established in ContactForm.vue
- List/detail split view pattern established in ContactsView.vue

### Follow-up Questions - Round 1

**Follow-up 1: File Attachments - Storage and Access Details**
Since file attachments are included, I need clarification on:
- Where should uploaded files be stored? (filesystem path or preference)
- What file types should be allowed? (any restrictions on file extensions or MIME types?)
- What should be the maximum file size limit?
- Should there be a limit on the number of attachments per activity?
- For download, should the file be served with original filename or should we generate safe filenames?

**Answer:**
- Storage path: Choose and document a path that fits with common best practices
- File types: All file types allowed, no restrictions
- File size limit: No limits
- Number of attachments per activity: No limits
- Download: Serve with original filename but replace unsafe characters with '-'

**Follow-up 2: Contact Detail View - Timeline Integration**
You mentioned the timeline should be the default view when opening a contact. Currently, ContactPreview.vue shows contact details in a right sidebar. Should we:
- Replace the current ContactPreview component entirely with the activity timeline view?
- OR create a new dedicated contact detail page (e.g., /contacts/:id) that shows timeline as the primary content with contact info as a header/sidebar?
- OR add a tabbed interface to ContactPreview where "Timeline" is the default tab and "Contact Info" is another tab?

**Answer:** Add a tabbed interface to ContactPreview where "Timeline" is the default tab and "Contact Info" is another tab

**Follow-up 3: Markdown Rendering**
For markdown support in the notes field:
- Should markdown be rendered as formatted HTML when viewing activities, or just stored as plain text with markdown syntax visible?
- If rendered, which markdown library should we use? (e.g., marked.js, markdown-it, etc.)
- Should the activity creation form have a markdown preview feature, or just a plain textarea?

**Answer:**
- Library: Choose a simple, popular library that supports GitHub-Flavored Markdown (GFM). Document the choice clearly.
- Input: Text input with markdown preview pane
- Display: Markdown formatted to HTML

## Technical Decisions

Based on user requirements and best practices for the SimpleCRM project, the following technical decisions have been made:

### File Storage Architecture

**Decision: Local filesystem storage at `/home/yaakov/git/SimpleCRM/backend/uploads/activities/{activity_id}/`**

**Rationale:**
- Follows standard web application practices for file uploads
- Organizes files by activity ID for easy management and cleanup
- Aligns with project's simplicity-first philosophy (no cloud storage services)
- SQLite can store file metadata (filename, path, size, MIME type)
- Easy to implement cleanup when activities are deleted (CASCADE relationship)

**Implementation Details:**
- Base upload directory: `/home/yaakov/git/SimpleCRM/backend/uploads/`
- Activity-specific subdirectories: `activities/{activity_id}/`
- Create directories dynamically when first file is uploaded
- Store original filename with unsafe characters replaced by '-'
- File metadata stored in database: original_filename, stored_filename, file_path, file_size, mime_type, uploaded_at
- No file type restrictions (user requirement)
- No file size limits (user requirement)
- No attachment count limits per activity (user requirement)

**File Download Behavior:**
- Serve file with Content-Disposition header using sanitized original filename
- Replace unsafe characters (/, \, :, *, ?, ", <, >, |, null bytes) with '-'
- Preserve file extension
- Example: "My Document (2024).pdf" becomes "My-Document--2024-.pdf"

### Markdown Library Selection

**Decision: Use `marked` library with GitHub-Flavored Markdown (GFM) support**

**Rationale:**
- Lightweight and fast (~25KB minified)
- Most popular markdown parser in JavaScript ecosystem (100k+ stars on GitHub)
- Built-in GFM support via `marked-gfm-heading-id` or `gfm: true` option
- Well-maintained with regular security updates
- Simple API that fits Vue.js patterns
- No complex dependencies
- Excellent documentation

**Implementation Details:**
- Install: `npm install marked`
- Configure with GFM support: `marked.setOptions({ gfm: true, breaks: true })`
- Sanitize output with DOMPurify to prevent XSS attacks
- Install DOMPurify: `npm install dompurify`

**Markdown Input/Preview Pattern:**
- Split-pane editor in activity form:
  - Left pane: Textarea for markdown input
  - Right pane: Live preview of rendered markdown
- Preview updates as user types (with debouncing for performance)
- Toggle button to switch between "Write" and "Preview" modes on mobile/smaller screens
- Display rendered markdown HTML in activity timeline view

**Supported Markdown Features (GFM):**
- Headers (# H1, ## H2, etc.)
- Emphasis (*italic*, **bold**)
- Lists (ordered and unordered)
- Links and inline code
- Code blocks with syntax
- Blockquotes
- Tables
- Strikethrough (~~text~~)
- Task lists (- [ ] Todo item)

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets were provided. Implementation will follow established SimpleCRM UI patterns from ContactPreview.vue and ContactForm.vue.

## Requirements Summary

### Functional Requirements

**Core Activity Management:**
- Create, read, update, delete activities for contacts
- Four activity types: Call, Meeting, Email, General Note
- Markdown-formatted notes field with live preview
- Activity list sorted by date (most recent first)
- Hard deletes (no soft delete or trash)
- Update in place (no edit history)

**File Attachment Support:**
- Upload multiple files per activity
- No file type restrictions
- No file size limits
- No limit on attachment count per activity
- Download files with sanitized original filenames
- Store file metadata in database
- No preview/display functionality (upload and download only)

**Search and Filtering:**
- Filter activities by type (Call, Meeting, Email, General Note)
- Search activities by content/notes
- Date-sorted view (no date range filter needed)

**API Endpoints:**
- Contact-specific activities: GET /api/contacts/{contact_id}/activities
- All activities across contacts: GET /api/activities
- Create activity: POST /api/contacts/{contact_id}/activities
- Update activity: PUT/PATCH /api/activities/{activity_id}
- Delete activity: DELETE /api/activities/{activity_id}
- Upload attachment: POST /api/activities/{activity_id}/attachments
- Download attachment: GET /api/activities/{activity_id}/attachments/{attachment_id}

**User Interface Integration:**
- Add tabbed interface to ContactPreview component
- Two tabs: "Timeline" (default) and "Contact Info"
- Timeline tab displays activity list for the contact
- Activity creation form with markdown editor (split-pane or toggle)
- Activity items display rendered markdown
- Filter controls for activity type
- Search input for content search
- Edit/delete buttons on each activity item

### Reusability Opportunities

**Existing Components to Reference:**
- ContactPreview.vue - Pattern for implementing tabbed interface
- ContactForm.vue - Pattern for form validation and submission
- ContactsView.vue - Pattern for list/detail split view

**Backend Patterns to Follow:**
- Contact model structure - Use similar SQLAlchemy patterns
- Contact router - Use similar FastAPI endpoint structure
- Contact schemas - Use similar Pydantic validation patterns
- Database session management from existing routers
- Error handling patterns from existing endpoints

**Technical Patterns:**
- Vue Composition API for state management
- Tailwind CSS utility classes for styling
- FastAPI dependency injection for database sessions
- Pydantic schemas for request/response validation
- SQLAlchemy relationships with CASCADE deletes

### Scope Boundaries

**In Scope:**
- Full CRUD operations for activities
- Four specific activity types (Call, Meeting, Email, General Note)
- Markdown notes with live preview
- File upload and download (multiple files per activity)
- Type filtering and content search
- Contact-specific and cross-contact activity queries
- Timeline as default tab in contact detail view
- Hard deletes and in-place updates

**Out of Scope (Explicitly Excluded):**
- Soft deletes or trash functionality
- Edit history or version tracking
- Automated activity creation from emails/calendar
- Reminders or notifications for activities
- Activity templates
- Bulk operations (bulk delete, bulk update)
- Activity sharing between contacts
- Rich text editor (using markdown instead)
- File preview or inline display
- Date range filtering
- Activity categories beyond the four specified types
- User/owner tracking (single-user system)

### Technical Considerations

**Data Model:**
- Activity model with fields: id, contact_id (FK), type (enum), subject, notes (text), activity_date, created_at, updated_at
- Attachment model with fields: id, activity_id (FK), original_filename, stored_filename, file_path, file_size, mime_type, uploaded_at
- Foreign key CASCADE deletes: Delete activity deletes attachments, delete contact deletes activities
- SQLAlchemy relationships: contact.activities (one-to-many), activity.attachments (one-to-many)

**File Storage:**
- Base directory: `/home/yaakov/git/SimpleCRM/backend/uploads/`
- Activity subdirectories: `activities/{activity_id}/`
- Filename sanitization for downloads
- File metadata in SQLite database
- Create upload directories on-demand

**Frontend Dependencies:**
- Add `marked` package for markdown parsing
- Add `dompurify` package for XSS prevention
- Use existing Vue Router for navigation
- Use existing Tailwind CSS for styling

**Backend Dependencies:**
- Use existing FastAPI for API endpoints
- Use existing SQLAlchemy for database models
- Python `pathlib` for file path handling
- Python `uuid` for unique filenames if needed

**Integration Points:**
- ContactPreview.vue requires modification to add tabs
- Main router needs activity-related API endpoints
- Database migration to create activity and attachment tables
- File upload middleware for handling multipart/form-data

**Architecture Approach:**
- Follow existing three-layer architecture: Router -> Service -> Model
- Activity service handles business logic (CRUD, file management)
- Activity router handles HTTP requests/responses
- Activity model defines database schema
- Activity schemas define Pydantic validation models
- Separate AttachmentService for file operations
- Reuse database session dependency from existing routers

**Performance Considerations:**
- No pagination required (portfolio project, limited data)
- File uploads handled synchronously (acceptable for demo)
- Markdown rendering on client side (no server-side rendering)
- Simple file storage (no CDN or cloud storage)
- SQLite adequate for file metadata queries

**Security Considerations:**
- Sanitize filenames for download (prevent directory traversal)
- XSS prevention via DOMPurify for markdown HTML
- Validate file paths stay within uploads directory
- No file type restrictions as per user requirement (accept security trade-off)
- No authentication checks needed (single-user system)
