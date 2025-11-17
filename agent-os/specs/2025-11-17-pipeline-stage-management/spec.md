# Specification: Pipeline Stage Management

## Goal
Enable users to organize contacts across a fixed 4-stage sales pipeline (Lead, Qualified, Proposal, Client) with simple stage updates and visual distribution overview integrated into the contact management interface.

## User Stories
- As a sales user, I want to assign each contact to a pipeline stage so that I can organize my sales workflow
- As a sales user, I want to see how many contacts are in each stage so that I can understand my pipeline distribution at a glance

## Specific Requirements

**Fixed 4-Stage Pipeline**
- Pipeline consists of exactly 4 stages in order: Lead, Qualified, Proposal, Client
- Stage names and order are hardcoded and non-customizable in MVP
- Every contact must have exactly one current stage (no multi-stage or null values allowed)
- New contacts automatically default to 'Lead' stage
- No stage customization interface needed (add/remove/rename stages out of scope)

**Contact Model Integration**
- Add pipeline_stage field to Contact model as enum or validated string
- Valid values restricted to: 'Lead', 'Qualified', 'Proposal', 'Client'
- Default value set to 'Lead' for all new contacts
- NOT NULL constraint to enforce every contact has a stage
- Database index on pipeline_stage column for efficient filtering and grouping queries
- Store only current stage (no stage transition history tracking)

**Stage Update Functionality**
- Users can update a contact's stage with one-click action (dropdown or button interface)
- Stage changes apply immediately without validation dialogs or confirmation prompts
- No automated stage progression rules or workflows
- No stage-specific validation logic or business rules
- Stage updates persist via standard Contact update API endpoint

**Pipeline Overview Display**
- Show contact count distribution across all 4 stages
- Display as simple list or table view (not Kanban board)
- Integrated into dashboard or contact list view (not standalone page)
- Visual representation using counts or simple bar/progress indicators
- Overview updates when contacts are created, updated, or deleted
- Counts filtered by current authenticated user's contacts only

**Backend API Requirements**
- Extend existing Contact CRUD endpoints to handle pipeline_stage field
- Add GET endpoint to retrieve stage distribution counts (e.g., GET /api/contacts/pipeline-stats)
- Validate stage values on create/update to only accept valid stage names
- Return appropriate error messages for invalid stage values (400 Bad Request)
- Follow RESTful conventions and existing API patterns from User endpoints
- Use Pydantic schemas for request/response validation

**Frontend UI Components**
- Create StageSelector component (dropdown or button group) for changing contact stages
- Create PipelineOverview component displaying contact counts per stage
- Integrate PipelineOverview into DashboardView or contact list view
- Use Tailwind CSS classes consistent with existing component styling
- Follow Vue 3 Composition API patterns from existing components
- Implement API service methods for fetching pipeline stats and updating stages

**Database Migration**
- Create migration to add pipeline_stage column to contacts table
- Set column type as ENUM('Lead', 'Qualified', 'Proposal', 'Client') or VARCHAR with CHECK constraint
- Set default value to 'Lead'
- Add NOT NULL constraint
- Create index on pipeline_stage column
- Ensure migration is reversible with proper down/rollback method

**Testing Coverage**
- Backend unit tests for pipeline_stage validation on Contact model
- Backend integration tests for stage distribution counting logic
- Backend tests for invalid stage value rejection
- Frontend component tests for StageSelector user interactions
- Frontend tests for PipelineOverview rendering and data display
- Test default stage assignment on new contact creation

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Contact Model (Feature #2 - Contact Management System)**
- This feature extends the Contact model being developed concurrently
- Follow Contact model structure with SQLAlchemy Base, timestamps (created_at, updated_at)
- Use same table naming convention (plural: contacts)
- Follow same relationship pattern (Contact belongs to User)
- Apply consistent field validation patterns

**User Model and Authentication Patterns**
- Reference User model structure for SQLAlchemy column definitions and constraints
- Use same timestamp approach (created_at, updated_at with datetime.utcnow defaults)
- Follow indexing pattern (index=True on frequently queried fields)
- Apply same authentication dependency pattern (get_current_user) for API endpoints

**API Router Patterns (app/routers/users.py)**
- Follow FastAPI router structure with APIRouter, prefix, and tags
- Use comprehensive docstrings with examples for endpoint documentation
- Apply Depends(get_current_user) for authenticated endpoints
- Follow HTTPException pattern for error handling with appropriate status codes
- Return Pydantic schema response models

**Pydantic Schemas (app/schemas/user.py)**
- Create ContactResponseSchema and ContactUpdateSchema patterns
- Use Field validators for constraints (min_length, max_length)
- Apply ConfigDict(from_attributes=True) for SQLAlchemy model conversion
- Define separate request and response schemas

**Service Layer Pattern (app/services/user_service.py)**
- Create ContactService with static methods for business logic
- Implement validation in service layer before database operations
- Use db.commit() and db.refresh() pattern for updates
- Raise ValueError for business rule violations, catch in router for proper HTTP errors

**Frontend API Service (frontend/src/services/api.js)**
- Use existing apiGet, apiPost, apiPut, apiDelete helper functions
- Follow getAuthHeaders() pattern for authenticated requests
- Apply handleResponse() for consistent error handling
- Create contact-specific service methods following established patterns

**Frontend Components (FormInput.vue, DashboardView.vue)**
- Use Tailwind utility classes for styling (border, rounded-md, px-3, py-2, etc.)
- Follow Vue 3 Composition API with <script setup>
- Apply defineProps and defineEmits for component communication
- Use consistent layout structure (max-w-7xl, mx-auto, bg-white, shadow, rounded-lg)

**Database Patterns**
- Follow SQLAlchemy declarative base model structure
- Use relationship() with back_populates for associations
- Apply cascade behaviors for related entity management
- Create indexes on foreign keys and frequently queried columns

## Out of Scope
- Stage customization interface (adding, removing, renaming stages)
- Kanban board or drag-and-drop view for pipeline management
- Stage transition history or audit trail tracking
- Stage change confirmation dialogs or validation prompts
- Automated stage progression based on rules or triggers
- Stage-specific custom fields or conditional form fields
- Stage-specific workflows or automated actions
- Revenue reporting or analytics broken down by stage
- Time-in-stage metrics and analytics
- Stage change notifications or alerts to users
- Bulk stage updates for multiple contacts at once
- Stage-based access controls or permissions
- Custom stage colors or visual customization
- Stage progression probability or forecasting
- Integration of pipeline metrics into separate analytics dashboard
