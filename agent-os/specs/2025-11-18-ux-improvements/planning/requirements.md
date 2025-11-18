# Spec Requirements: UX Improvements

## Initial Description
Requested UX improvements for SimpleCRM:

1. Add counts of available matches to the filter drop-down on the Contacts page (e.g., "All Stages (15)"). If possible, count matching search results, not the whole list.

2. Dashboard now fully included in Contacts page:
   - Login should go directly to Contacts page
   - Remove the Dashboard completely

3. Apply the same count change for Filter by Type in Activity Timeline

4. Allow attaching files directly when creating an activity with "Add Activity":
   - Solution: Empty activities are fully permitted (like empty documents in Google Docs)
   - All activity records owned by the user - can create, see, and remove as desired
   - No automation required
   - Create activity ID when user clicks "New Activity" (renamed from "Add Activity")
   - Always say "Update Activity", never "Create Activity" as the activity already exists
   - Default value for activity: Note (no "Select type" option)

5. Show the Pipeline Stage in the timeline - stage changes are part of an activity:
   - Add pipeline stage column to activities database table
   - Contact's current pipeline stage = stage from last activity, or "Lead" when no activities
   - New activities take stage from previous activity (but can be changed)
   - Show pipeline stage badge in timeline ONLY when it differs from previous stage
   - Show current badge next to contact name
   - Remove change-stage selector from Contact Info tab

6. Passive Contacts - Add stages "Qualified Out", "Lost Proposal", "Work Completed", "Archived":
   - Create two tabs to select contacts: Active (Lead, Qualified, Proposal, Client) and Passive (new stages)
   - Passive clients not visible when working in active clients tab
   - Separate passive options from active options with a line in the dropdown for status change

7. Equal space: Use most of screen width and divide space equally between Contacts list and Timeline/Contact info

8. Show info from contact under the contact name in right side (above timeline/contact info tabs): Add title and company name - linked to website

## Requirements Discussion

### First Round Questions

**Q1:** For filter counts, should they reflect the FILTERED results (e.g., if I search for "John", show counts of matches within those search results) or the TOTAL counts regardless of search?
**Answer:** Filter counts should reflect FILTERED results (after search is applied).

**Q2:** When removing the Dashboard, should I remove ALL references (NavigationBar link, route, view component) or keep the code but redirect to Contacts?
**Answer:** Remove all references including NavigationBar link.

**Q3:** For the empty activity pattern - when user clicks "New Activity", should the system:
- POST immediately to create empty activity, then open modal with activity ID for editing? OR
- Open modal first, create activity only when user clicks Save?
**Answer:** POST creates empty activity (type='Note', subject='', notes=null, activity_date=now) immediately, open modal with activity ID for editing. Modal title always "Update Activity". User can attach files immediately. User can save or close, leaving empty activity.

**Q4:** For empty activities that are never filled in - should they:
- Appear in the timeline (user must manually delete if unwanted)? OR
- Have some automatic cleanup logic?
**Answer:** Empty activities appear in timeline. User must manually delete if unwanted. No automation.

**Q5:** For moving pipeline_stage from contacts to activities:
- Add `pipeline_stage` column to activities table
- Remove `pipeline_stage` column from contacts table
- Contact's current stage = stage from most recent activity
- If no activities, contact is "Lead"
- Confirm removal of StageSelector from Contact Info tab
**Answer:** All confirmed.

**Q6:** For stage change badges in timeline - show badge:
- ONLY when stage changed from previous activity? OR
- On every activity showing its stage?
**Answer:** Show badge ONLY when stage changed. Badge shows the new stage name (e.g., "Qualified", "Client").

**Q7:** For the Passive/Active tabs UI - should they be:
- Above the search/filter area with counts like "Active (15)" and "Passive (3)"? OR
- Part of the stage filter dropdown?
**Answer:** Tabs above search/filter area. "Active (15)" and "Passive (3)" format. Highlighted selected tab. Filter dropdown options change based on active tab.

**Q8:** For the pipeline stage dropdown (when changing stage on an activity) - should there be a visual separator (horizontal line) between active and passive stages?
**Answer:** Yes, visual separator between active and passive stages.

**Q9:** For equal width columns - the current layout is grid-cols-3 with contact list taking 2 columns (col-span-2) and preview taking 1 column (col-span-1). Should I change to grid-cols-2 with both panels having equal col-span-1, using more of the screen width?
**Answer:** Yes, change to grid-cols-2 with equal col-span-1. Use more screen width. Both panels should have equal horizontal space.

**Q10:** For contact info under name (job_title and company) - if fields are empty, should I:
- Show nothing? OR
- Show placeholder text?
Format: "[job_title] at [company]" with company linked to website?
**Answer:** Format: "[job_title] at [company]" with company linked to website. If website empty, company as plain text. If job_title empty, just show company.

**Q11:** Migration strategy - since pipeline_stage is moving from contacts to activities:
- Delete existing data (it's a demo project)? OR
- Attempt data migration (create activities for existing contacts with their current stage)?
**Answer:** Delete existing data (demo project).

**Q12:** Stage badge next to contact name - should this appear:
- Only in ContactPreview header (right panel)? OR
- Also in contacts list table (left panel)?
**Answer:** Show in ContactPreview header (right panel) AND in contacts list table (left panel).

**Q13:** Out of scope items - confirm these are NOT included:
- Sorting contacts by different fields
- Bulk stage changes
- Stage change history view
- Custom stage names
- Date range filtering on activities
**Answer:** All mentioned suggestions are out of scope.

### Existing Code to Reference

**Similar Features Identified:**

User did not provide specific paths to similar features, but from code review:

- **Tab Pattern:** ContactPreview.vue (lines 24-49) shows tab implementation with border-bottom highlighting
- **Badge Styling:** ActivityItem.vue (lines 7-14) shows badge pattern with color classes; ContactsView.vue (lines 295-303) shows getStageClass() function for stage badges
- **Modal Pattern:** ActivityForm.vue shows full modal implementation with overlay and form
- **Dropdown/Select Pattern:** StageSelector.vue shows select dropdown with stages; ActivityTimeline.vue shows filter dropdown
- **Grid Layout:** ContactsView.vue (line 7) uses grid-cols-3 pattern that needs to be changed to grid-cols-2

**Components to Potentially Reuse:**
- Badge styling patterns from ActivityItem.vue
- Tab UI from ContactPreview.vue
- Modal overlay from ActivityForm.vue
- Select dropdown patterns from StageSelector.vue and ActivityTimeline.vue
- Grid layout classes from ContactsView.vue

**Backend Logic to Reference:**
- Activity model: `/home/yaakov/git/SimpleCRM/backend/app/models/activity.py`
- Contact model: `/home/yaakov/git/SimpleCRM/backend/app/models/contact.py`
- Activity service: `/home/yaakov/git/SimpleCRM/backend/app/services/activity_service.py`
- Contact service: `/home/yaakov/git/SimpleCRM/backend/app/services/contact_service.py`

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets to analyze.

## Requirements Summary

### Functional Requirements

#### 1. Filter Counts (Contacts Page)
- Add counts to stage filter dropdown showing filtered results
- Format: "All Stages (15)", "Lead (3)", "Qualified (5)", etc.
- Counts reflect current search results, not total database
- Update counts dynamically as user types in search field

#### 2. Filter Counts (Activity Timeline)
- Add counts to type filter dropdown showing filtered results
- Format: "All Types (10)", "Call (2)", "Meeting (3)", etc.
- Counts reflect current search results within selected contact's activities

#### 3. Dashboard Removal
- Remove `/dashboard` route from router
- Remove DashboardView.vue component (or leave but unreferenced)
- Remove "Dashboard" link from NavigationBar.vue
- Change root path redirect from `/dashboard` to `/contacts`
- Update authentication flow to redirect to `/contacts` after login

#### 4. Empty Activity Creation
- Rename "Add Activity" button to "New Activity"
- On click, immediately POST to create empty activity with:
  - type: 'Note'
  - subject: '' (empty string)
  - notes: null
  - activity_date: current timestamp
  - pipeline_stage: copied from most recent activity or 'Lead' if no previous activities
- Backend returns created activity with ID
- Frontend immediately opens ActivityForm modal with activity ID
- Modal title is always "Update Activity" (never "Create Activity")
- File attachments can be added immediately since activity exists
- User can close modal without filling fields (empty activity remains in timeline)
- User must manually delete empty activities if unwanted

#### 5. Pipeline Stage Migration to Activities

**Database Changes:**
- Add `pipeline_stage` column to activities table (String(50), nullable=False, index=True)
- Remove `pipeline_stage` column from contacts table
- Migration approach: Delete existing data (demo project)

**Business Logic:**
- Contact's current pipeline stage determined by:
  - Stage from most recent activity (by activity_date DESC)
  - Default to 'Lead' if contact has no activities
- New activity defaults to stage from most recent activity (user can change)
- Stage options for activities: Lead, Qualified, Proposal, Client, Qualified Out, Lost Proposal, Work Completed, Archived

**UI Changes:**
- Remove StageSelector component from ContactPreview "Contact Info" tab
- Add pipeline_stage field to ActivityForm
- Show stage change badge in timeline ONLY when stage differs from previous activity
- Badge shows new stage name (e.g., "Qualified", "Client")
- Badge uses same color scheme as existing stage badges

#### 6. Passive Contacts / Active-Passive Tabs

**New Pipeline Stages:**
- Active stages: Lead, Qualified, Proposal, Client
- Passive stages: Qualified Out, Lost Proposal, Work Completed, Archived

**Tab UI (ContactsView):**
- Add tabs above search/filter area
- Two tabs: "Active (count)" and "Passive (count)"
- Counts show total contacts in each category based on current filters
- Selected tab highlighted with blue underline (same style as ContactPreview tabs)
- Active tab selected by default

**Filter Behavior:**
- Stage filter dropdown options change based on selected tab:
  - Active tab: show Lead, Qualified, Proposal, Client options
  - Passive tab: show Qualified Out, Lost Proposal, Work Completed, Archived options
- "All Stages" option always available

**Pipeline Stage Dropdown (ActivityForm):**
- Show all 8 stage options
- Visual separator (horizontal line/border) between active and passive stages
- Active stages listed first, then separator, then passive stages

#### 7. Equal Width Layout
- Change ContactsView grid from `grid-cols-3` to `grid-cols-2`
- Contact list (left): change from `col-span-2` to `col-span-1`
- Preview panel (right): keep `col-span-1`
- Adjust max-width if needed to use more screen width
- Both panels should have equal horizontal space

#### 8. Contact Info Under Name
- Display under contact name in ContactPreview header (above tabs)
- Format logic:
  - If job_title AND company: "[job_title] at [company]"
  - If only company: "[company]"
  - If only job_title: "[job_title]"
  - If neither: show nothing
- Company link behavior:
  - If website exists: link company name to website (target="_blank", rel="noopener noreferrer")
  - If website empty: show company as plain text
- Styling: smaller font than name, gray text, company link in blue

#### 9. Stage Badge Display
- Show current stage badge in two locations:
  - ContactPreview header (right panel): next to or below contact name
  - Contacts list table (left panel): in the Stage column (already exists, ensure consistency)
- Use same badge styling as existing stage badges (getStageClass pattern)
- Badge colors by stage:
  - Lead: yellow (bg-yellow-100 text-yellow-800)
  - Qualified: blue (bg-blue-100 text-blue-800)
  - Proposal: purple (bg-purple-100 text-purple-800)
  - Client: green (bg-green-100 text-green-800)
  - Passive stages: gray or red tones (to be determined during implementation)

### Reusability Opportunities

**Existing Components to Reference:**
- **Tab Pattern:** ContactPreview.vue lines 24-49 for Active/Passive tabs
- **Badge Component:** Could extract badge styling into reusable component (currently inline in ActivityItem and ContactsView)
- **Modal Pattern:** ActivityForm.vue for consistent modal behavior
- **Dropdown Pattern:** StageSelector.vue and ActivityTimeline.vue filter dropdowns

**Backend Patterns:**
- Activity creation pattern in activity_service.py
- Stage validation logic (will need to expand for new passive stages)
- Query patterns for filtering by stage and type

**Potential Abstractions:**
- StageBadge component for consistent stage display
- FilterDropdown component with counts
- TabGroup component for Active/Passive pattern

### Scope Boundaries

**In Scope:**
- Filter counts on Contacts page stage dropdown
- Filter counts on Activity Timeline type dropdown
- Complete removal of Dashboard (route, view, navigation)
- Empty activity creation workflow
- File attachment on empty activities
- Pipeline stage migration from contacts to activities
- Four new passive stages
- Active/Passive tabs with filtering
- Visual separator in stage dropdown
- Equal width layout for contacts list and preview
- Contact info display under name
- Stage badges in timeline (on change only)
- Stage badges next to contact name (both panels)
- Migration strategy: delete existing data

**Out of Scope:**
- Sorting contacts by different fields
- Bulk stage changes
- Stage change history view
- Custom stage names or user-defined stages
- Date range filtering on activities
- Activity templates
- Activity reminders or notifications
- Drag-and-drop stage changes
- Kanban-style pipeline view
- Analytics on stage conversion rates
- Export functionality
- Mobile-specific optimizations

### Technical Considerations

**Frontend (Vue.js 3):**
- Computed properties for filter counts based on filtered data
- Reactive tab state for Active/Passive
- Modal state management for empty activity creation
- Router update to remove dashboard route and redirect to contacts
- Component updates: ContactsView, ActivityTimeline, ActivityForm, ContactPreview, NavigationBar
- Potential new components: StageBadge (optional)

**Backend (FastAPI/Python):**
- Database migration to add pipeline_stage to activities, remove from contacts
- Activity model update with pipeline_stage enum (8 values)
- Contact model update to remove pipeline_stage column
- Contact service logic to compute current stage from activities
- Activity service logic to default new activity stage to previous stage
- API endpoint updates to support new stage values
- Validation for new stage values

**Database (SQLite/SQLAlchemy):**
- Migration script to:
  - Add pipeline_stage column to activities table
  - Remove pipeline_stage column from contacts table
  - Drop existing data (demo project, no data migration needed)
- Update Activity model enum with all 8 stages
- Add index on activities.pipeline_stage for query performance

**Testing:**
- Test empty activity creation workflow
- Test file attachment on empty activities
- Test stage computation from activities
- Test Active/Passive tab filtering
- Test filter counts with search combinations
- Test stage badge display logic (show only on change)
- Test contact info formatting with various field combinations

**Performance:**
- Filter counts computed on filtered dataset (already in memory)
- Stage computation may require additional query (get most recent activity)
- Consider caching contact's current stage if performance issues arise
- Index on activities.pipeline_stage and activity_date for efficient queries

**Data Migration:**
- No data migration required (delete existing demo data)
- Document that this is a breaking change requiring fresh database
- Update seed data scripts if they exist

**User Experience:**
- Empty activities visible in timeline (intentional - no automatic cleanup)
- Users can manually delete empty activities via timeline item actions
- Stage changes reflected immediately in both panels
- Counts update as user types (debounced search already exists)
- Active/Passive tabs provide clear separation of contact lifecycle states
