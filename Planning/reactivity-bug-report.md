# Reactivity Bug Report: Activity Timeline Not Updating on Contact Change

**Date:** 2025-11-18
**Project:** SimpleCRM
**Feature:** Activity Timeline & Notes
**Severity:** High (User-facing data integrity issue)
**Status:** Root cause identified, fix pending

---

## Executive Summary

During user acceptance testing of the Activity Timeline & Notes feature, a critical bug was discovered: when switching between contacts, the activity timeline displays stale data from the previously selected contact. This creates a severe user experience issue where users see incorrect information and may believe data is lost or corrupted.

**Key Findings:**
- **Symptom:** Activity timeline shows wrong contact's activities when switching contacts
- **User Impact:** High - users see incorrect data, leading to confusion and perceived data loss
- **Technical Root Cause:** Component uses non-reactive `onMounted()` lifecycle hook for prop-dependent data fetching
- **Design Root Cause:** Missing reactivity requirements in component specifications and coding standards

**Good News:**
- Data is persisting correctly to the database
- Backend API is functioning properly
- Fix is straightforward (5 lines of code)
- This is a design documentation gap, not an architectural flaw

**Recommendations:**
- Immediate: Fix the component (add `watch()` for `contactId` prop)
- Short-term: Update coding standards and testing requirements
- Long-term: Create component specification templates with reactivity requirements

The root cause traces back to incomplete guidance in our design documentation. This report provides comprehensive recommendations to prevent similar issues in future features.

---

## Technical Summary

### Symptom
When a user selects a different contact in the CRM interface, the activity timeline continues to display activities from the previously selected contact instead of updating to show the new contact's activities.

### Problem
The `ActivityTimeline.vue` component fails to react to changes in its `contactId` prop, violating Vue's reactivity model and creating a data consistency issue in the user interface.

### Technical Root Cause
**Location:** `frontend/src/components/ActivityTimeline.vue`, lines 202-204

```javascript
onMounted(() => {
  fetchActivities()
})
```

**Issue:** The component fetches data only once when mounted, using the non-reactive `onMounted()` lifecycle hook. When the `contactId` prop changes, Vue reuses the existing component instance (performance optimization), but no code exists to detect the prop change and re-fetch data.

**Violation:** Misuse of non-reactive API (`onMounted`) for reactive data (props). This is fundamentally incompatible with Vue's reactivity system.

### Design Root Cause
**Missing Design Guidance:** Our design documentation lacks explicit requirements for component reactive behavior:

1. **Global Standards Gap:** `agent-os/standards/frontend/components.md` does not specify Vue 3 Composition API lifecycle patterns or reactivity rules
2. **Tech Stack Gap:** `agent-os/product/tech-stack.md` mentions "excellent reactivity" but provides no guidance on HOW to use it correctly
3. **Specification Gap:** Feature spec (`spec.md`) describes components but omits reactive behavior requirements
4. **Task Gap:** Implementation tasks (`tasks.md`) do not include explicit lifecycle implementation instructions
5. **Testing Gap:** `agent-os/standards/testing/test-writing.md` does not require prop reactivity tests

**Result:** The implementer had no guidance indicating that `onMounted()` is inappropriate for prop-dependent data fetching, leading to this anti-pattern.

---

## Detailed Analysis

### 1. Symptom: Stale Data Display

**User Workflow:**
1. User logs into SimpleCRM
2. User selects contact "David Cohen" from the contacts list
3. ActivityTimeline mounts and displays David's 4 activities ✅
4. User clicks contact "Yehonathan Miller"
5. ContactPreview updates: contact name changes to "Yehonathan Miller" ✅
6. ActivityTimeline still shows David's 4 activities ❌

**Why This Confused Users:**
Users reported "data loss on page reload" because:
- They added activities to David Cohen
- Switched to Yehonathan Miller (saw David's activities, didn't notice)
- Reloaded the page (saw empty state if no contact selected by default)
- Concluded their data was lost

**Actual State:**
- All data is correctly persisted in the database (verified: 4 activities exist for David Cohen)
- Backend API works correctly
- The issue is purely frontend reactivity

### 2. Problem: Component Reactivity Violation

**The Fundamental Issue:**

Vue's component model optimizes performance by **reusing component instances**. When `ContactPreview.vue` updates its `:contact-id` prop:

```vue
<!-- ContactPreview.vue, line 53 -->
<ActivityTimeline :contact-id="contact.id" />
```

Vue does NOT destroy and recreate `ActivityTimeline`. Instead:
- The existing component instance stays mounted
- Only the `contactId` prop value changes (1 → 2)
- No lifecycle hooks fire (`onMounted` only fires once per instance)
- Component continues displaying old data

**What the Code Does:**

```javascript
// ActivityTimeline.vue - Current Implementation (WRONG)
const props = defineProps({
  contactId: { type: Number, required: true }
})

onMounted(() => {
  fetchActivities()  // Uses props.contactId
})

async function fetchActivities() {
  const response = await getActivitiesForContact(props.contactId)
  activities.value = response.activities || []
}
```

**Execution Timeline:**
1. Component mounts with `contactId: 1`
2. `onMounted()` fires → `fetchActivities()` called → fetches contact 1's activities
3. Prop changes to `contactId: 2`
4. **Nothing happens** - `onMounted` doesn't fire again
5. Component still displays contact 1's activities

### 3. Technical Root Cause: Misuse of Non-Reactive API

**The Core Principle:**

> **Use reactive APIs for reactive data.**

Vue provides different APIs for different purposes:

| **API** | **Purpose** | **Use For** |
|---------|-------------|-------------|
| `onMounted()` | One-time initialization | Setting up event listeners, initializing third-party libraries |
| `watch()` | React to reactive changes | Re-fetching data when props/refs change |
| `watchEffect()` | Automatic dependency tracking | Complex reactive computations |

**The Violation:**

Using `onMounted()` for prop-dependent logic violates this separation:
- `onMounted()` is **non-reactive** - fires once per component lifetime
- `props.contactId` is **reactive** - can change multiple times
- Mixing them creates a reactivity blind spot

**The Correct Pattern:**

```javascript
// ActivityTimeline.vue - Correct Implementation
watch(() => props.contactId, (newId) => {
  if (newId) {
    fetchActivities()
  }
}, { immediate: true })  // immediate: true replaces onMounted
```

**Why This Works:**
- `watch()` is designed for reactive dependencies
- Fires whenever `props.contactId` changes
- `immediate: true` option fires on initial mount (no need for `onMounted`)
- Perfectly aligned with Vue's reactivity model

### 4. Design Root Cause: Documentation Gaps

This bug occurred because our design documentation failed to communicate the reactivity principle at multiple levels:

#### **Gap 1: Global Frontend Standards**

**File:** `agent-os/standards/frontend/components.md`

**Current Content:**
```markdown
- **Single Responsibility**: Each component should have one clear purpose
- **Reusability**: Design components to be reused across different contexts
- **State Management**: Keep state as local as possible
```

**Missing:**
- Vue 3 Composition API lifecycle patterns
- Reactivity principles and rules
- When to use `watch()` vs `onMounted()`
- Code examples showing correct patterns

**Impact:** Implementer has no reference for Vue-specific patterns.

#### **Gap 2: Tech Stack Documentation**

**File:** `agent-os/product/tech-stack.md`

**Current Content:**
```markdown
- **JavaScript Framework:** Vue.js 3 (Composition API)
  - Chosen for: Lightweight, excellent reactivity, gentle learning curve
```

**Missing:**
- What "excellent reactivity" means in practice
- How to leverage reactivity correctly
- Common pitfalls and anti-patterns

**Impact:** Technology choice lacks implementation guidance.

#### **Gap 3: Feature Specification**

**File:** `agent-os/specs/2025-11-18-activity-timeline-notes/spec.md`

**Current Content (lines 66-70):**
```markdown
**Frontend Components**
- Create ActivityTimeline.vue component for displaying activity list
- Create ActivityForm.vue component for creating/editing activities
```

**Missing:**
- Component reactive behavior requirements
- Lifecycle implementation requirements
- Specific test requirements for reactivity

**Impact:** Spec describes WHAT to build but not HOW reactive behavior should work.

#### **Gap 4: Implementation Tasks**

**File:** `agent-os/specs/2025-11-18-activity-timeline-notes/tasks.md`

**Current Content (lines 290-308):**
```markdown
- [ ] 6.2 Create ActivityTimeline.vue
  - Props: contactId (number, required)
  - Methods: fetchActivities() - GET /api/contacts/{contactId}/activities
  - Use Composition API
```

**Missing:**
- Explicit lifecycle instructions ("DO NOT use onMounted")
- Required implementation pattern ("MUST use watch with immediate: true")
- Acceptance criteria including reactivity verification

**Impact:** Task list doesn't prevent the anti-pattern.

#### **Gap 5: Testing Standards**

**File:** `agent-os/standards/testing/test-writing.md`

**Current Content:**
```markdown
- **Test Behavior, Not Implementation**
- **Mock External Dependencies**
- **Fast Execution**
```

**Missing:**
- Required tests for reactive components
- Test template for prop reactivity
- Examples of reactivity tests

**Impact:** Even though tests were written (10 tests for ActivityTimeline), none verified prop reactivity because it wasn't a required test case.

---

## Recommendations

### Phase 1: Immediate Fix (Development)

**Action:** Fix the ActivityTimeline component

**Code Change Required:**
```javascript
// File: frontend/src/components/ActivityTimeline.vue

// REMOVE:
onMounted(() => {
  fetchActivities()
})

// ADD:
watch(() => props.contactId, (newContactId) => {
  if (newContactId) {
    fetchActivities()
  }
}, { immediate: true })
```

**Additional Change:**
```javascript
// Add to fetchActivities() to clear stale data
async function fetchActivities() {
  loading.value = true
  activities.value = []  // Clear previous activities

  try {
    const response = await getActivitiesForContact(props.contactId)
    activities.value = response.activities || []
  } catch (err) {
    // ... error handling
  } finally {
    loading.value = false
  }
}
```

**Test to Add:**
```javascript
// File: frontend/tests/components/ActivityTimeline.test.js

it('re-fetches activities when contactId prop changes', async () => {
  const { wrapper, mockFetch } = await mountActivityTimeline({ contactId: 1 })
  await flushPromises()

  expect(mockFetch).toHaveBeenCalledWith(
    expect.stringContaining('/api/contacts/1/activities')
  )

  // Change contactId prop
  await wrapper.setProps({ contactId: 2 })
  await flushPromises()

  expect(mockFetch).toHaveBeenCalledWith(
    expect.stringContaining('/api/contacts/2/activities')
  )
  expect(mockFetch).toHaveBeenCalledTimes(2)
})

it('clears previous activities while loading new ones', async () => {
  const { wrapper } = await mountActivityTimeline({ contactId: 1 })
  await flushPromises()

  // Verify activities loaded for contact 1
  expect(wrapper.vm.activities).toHaveLength(3)

  // Change contact
  await wrapper.setProps({ contactId: 2 })

  // Activities should be cleared immediately
  expect(wrapper.vm.activities).toHaveLength(0)
  expect(wrapper.vm.loading).toBe(true)
})
```

---

### Phase 2: Documentation Updates (Prevent Future Occurrences)

#### **Update 1: Frontend Component Standards**

**File:** `agent-os/standards/frontend/components.md`

**Add New Section:**

```markdown
## Vue 3 Composition API Patterns

### Core Principle: Use Reactive APIs for Reactive Data

**Rule:** When component behavior depends on reactive values (props, refs, computed), ALWAYS use reactive APIs (`watch`, `watchEffect`, `computed`). NEVER use non-reactive lifecycle hooks (`onMounted`, `onBeforeMount`) for reactive dependencies.

### Data Fetching Based on Props

**Problem:** Component needs to fetch data based on a prop value that can change.

✅ **Correct Pattern:**
```javascript
import { watch, ref } from 'vue'
import { fetchDataFromApi } from '@/services/api'

const props = defineProps({
  entityId: { type: Number, required: true }
})

const data = ref([])
const loading = ref(false)

// Use watch for prop-dependent data fetching
watch(() => props.entityId, async (newId) => {
  if (!newId) return

  loading.value = true
  data.value = []  // Clear stale data

  try {
    data.value = await fetchDataFromApi(newId)
  } catch (error) {
    console.error('Failed to fetch:', error)
  } finally {
    loading.value = false
  }
}, { immediate: true })  // immediate: true fires on mount
```

❌ **Anti-Pattern (DO NOT USE):**
```javascript
// WRONG: onMounted doesn't react to prop changes
onMounted(async () => {
  data.value = await fetchDataFromApi(props.entityId)
  // Will NEVER update when props.entityId changes!
})
```

**Why This Matters:**
- Vue reuses component instances for performance
- Props can change without component remounting
- `onMounted` fires only ONCE per component lifetime
- Data becomes stale when props change

### When to Use Each Lifecycle Hook

| **Hook** | **Use For** | **Example** |
|----------|-------------|-------------|
| `watch(() => props.x)` | Prop-dependent data fetching | Fetch user data when userId prop changes |
| `watchEffect()` | Auto-tracked dependencies | Update derived state based on multiple refs |
| `computed()` | Synchronous derived state | Format display values from reactive state |
| `onMounted()` | One-time initialization ONLY | Set up event listeners, initialize third-party libraries |
| `onBeforeMount()` | Pre-render setup | Rarely needed with Composition API |
| `onUnmounted()` | Cleanup | Remove event listeners, cancel timers |

### Multiple Reactive Dependencies

**Problem:** Component depends on multiple props or refs.

**Pattern:**
```javascript
// Watch multiple dependencies
watch([() => props.categoryId, () => props.sortBy],
  async ([categoryId, sortBy]) => {
    if (categoryId) {
      await fetchItems(categoryId, sortBy)
    }
  },
  { immediate: true }
)
```

### Component Specification Checklist

When designing a component, document:

- [ ] **Props:** List all props with types and purpose
- [ ] **Reactive Behavior:** Explicitly state which prop changes trigger which side effects
- [ ] **Lifecycle Requirements:** Specify which hooks are needed and why
- [ ] **Required Tests:** Include prop reactivity tests for all data-fetching logic

**Example Specification:**
```markdown
## Component: UserActivityList

**Props:**
- `userId` (Number, required): ID of user whose activities to display

**Reactive Behavior:**
- MUST re-fetch activities when `userId` prop changes
- MUST clear previous activities before fetching new ones
- MUST show loading state during fetch

**Implementation Requirements:**
- Use `watch(() => props.userId, ..., { immediate: true })`
- DO NOT use `onMounted()` for data fetching

**Required Tests:**
- "fetches activities on initial mount"
- "re-fetches activities when userId changes"
- "clears stale activities while loading"
```

### Code Review Checklist for Vue Components

When reviewing Vue components, verify:

- [ ] Does component fetch data based on props?
  - [ ] If yes: Uses `watch()` instead of `onMounted()`?
  - [ ] If yes: Uses `{ immediate: true }` option?
  - [ ] Clears stale data before fetching new data?
- [ ] Does component have reactive dependencies?
  - [ ] All dependencies in `watch()` or `watchEffect()`?
  - [ ] No reactive logic in `onMounted()`?
- [ ] Are prop reactivity tests present?
  - [ ] Tests verify re-fetch on prop change?
  - [ ] Tests verify stale data cleared?
```

---

#### **Update 2: Global Tech Stack Standards**

**File:** `agent-os/standards/global/tech-stack.md`

**Modify Existing Section:**

```markdown
### Frontend
- **JavaScript Framework:** Vue.js 3 (Composition API)
- **CSS Framework:** Tailwind CSS
- **UI Components:** Custom components (keep it simple)
- **Build Tool:** Vite

**Vue 3 Composition API Requirements:**
- **Lifecycle Pattern:** Use `watch()` with `{ immediate: true }` for prop-dependent initialization
- **Reactivity Rule:** Never use `onMounted()` for reactive dependencies (props, refs, computed)
- **State Management:** Keep state as local as possible; lift only when needed
- **Testing Requirement:** All prop-dependent data fetching MUST have prop reactivity tests

**Common Anti-Patterns to Avoid:**
```javascript
// ❌ WRONG: Using onMounted with prop-dependent logic
onMounted(() => {
  fetchData(props.id)  // Won't update when props.id changes
})

// ✅ CORRECT: Using watch with immediate option
watch(() => props.id, (id) => {
  fetchData(id)
}, { immediate: true })
```
```

---

#### **Update 3: Testing Standards**

**File:** `agent-os/standards/testing/test-writing.md`

**Add New Section:**

```markdown
## Required Tests by Component Type

### Data-Fetching Components

**Definition:** Components that fetch data from APIs based on prop values.

**Required Tests:**

#### Test 1: Initial Data Fetch
```javascript
it('fetches data on initial mount', async () => {
  const wrapper = mount(Component, {
    props: { entityId: 1 }
  })
  await flushPromises()

  expect(mockApiFetch).toHaveBeenCalledWith(
    expect.stringContaining('/entities/1')
  )
  expect(wrapper.vm.data).toBeDefined()
})
```

#### Test 2: Prop Reactivity (CRITICAL)
```javascript
it('re-fetches data when key prop changes', async () => {
  const wrapper = mount(Component, {
    props: { entityId: 1 }
  })
  await flushPromises()

  expect(mockApiFetch).toHaveBeenCalledWith(
    expect.stringContaining('/entities/1')
  )

  // Change prop
  await wrapper.setProps({ entityId: 2 })
  await flushPromises()

  // Verify new fetch
  expect(mockApiFetch).toHaveBeenCalledWith(
    expect.stringContaining('/entities/2')
  )
  expect(mockApiFetch).toHaveBeenCalledTimes(2)
})
```

#### Test 3: Stale Data Handling
```javascript
it('clears stale data while loading new data', async () => {
  const wrapper = mount(Component, {
    props: { entityId: 1 }
  })
  await flushPromises()

  expect(wrapper.vm.data).toHaveLength(3)  // Has data

  // Change prop
  await wrapper.setProps({ entityId: 2 })

  // Data should be cleared immediately, before fetch completes
  expect(wrapper.vm.data).toHaveLength(0)
  expect(wrapper.vm.loading).toBe(true)
})
```

**Why These Tests Matter:**

The "prop reactivity" test (Test 2) would have caught this bug during development. Without this test, the anti-pattern goes undetected until user testing.

**Test Coverage Principle:**

> Tests should verify behavior that users depend on. If users expect the UI to update when they change selections, that behavior MUST be tested.
```

---

#### **Update 4: Product Tech Stack**

**File:** `agent-os/product/tech-stack.md`

**Modify Section (lines 17-20):**

```markdown
### Frontend Stack
- **JavaScript Framework:** Vue.js 3 (Composition API)
  - Chosen for: Lightweight, excellent reactivity, gentle learning curve, powerful composables
  - Using Composition API for better TypeScript support and code organization
  - **Reactivity Pattern:** Always use `watch()` for prop-dependent data fetching
  - **Lifecycle Pattern:** `onMounted()` for one-time setup only, never for reactive data
  - **Testing Requirement:** All prop-dependent fetches must have reactivity tests
- **CSS Framework:** Tailwind CSS
  - Chosen for: Rapid UI development, utility-first approach, small bundle size
```

---

### Phase 3: Process & Template Improvements

#### **New Document 1: Component Specification Template**

**File:** `agent-os/templates/component-spec-template.md`

```markdown
# Component Specification Template

Use this template when specifying new Vue components.

## Component: [ComponentName]

### Purpose
[Brief description of what this component does]

### Props

| Prop Name | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| entityId | Number | Yes | - | ID of entity to display |

### Reactive Behavior

**Data Dependencies:**
- [ ] Component fetches data based on props
- [ ] Component computes derived state from props
- [ ] Component watches external state (stores, composables)

**Reactivity Requirements:**

For each reactive dependency, specify:

**When `entityId` prop changes:**
- MUST: Re-fetch entity data from API
- MUST: Clear previous entity data before fetching
- MUST: Show loading state during fetch
- MUST NOT: Use `onMounted()` for this logic

**Implementation Pattern:**
```javascript
watch(() => props.entityId, async (newId) => {
  if (!newId) return

  loading.value = true
  data.value = null  // Clear stale data

  try {
    data.value = await fetchEntity(newId)
  } finally {
    loading.value = false
  }
}, { immediate: true })
```

### Lifecycle Requirements

**Initialization:**
- [ ] Use `watch()` with `{ immediate: true }` for prop-dependent setup
- [ ] Use `onMounted()` ONLY for one-time initialization (if needed)

**Cleanup:**
- [ ] Use `onUnmounted()` for cleanup (if needed)

### State Management

**Local State:**
- `data` (ref): Entity data from API
- `loading` (ref): Loading state
- `error` (ref): Error state

**Computed State:**
- `formattedDate` (computed): Formatted display of entity.date

### Events Emitted

| Event Name | Payload | When | Description |
|------------|---------|------|-------------|
| updated | entity | After successful save | Entity was updated |

### Required Tests

- [ ] **Initial Mount Test:** Fetches data on initial mount with provided prop
- [ ] **Prop Reactivity Test:** Re-fetches data when prop changes
- [ ] **Stale Data Test:** Clears previous data before fetching new data
- [ ] **Loading State Test:** Shows loading state during fetch
- [ ] **Error Handling Test:** Displays error message on fetch failure

### Acceptance Criteria

- [ ] Component renders correctly with valid prop
- [ ] Component re-fetches data when prop changes (verified by test)
- [ ] Stale data cleared before new fetch (verified by test)
- [ ] Loading states display correctly
- [ ] Error states handled gracefully
- [ ] No console errors or warnings
- [ ] Follows existing component patterns (Tailwind CSS, Composition API)
```

---

#### **New Document 2: Code Review Checklist**

**File:** `agent-os/standards/code-review-checklist.md`

```markdown
# Code Review Checklist

## Vue 3 Component Review

### Reactivity & Lifecycle

- [ ] **Prop-Dependent Logic**
  - [ ] Component fetches data based on props?
    - [ ] Uses `watch(() => props.x)` instead of `onMounted()`?
    - [ ] Uses `{ immediate: true }` option?
    - [ ] Clears stale data before fetching new data?
  - [ ] Component computes values from props?
    - [ ] Uses `computed()` for synchronous derivation?
    - [ ] Uses `watch()` for async side effects?

- [ ] **Lifecycle Hooks**
  - [ ] `onMounted()` used ONLY for one-time initialization?
  - [ ] No reactive dependencies in `onMounted()`?
  - [ ] `onUnmounted()` properly cleans up (listeners, timers, etc.)?

- [ ] **State Management**
  - [ ] State kept as local as possible?
  - [ ] No unnecessary prop drilling?
  - [ ] Proper use of emits for parent communication?

### Testing

- [ ] **Prop Reactivity Tests** (for data-fetching components)
  - [ ] Test exists: "fetches data on initial mount"?
  - [ ] Test exists: "re-fetches when prop changes"?
  - [ ] Test exists: "clears stale data while loading"?

- [ ] **Coverage**
  - [ ] All critical user workflows tested?
  - [ ] Tests verify behavior, not implementation?
  - [ ] Tests are fast and isolated?

### Code Quality

- [ ] **Composition API**
  - [ ] Follows setup script pattern (`<script setup>`)?
  - [ ] Proper use of `ref`, `reactive`, `computed`?
  - [ ] No unnecessary `reactive()` wrapping?

- [ ] **Props & Emits**
  - [ ] Props have type definitions?
  - [ ] Required vs optional props clearly marked?
  - [ ] Emits declared with `defineEmits()`?

- [ ] **Error Handling**
  - [ ] API errors caught and displayed to user?
  - [ ] Loading states prevent race conditions?
  - [ ] No unhandled promise rejections?

### Accessibility

- [ ] **Keyboard Navigation**
  - [ ] Interactive elements focusable?
  - [ ] Tab order logical?

- [ ] **Screen Readers**
  - [ ] Semantic HTML used?
  - [ ] ARIA labels where needed?

### Performance

- [ ] **Reactivity**
  - [ ] No unnecessary watchers?
  - [ ] Computed values used instead of methods where appropriate?
  - [ ] No watch inside watch?

- [ ] **Rendering**
  - [ ] v-if used for conditional rendering (not v-show for large trees)?
  - [ ] Keys provided for v-for lists?

## Backend Review

### API Endpoints

- [ ] **REST Conventions**
  - [ ] Proper HTTP methods (GET, POST, PUT, DELETE)?
  - [ ] Appropriate status codes (200, 201, 204, 400, 404)?
  - [ ] Consistent URL patterns?

- [ ] **Authentication & Authorization**
  - [ ] Endpoints protected with `Depends(get_current_user)`?
  - [ ] Ownership verification in service layer?

### Database

- [ ] **Models**
  - [ ] Proper foreign keys with CASCADE behavior?
  - [ ] Indexes on frequently queried fields?
  - [ ] Timestamps (created_at, updated_at)?

- [ ] **Queries**
  - [ ] No N+1 query problems?
  - [ ] Proper use of joins/eager loading?

### Testing

- [ ] **Service Layer**
  - [ ] Critical business logic tested?
  - [ ] Ownership verification tested?

- [ ] **API Endpoints**
  - [ ] Happy path tested?
  - [ ] Error cases tested (404, 403, 400)?

## General

- [ ] Code follows project conventions?
- [ ] No debugging code (console.log, debugger)?
- [ ] Comments explain "why", not "what"?
- [ ] No TODO comments without tickets?
- [ ] Documentation updated?
```

---

#### **New Document 3: Feature Spec Template with Reactivity**

**File:** `agent-os/templates/feature-spec-template.md`

```markdown
# Feature Specification Template

## [Feature Name]

### Goal
[High-level objective of this feature]

### User Stories
- As a [user type], I want to [action] so that [benefit]

### Specific Requirements

#### Frontend Components

##### [ComponentName] Component

**Purpose:** [What this component does]

**Props:**
- `propName` (Type, required/optional): Description

**Reactive Behavior:**
> IMPORTANT: Specify exactly when component should re-fetch or recalculate

**When `propName` changes:**
- MUST re-fetch [data] from API
- MUST clear previous [data] before fetching
- MUST show loading state

**Implementation Requirements:**
- Use `watch(() => props.propName, ..., { immediate: true })`
- DO NOT use `onMounted()` for data fetching

**State:**
- `data` (ref): [Description]
- `loading` (ref): Loading state
- `error` (ref): Error state

**API Calls:**
- `GET /api/endpoint` - [Description]

**Layout:**
- [Description of UI layout]

**Styling:**
- Tailwind CSS following existing patterns

**Required Tests:**
- [ ] Fetches data on initial mount
- [ ] Re-fetches when `propName` changes (CRITICAL)
- [ ] Clears stale data while loading
- [ ] Displays loading state
- [ ] Handles errors gracefully

**Acceptance Criteria:**
- [ ] Component displays correct data for given prop
- [ ] Component updates when prop changes (verified by test)
- [ ] No console errors
- [ ] Follows existing component patterns

[Repeat for each component]

#### Backend API

[Backend specifications...]

### Out of Scope
[Explicitly list what is NOT included]

### Testing Requirements

**Minimum Required Tests:**
- [ ] All components with prop-dependent data fetching have reactivity tests
- [ ] All API endpoints have basic happy path tests
- [ ] Critical user workflows covered by integration tests

### Documentation Requirements

- [ ] API endpoints documented
- [ ] Component usage documented
- [ ] README updated with new feature
```

---

### Phase 4: Training & Knowledge Sharing

#### **Recommendation 1: Developer Onboarding Checklist**

Create: `agent-os/onboarding/vue-reactivity-guide.md`

```markdown
# Vue 3 Reactivity Guide for SimpleCRM

## Key Concept: Reactive vs Non-Reactive APIs

Vue 3's power comes from its reactivity system. Understanding when to use reactive vs non-reactive APIs is critical.

### The Golden Rule

> If your code depends on reactive data (props, refs, computed), use reactive APIs (watch, watchEffect, computed). Never use non-reactive lifecycle hooks (onMounted, onBeforeMount).

### Common Scenario: Data Fetching Based on Props

**Scenario:** You need to fetch user data when a `userId` prop is provided or changes.

**❌ Wrong Approach:**
```javascript
onMounted(() => {
  fetchUser(props.userId)
})
// Problem: Doesn't update when props.userId changes!
```

**✅ Correct Approach:**
```javascript
watch(() => props.userId, (userId) => {
  if (userId) fetchUser(userId)
}, { immediate: true })
// Fires on mount AND whenever props.userId changes
```

### Practice Exercise

Try fixing this buggy component:

```vue
<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  productId: Number
})

const product = ref(null)

onMounted(async () => {
  product.value = await fetchProduct(props.productId)
})
</script>
```

**Bug:** When parent changes `productId`, the product doesn't update.

**Fix:** Replace `onMounted` with `watch(() => props.productId, ...)`.

### Quiz

1. When should you use `onMounted()`?
   - **Answer:** Only for one-time initialization (event listeners, third-party lib setup)

2. How do you fetch data based on a prop?
   - **Answer:** `watch(() => props.x, fetch, { immediate: true })`

3. What's the purpose of `{ immediate: true }`?
   - **Answer:** Runs the watcher callback immediately on component mount
```

#### **Recommendation 2: Internal Tech Talk**

Schedule a team session covering:
1. This bug as a case study
2. Vue reactivity fundamentals
3. Live coding: Fixing the bug together
4. Code review practice with reactivity checklist

---

### Phase 5: Automated Prevention

#### **Recommendation 1: ESLint Rule**

Create custom ESLint rule or use existing:

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    // Warn when onMounted accesses props
    'vue/no-setup-props-destructure': 'error',

    // Custom rule (requires development)
    'custom/no-props-in-onmounted': 'warn'
  }
}
```

#### **Recommendation 2: Pre-commit Hook**

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for common reactivity anti-patterns
if git diff --cached --name-only | grep -q '\.vue$'; then
  echo "Checking Vue files for reactivity anti-patterns..."

  if git diff --cached | grep -E 'onMounted.*props\.' > /dev/null; then
    echo "⚠️  WARNING: Possible reactivity issue detected!"
    echo "   Found 'props' access inside 'onMounted()'"
    echo "   Consider using 'watch(() => props.x)' instead"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
fi
```

---

## Implementation Priority

### Priority 1: Immediate (This Sprint)
1. ✅ Fix ActivityTimeline component
2. ✅ Add prop reactivity tests
3. ✅ Verify fix with manual testing

### Priority 2: Short-term (Next Sprint)
1. Update `agent-os/standards/frontend/components.md` with reactivity patterns
2. Update `agent-os/standards/testing/test-writing.md` with required tests
3. Create `agent-os/templates/component-spec-template.md`
4. Create `agent-os/standards/code-review-checklist.md`

### Priority 3: Medium-term (Next Month)
1. Update `agent-os/product/tech-stack.md`
2. Update `agent-os/standards/global/tech-stack.md`
3. Create `agent-os/onboarding/vue-reactivity-guide.md`
4. Review ALL existing Vue components for similar issues
5. Add prop reactivity tests to existing components

### Priority 4: Long-term (Next Quarter)
1. Develop custom ESLint rule for reactivity anti-patterns
2. Set up pre-commit hooks
3. Conduct team training session
4. Create video tutorial for component development

---

## Success Metrics

### Immediate Success
- [ ] Bug fixed in ActivityTimeline
- [ ] Prop reactivity tests pass
- [ ] User testing confirms issue resolved

### Process Success (3 months)
- [ ] All documentation updated
- [ ] No new reactivity bugs in code reviews
- [ ] All new components have prop reactivity tests
- [ ] 100% of developers trained on reactivity patterns

### Long-term Success (6 months)
- [ ] Zero reactivity bugs in production
- [ ] Automated detection catching issues in CI/CD
- [ ] Component development time reduced (clear patterns = faster development)

---

## Conclusion

This bug revealed a critical gap in our design documentation rather than a flaw in our architecture. The fix is simple (5 lines of code), but the learning opportunity is significant.

**Key Takeaways:**

1. **Technical:** Always use reactive APIs (`watch`) for reactive dependencies (props, refs)
2. **Design:** Component specifications must explicitly define reactive behavior
3. **Testing:** Prop reactivity tests should be mandatory for data-fetching components
4. **Process:** Code review checklists prevent anti-patterns from merging

By implementing these recommendations, we transform this bug from a one-time fix into a systematic improvement that prevents similar issues across all future features.

The investment in documentation and process now will pay dividends in:
- Faster development (clear patterns to follow)
- Fewer bugs (automated and manual checks)
- Better code quality (consistent reactive behavior)
- Smoother onboarding (explicit guidance for new developers)

---

## Appendix: Quick Reference

### When to Use Each API

```javascript
// ✅ Fetch data based on prop
watch(() => props.id, fetchData, { immediate: true })

// ✅ Compute derived value from prop
const displayName = computed(() => props.user.name.toUpperCase())

// ✅ Auto-track multiple dependencies
watchEffect(() => {
  console.log(props.a, state.b)  // Automatically re-runs when either changes
})

// ✅ One-time initialization ONLY
onMounted(() => {
  window.addEventListener('resize', handleResize)
  initializeThirdPartyLib()
})

// ❌ NEVER: Props in onMounted
onMounted(() => {
  fetchData(props.id)  // WRONG - doesn't react to prop changes
})
```

### Testing Template

```javascript
// REQUIRED test for every prop-dependent component
it('re-fetches when prop changes', async () => {
  const wrapper = mount(Component, { props: { id: 1 } })
  await flushPromises()
  expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/1'))

  await wrapper.setProps({ id: 2 })
  await flushPromises()
  expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/2'))
})
```

---

**Report Author:** Claude (AI Assistant)
**Reviewed By:** [To be filled by Product Owner]
**Approved By:** [To be filled by Tech Lead]
**Date:** 2025-11-18
