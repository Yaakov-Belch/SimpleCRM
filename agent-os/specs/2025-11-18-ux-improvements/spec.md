# Specification: UX Improvements

## Goal
Enhance SimpleCRM's user experience with improved filtering, activity creation workflow, pipeline stage visualization, passive contact management, layout improvements, and contact information display.

## User Stories
- As a user, I want to see counts in filter dropdowns so I can quickly understand data distribution without guessing
- As a user, I want to attach files when creating a new activity without saving it first so I can complete my work in one flow
- As a user, I want to see pipeline stage changes in the activity timeline so I can track contact progression visually

## Specific Requirements

**Filter Counts on Contacts Page**
- Add count badges to stage filter dropdown showing number of contacts per stage (e.g., "Lead (15)")
- Count should reflect filtered search results when search query is active, not just total contacts
- Apply same filter count pattern to Activity Timeline type filter (e.g., "Call (5)", "Note (12)")
- Display counts dynamically using existing backend queries with minimal overhead
- Update counts reactively when contacts are created, deleted, or stage is changed

**Remove Dashboard and Redirect to Contacts**
- Update router to redirect root path "/" directly to "/contacts" instead of "/dashboard"
- Update login success redirect to go to "/contacts" instead of "/dashboard"
- Remove Dashboard navigation link from NavigationBar component
- Keep DashboardView.vue file but unused (do not delete) for potential future use
- Update auth guard to redirect authenticated users accessing public routes to "/contacts"

**Empty Activity Creation with Immediate ID**
- Change "Add Activity" button text to "New Activity" for consistency with "New Contact"
- Create activity record in database immediately when user clicks "New Activity" (before filling any fields)
- Pre-populate activity with default values: type="Note", activity_date=current datetime
- Allow empty subject field initially (validate only on explicit save/update action)
- Change form submit button text from "Create Activity" to "Update Activity" always
- Empty activities (no subject, no notes, no attachments) are permitted and user-owned
- Display newly created empty activity in timeline immediately

**Pipeline Stage in Activities Database**
- Add pipeline_stage column to activities table (String, nullable=False, default="Lead", indexed)
- New activity inherits pipeline_stage from most recent previous activity for same contact
- If no previous activities exist for contact, default to "Lead"
- Allow user to change pipeline_stage when creating/editing activity via dropdown in ActivityForm
- Contact's current pipeline_stage is derived from most recent activity's pipeline_stage
- Remove pipeline_stage column from contacts table (deprecated by activity-based tracking)
- Contact model should compute current_pipeline_stage property from latest activity

**Pipeline Stage Badges in Timeline**
- Display pipeline stage badge in ActivityItem only when stage differs from previous activity
- Sort activities by activity_date descending to determine "previous" activity
- Show current pipeline stage badge next to contact name in ContactPreview header
- Use existing badge styling with stage-specific colors (Lead=yellow, Qualified=blue, Proposal=purple, Client=green)
- Add new passive stage colors: Qualified Out=gray, Lost Proposal=red, Work Completed=teal, Archived=slate
- Remove StageSelector component from Contact Info tab (stage changes now happen via activities)

**Passive Contact Stages**
- Add four new pipeline stages: "Qualified Out", "Lost Proposal", "Work Completed", "Archived"
- Create Active/Passive tab system in ContactsView for filtering contact visibility
- Active tab shows: Lead, Qualified, Proposal, Client stages only (with total count badge)
- Passive tab shows: Qualified Out, Lost Proposal, Work Completed, Archived stages only (with total count badge)
- Default view is Active tab
- In pipeline stage dropdown (in ActivityForm), separate active and passive stages with visual divider line
- Update backend pipeline stats endpoint to return separate active_count and passive_count
- Update PipelineOverview component to show only active stages

**Equal Space Layout**
- Update ContactsView grid from "grid-cols-3" with "col-span-2" and "col-span-1" to equal 50/50 split
- Use "grid-cols-2" with each column taking "col-span-1"
- Increase max-width container from "max-w-7xl" to "max-w-full" with appropriate padding
- Ensure responsive behavior maintains equal columns on desktop, stacks on mobile

**Contact Info Display Above Tabs**
- Move job_title and company from Contact Info tab to ContactPreview header section
- Display below contact name but above Timeline/Contact Info tabs
- Make company name a clickable link to website (if website field exists)
- Format: "[Job Title] at [Company]" with company linked to website
- If no job_title, show just company name linked
- If no website, display company as plain text
- Add subtle styling (text-sm, text-gray-600) to differentiate from contact name

## Visual Design
No visual mockups provided. Follow existing SimpleCRM design patterns using Tailwind CSS.

## Existing Code to Leverage

**ContactsView.vue - Filter and Search Pattern**
- Reuse existing stageFilter select dropdown structure (lines 34-46)
- Extend with count badges using parentheses format
- Leverage onFilterChange handler to update counts reactively
- Apply same pattern to ActivityTimeline filterType dropdown

**ActivityForm.vue - File Upload Logic**
- Current implementation prevents uploads until activity exists (lines 291-294)
- Remove this restriction once activities are created immediately
- Reuse existing uploadAttachment, deleteAttachment API calls
- Keep attachment display list and delete handlers unchanged

**Contact and Activity Models - Relationships**
- Contact has activities relationship with cascade delete (backend/app/models/contact.py)
- Activity has contact_id foreign key with CASCADE delete (backend/app/models/activity.py)
- Add pipeline_stage column to Activity model following same pattern as Contact.pipeline_stage
- Activity already has created_at, updated_at timestamps for ordering

**ContactService.get_pipeline_stats - Counting Pattern**
- Extend existing stats query to include new passive stages
- Use same group_by pattern to count contacts per stage
- Add active_count and passive_count aggregate fields
- Return counts separated by active vs passive categories

**StageSelector.vue - Dropdown Pattern**
- Reuse dropdown styling and stage array structure
- Extend stages array with passive options
- Add visual separator (optgroup or hr) between active and passive stages
- Remove this component from ContactPreview Contact Info tab section

## Out of Scope
- Automated cleanup of empty activities (user manages their own activities)
- Activity draft/publish workflow (all activities are immediately live)
- Stage change activity auto-generation (stage changes only via manual activity creation)
- Contact-level pipeline_stage direct editing (must use activities to change stage)
- Migration of existing contact pipeline_stage to activities (manual data migration)
- Filtering contacts by date ranges or custom fields
- Bulk stage updates or bulk contact operations
- Activity templates or quick-add presets
- Pipeline stage validation rules or workflows
- Email/calendar integration for activities
