# Task Breakdown: Pipeline Stage Management

## Overview
Total Tasks: 4 Task Groups
Feature Type: Database extension with API and UI components
Integration: Extends Contact model from Feature #2 (Contact Management System)

## Task List

### Database Layer

#### Task Group 1: Pipeline Stage Field Integration
**Dependencies:** Contact model from Feature #2 must exist

- [ ] 1.0 Complete database layer for pipeline stage
  - [ ] 1.1 Write 2-8 focused tests for pipeline_stage functionality
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors:
      - Valid stage values accepted ('Lead', 'Qualified', 'Proposal', 'Client')
      - Invalid stage values rejected with appropriate error
      - Default value 'Lead' applied to new contacts
      - NOT NULL constraint prevents null stages
    - Skip exhaustive edge case testing
  - [ ] 1.2 Add pipeline_stage field to Contact model
    - Location: /home/yaakov/git/SimpleCRM/backend/app/models/contact.py
    - Field type: String with validation or ENUM
    - Valid values: 'Lead', 'Qualified', 'Proposal', 'Client'
    - Default value: 'Lead'
    - NOT NULL constraint
    - Add validation at model level using SQLAlchemy validators
    - Follow existing Contact model pattern with timestamps (created_at, updated_at)
  - [ ] 1.3 Create migration for pipeline_stage column
    - Location: /home/yaakov/git/SimpleCRM/backend/alembic/versions/[timestamp]_add_pipeline_stage_to_contacts.py
    - Add pipeline_stage column to contacts table
    - Column type: VARCHAR with CHECK constraint or ENUM type (match model implementation)
    - Default: 'Lead'
    - NOT NULL constraint
    - Create index on pipeline_stage column for efficient filtering (CREATE INDEX idx_contacts_pipeline_stage ON contacts(pipeline_stage))
    - Implement reversible down() method to drop column and index
    - Follow small, focused migration principle
  - [ ] 1.4 Ensure database layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify migration runs successfully (alembic upgrade head)
    - Verify migration rollback works (alembic downgrade -1, then upgrade again)
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- pipeline_stage field added to Contact model with proper validation
- Migration successfully adds column with index
- Migration is reversible
- Default value 'Lead' is applied to new contacts
- Invalid stage values are rejected at model level

---

### API Layer

#### Task Group 2: Pipeline Stage API Endpoints
**Dependencies:** Task Group 1

- [ ] 2.0 Complete API layer for pipeline stage
  - [ ] 2.1 Write 2-8 focused tests for pipeline stage API endpoints
    - Limit to 2-8 highly focused tests maximum
    - Test only critical API behaviors:
      - GET /api/contacts/:id returns contact with pipeline_stage field
      - PUT /api/contacts/:id updates pipeline_stage successfully
      - PUT /api/contacts/:id with invalid stage returns 400 error
      - GET /api/contacts/pipeline-stats returns correct stage distribution counts
    - Skip exhaustive testing of all scenarios
  - [ ] 2.2 Update Contact Pydantic schemas
    - Location: /home/yaakov/git/SimpleCRM/backend/app/schemas/contact.py
    - Add pipeline_stage field to ContactBase schema
    - Type: str with Field validator
    - Validation: Must be one of ['Lead', 'Qualified', 'Proposal', 'Client']
    - Default: 'Lead'
    - Include in ContactCreate, ContactUpdate, and ContactResponse schemas
    - Follow existing schema pattern with ConfigDict(from_attributes=True)
  - [ ] 2.3 Create PipelineStats response schema
    - Location: /home/yaakov/git/SimpleCRM/backend/app/schemas/contact.py
    - Define PipelineStatsResponse schema with stage counts
    - Fields: lead_count, qualified_count, proposal_count, client_count (all int)
    - Add total_count field for convenience
    - Follow Pydantic schema conventions
  - [ ] 2.4 Extend Contact CRUD endpoints to handle pipeline_stage
    - Location: /home/yaakov/git/SimpleCRM/backend/app/routers/contacts.py
    - Ensure GET /api/contacts/:id includes pipeline_stage in response
    - Ensure POST /api/contacts creates contacts with pipeline_stage (default 'Lead')
    - Ensure PUT /api/contacts/:id updates pipeline_stage field
    - Add validation to reject invalid stage values (return 400 Bad Request with clear error message)
    - Follow existing router pattern with Depends(get_current_user) for authentication
    - Use comprehensive docstrings with examples
  - [ ] 2.5 Implement pipeline statistics endpoint
    - Location: /home/yaakov/git/SimpleCRM/backend/app/routers/contacts.py
    - Create GET /api/contacts/pipeline-stats endpoint
    - Return contact counts grouped by pipeline_stage
    - Filter by current authenticated user's contacts only
    - Use SQLAlchemy group_by and count queries
    - Return PipelineStatsResponse schema
    - Follow RESTful conventions and existing API patterns
  - [ ] 2.6 Add business logic to ContactService (if service layer exists)
    - Location: /home/yaakov/git/SimpleCRM/backend/app/services/contact_service.py (if applicable)
    - Add validate_pipeline_stage() static method
    - Add get_pipeline_stats() method for counting logic
    - Raise ValueError for invalid stages (caught in router for proper HTTP errors)
    - Follow existing service layer pattern with static methods
  - [ ] 2.7 Ensure API layer tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify pipeline_stage field is included in contact responses
    - Verify stage updates work correctly
    - Verify pipeline-stats endpoint returns accurate counts
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Contact endpoints include pipeline_stage field
- Stage validation returns 400 for invalid values
- Pipeline stats endpoint returns accurate counts filtered by user
- API follows RESTful conventions and existing patterns

---

### Frontend Components

#### Task Group 3: Pipeline Stage UI Components
**Dependencies:** Task Group 2

- [ ] 3.0 Complete pipeline stage UI components
  - [ ] 3.1 Write 2-8 focused tests for UI components
    - Limit to 2-8 highly focused tests maximum
    - Test only critical component behaviors:
      - StageSelector component renders all 4 stages
      - StageSelector emits stage-change event when selection changes
      - PipelineOverview component displays stage counts correctly
      - PipelineOverview component updates when data changes
    - Skip exhaustive testing of all component states and interactions
  - [ ] 3.2 Create API service methods for pipeline stage
    - Location: /home/yaakov/git/SimpleCRM/frontend/src/services/api.js (or contactService.js)
    - Add updateContactStage(contactId, stage) method
    - Add getPipelineStats() method
    - Use existing apiGet, apiPut helper functions
    - Follow getAuthHeaders() pattern for authenticated requests
    - Apply handleResponse() for consistent error handling
  - [ ] 3.3 Create StageSelector component
    - Location: /home/yaakov/git/SimpleCRM/frontend/src/components/StageSelector.vue
    - Component type: Dropdown or button group for selecting pipeline stage
    - Props: modelValue (current stage), contactId
    - Emits: update:modelValue event when stage changes
    - Display all 4 stages: Lead, Qualified, Proposal, Client
    - One-click stage change (no confirmation dialog)
    - Call updateContactStage API method on change
    - Use Tailwind CSS classes consistent with existing components (border, rounded-md, px-3, py-2)
    - Follow Vue 3 Composition API with &lt;script setup&gt;
    - Apply defineProps and defineEmits for component communication
  - [ ] 3.4 Create PipelineOverview component
    - Location: /home/yaakov/git/SimpleCRM/frontend/src/components/PipelineOverview.vue
    - Component type: Simple list/table displaying contact counts per stage
    - Display all 4 stages with counts: Lead (X), Qualified (X), Proposal (X), Client (X)
    - Visual representation: Simple list or progress bar indicators
    - Fetch data from getPipelineStats() API method
    - Auto-refresh when prop changes or on mount
    - Use Tailwind CSS for styling (bg-white, shadow, rounded-lg, p-4)
    - Follow Vue 3 Composition API with &lt;script setup&gt;
    - Use consistent layout structure (max-w-7xl, mx-auto)
  - [ ] 3.5 Integrate StageSelector into contact detail/edit views
    - Location: /home/yaakov/git/SimpleCRM/frontend/src/views/ContactDetailView.vue (or similar)
    - Add StageSelector component to contact detail or edit form
    - Bind to contact's current pipeline_stage
    - Handle stage-change event to update contact
    - Display current stage prominently
    - Follow existing form layout patterns
  - [ ] 3.6 Integrate PipelineOverview into dashboard or contact list
    - Location: /home/yaakov/git/SimpleCRM/frontend/src/views/DashboardView.vue (or ContactListView.vue)
    - Add PipelineOverview component to dashboard or top of contact list
    - Position in prominent location for quick visibility
    - Ensure overview updates when contacts are created, updated, or deleted
    - Follow existing dashboard layout patterns
  - [ ] 3.7 Ensure UI component tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify StageSelector component renders and emits events correctly
    - Verify PipelineOverview component displays counts accurately
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- StageSelector component allows one-click stage updates
- PipelineOverview component displays accurate counts
- Components integrated into appropriate views
- Styling consistent with existing application design
- Vue 3 Composition API patterns followed

---

### Integration Testing

#### Task Group 4: End-to-End Workflow Testing
**Dependencies:** Task Groups 1-3

- [ ] 4.0 Review and test complete pipeline stage workflow
  - [ ] 4.1 Review existing tests from Task Groups 1-3
    - Review the 2-8 tests written by database-engineer (Task 1.1)
    - Review the 2-8 tests written by api-engineer (Task 2.1)
    - Review the 2-8 tests written by ui-designer (Task 3.1)
    - Total existing tests: approximately 6-24 tests
  - [ ] 4.2 Analyze test coverage gaps for Pipeline Stage Management feature only
    - Identify critical user workflows that lack test coverage:
      - Creating new contact defaults to 'Lead' stage
      - Updating contact stage through UI updates database
      - Pipeline overview reflects accurate counts after stage changes
      - Invalid stage values are handled gracefully
    - Focus ONLY on gaps related to pipeline stage feature requirements
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows over unit test gaps
  - [ ] 4.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration points and end-to-end workflows:
      - Full workflow: Create contact -> Verify 'Lead' stage -> Update to 'Qualified' -> Verify pipeline stats updated
      - Error handling: Attempt invalid stage update -> Verify error message displayed
      - Multi-user: Verify pipeline stats filtered by current user only
    - Do NOT write comprehensive coverage for all scenarios
    - Skip edge cases and performance tests unless business-critical
  - [ ] 4.4 Manual testing checklist
    - Create new contact and verify default 'Lead' stage appears
    - Update contact through each stage transition (Lead -> Qualified -> Proposal -> Client)
    - Verify pipeline overview counts update immediately
    - Attempt invalid stage value through API (should fail with 400)
    - Verify stage persists after page refresh
    - Test with multiple users to ensure stats are user-specific
  - [ ] 4.5 Run feature-specific tests only
    - Run ONLY tests related to pipeline stage feature (tests from 1.1, 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-34 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical workflows pass
    - Fix any failing tests before considering feature complete

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-34 tests total)
- Critical user workflows for pipeline stage management are covered
- No more than 10 additional tests added when filling in testing gaps
- Manual testing checklist completed successfully
- Pipeline stage feature works end-to-end from database to UI
- Feature integrates smoothly with Contact Management System

---

## Execution Order

Recommended implementation sequence:
1. **Database Layer** (Task Group 1) - Add pipeline_stage field to Contact model with migration
2. **API Layer** (Task Group 2) - Extend contact endpoints and add pipeline stats endpoint
3. **Frontend Components** (Task Group 3) - Build StageSelector and PipelineOverview components
4. **Integration Testing** (Task Group 4) - Verify end-to-end workflows and fill critical test gaps

## Important Notes

### Integration with Feature #2 (Contact Management System)
- This feature EXTENDS the Contact model from Feature #2
- Contact model must exist before starting Task Group 1
- Coordinate with Contact Management System implementation timing
- Reuse Contact CRUD patterns and authentication flow

### Testing Philosophy
- Write minimal, focused tests during development (2-8 per task group)
- Test only critical paths and primary user workflows
- Defer comprehensive edge case testing
- Total expected tests: 16-34 for entire feature

### Technology Stack Alignment
- Backend: FastAPI + SQLAlchemy + Pydantic
- Frontend: Vue 3 Composition API + Tailwind CSS
- Database: SQLite with proper indexes
- Testing: pytest (backend), Vitest (frontend)

### Key Design Decisions
- Fixed 4-stage pipeline (hardcoded, non-customizable)
- No stage transition history tracking
- Simple list/table view (not Kanban board)
- One-click stage updates (no confirmation dialogs)
- User-specific pipeline statistics (filtered by authenticated user)
