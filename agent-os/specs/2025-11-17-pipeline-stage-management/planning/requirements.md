# Spec Requirements: Pipeline Stage Management

## Initial Description
Pipeline Stage Management

## Requirements Discussion

### First Round Questions

**Q1: Stage Customization - Are the stages fixed or customizable?**
**Answer:** Fixed 4-stage pipeline (Lead, Qualified, Proposal, Client) - non-customizable for MVP

**Q2: View Type - Should we implement a Kanban board view or simple list/table view?**
**Answer:** Simple list/table view with stage-wise contact distribution - Kanban board is out of scope

**Q3: Stage Changes - What validation or confirmation is needed when changing a contact's stage?**
**Answer:** One-click update - no validation or confirmation needed

**Q4: Pipeline Overview Location - Should this be a dedicated page or integrated into dashboard/contact list?**
**Answer:** Integrated into dashboard or contact list (not a dedicated page)

**Q5: Stage History - Should we track when contacts move between stages and maintain a history?**
**Answer:** Just current stage - no stage transition history tracking

**Q6: Default Stage - What stage should new contacts default to?**
**Answer:** New contacts default to 'Lead' stage

**Q7: Stage-Specific Logic - Should different stages trigger different behaviors, fields, or workflows?**
**Answer:** Purely organizational - no automated actions, no stage-specific fields or workflows

**Q8: Exclusions - What should explicitly NOT be included in this MVP?**
**Answer:** Stage customization, automated stage progression, stage-specific custom fields, revenue reporting by stage, time-in-stage analytics are all out of scope

**Q9: Existing Code Reuse - Are there existing features with similar patterns we should reference?**
**Answer:** No advanced features to reuse. Use existing pages for consistent styling. Reference Contact Management System data models

**Q10: Visual Assets - Do you have any design mockups or wireframes?**
**Answer:** No visuals provided

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Contact Management System (Feature #2) - Path: To be developed concurrently
- Data models to reference: Contact model will contain the pipeline_stage field
- UI patterns to reuse: Existing page layouts and styling conventions from the application

**Integration Note:**
This feature is tightly coupled with Feature #2 (Contact Management System). The pipeline_stage field will be added to the Contact model, and the pipeline overview will be integrated into contact-related views.

### Follow-up Questions
No follow-up questions were needed - requirements were clearly defined in initial responses.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - No visuals to analyze

## Requirements Summary

### Functional Requirements

**Core Pipeline Management:**
- Fixed 4-stage pipeline: Lead → Qualified → Proposal → Client
- Each contact has exactly one current stage (no multi-stage or no-stage contacts)
- New contacts automatically default to 'Lead' stage
- Simple one-click stage updates with no validation or confirmation dialogs
- No stage customization interface (stages are hardcoded)

**Pipeline Overview Display:**
- Show contact distribution across all 4 stages
- Display as simple list/table view (not Kanban)
- Integrated into dashboard or contact list (not a standalone page)
- Visual representation of contact counts per stage

**Contact Stage Management:**
- Add pipeline_stage field to Contact model
- Support reading and updating a contact's current stage
- Stage changes via simple dropdown or button interface
- Immediate stage updates without workflows or validation

**Data Model Integration:**
- pipeline_stage field added to Contact model (enum or string field)
- Valid values: 'Lead', 'Qualified', 'Proposal', 'Client'
- Default value: 'Lead'
- No stage history tracking table (only current stage stored)

### Reusability Opportunities

**Components to Reference:**
- Existing page layouts for consistent styling
- Contact Management System's data models for Contact schema
- Any existing dropdown or selection UI components
- Dashboard layout patterns if pipeline overview goes there

**Backend Patterns:**
- Follow Contact Management System's CRUD patterns
- Use SQLAlchemy model structure consistent with Contact model
- Leverage FastAPI router patterns from existing features

**Frontend Patterns:**
- Vue 3 Composition API patterns from existing components
- Tailwind CSS utility classes for consistent styling
- API service patterns for backend communication

### Scope Boundaries

**In Scope:**
- Fixed 4-stage pipeline (Lead, Qualified, Proposal, Client)
- pipeline_stage field on Contact model
- One-click stage updates for contacts
- Simple list/table view showing contact distribution by stage
- Integration of pipeline overview into dashboard or contact list
- Default 'Lead' stage for new contacts
- Basic UI for displaying and changing contact stages

**Out of Scope:**
- Stage customization (adding, removing, renaming stages)
- Kanban board or drag-and-drop interface
- Stage transition history or audit log
- Stage-specific validation or confirmation dialogs
- Automated stage progression based on rules
- Stage-specific custom fields or workflows
- Revenue reporting broken down by stage
- Time-in-stage analytics
- Stage change notifications or alerts
- Bulk stage updates for multiple contacts
- Stage-based access controls or permissions

**Future Enhancements (Explicitly Deferred):**
- Kanban board view (Phase 2, Roadmap item #12)
- Stage transition history tracking
- Revenue by stage reporting (part of Revenue Tracking feature)
- Time-in-stage metrics (part of Dashboard & Analytics feature)
- Automated stage progression rules
- Customizable pipeline stages

### Technical Considerations

**Database Schema:**
- Add `pipeline_stage` column to `contacts` table
- Type: ENUM('Lead', 'Qualified', 'Proposal', 'Client') or VARCHAR with validation
- Default: 'Lead'
- NOT NULL constraint (every contact must have a stage)
- Index on pipeline_stage for efficient filtering/grouping

**Backend Implementation:**
- Update Contact model (SQLAlchemy) to include pipeline_stage field
- Add validation to ensure only valid stage values are accepted
- Implement GET endpoint to retrieve stage distribution counts
- Update existing contact CRUD endpoints to handle stage field
- Follow FastAPI + SQLAlchemy patterns from tech stack

**Frontend Implementation:**
- Use Vue 3 Composition API
- Implement stage selector component (dropdown or button group)
- Create pipeline overview component showing contact counts per stage
- Integrate overview into dashboard or contact list view
- Use Tailwind CSS for styling consistent with existing pages
- API service methods for fetching stage counts and updating contact stages

**Integration Points:**
- Contact Management System (Feature #2) - shared Contact model
- Dashboard (future feature) - potential home for pipeline overview
- Contact list view - alternative location for pipeline overview

**Technology Alignment:**
- FastAPI for backend endpoints
- SQLAlchemy ORM for database operations
- Vue 3 Composition API for frontend components
- Tailwind CSS for styling
- SQLite database
- Pydantic schemas for API validation

**Testing Requirements:**
- Backend unit tests for stage validation
- Backend integration tests for stage update endpoints
- Frontend component tests for stage selector
- Frontend tests for pipeline overview display
- Test default stage assignment for new contacts
- Test stage distribution counting logic
