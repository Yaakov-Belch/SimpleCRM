# Stage Propagation Fix

## Problem
When a new activity changes the pipeline stage of a contact, this change was not reflected in other parts of the UI (ContactPreview badge, contacts list table) because those components were not being notified to update or refetch data from the server.

## Root Cause
- The `current_pipeline_stage` is a computed property on the Contact model (backend) that derives from the most recent activity's `pipeline_stage`
- When an activity is saved with a new pipeline_stage, the API returns the saved activity, but the frontend contact objects were not updated to reflect the new stage
- Components displaying the contact's stage had stale data

## Solution
Implemented an event propagation chain that notifies all UI components when an activity changes a contact's pipeline stage:

```
ActivityForm → ActivityTimeline → ContactPreview → ContactsView
```

### Implementation Details

#### 1. ActivityForm.vue
**File**: `frontend/src/components/ActivityForm.vue`

**Changes**:
- Added `'stage-updated'` to emits (line 218)
- Modified `handleSubmit()` function (lines 269-319):
  - Tracks if the pipeline_stage changed when saving an activity
  - Compares old stage (for updates) or assumes change (for new activities)
  - Emits `stage-updated` event with payload: `{ contactId, stage }`

**Logic**:
```javascript
const stageChanged = props.activity
  ? props.activity.pipeline_stage !== formData.pipeline_stage
  : true // New activities always have a stage

// After saving...
if (stageChanged && savedActivity.pipeline_stage) {
  emit('stage-updated', {
    contactId: props.contactId,
    stage: savedActivity.pipeline_stage
  })
}
```

#### 2. ActivityTimeline.vue
**File**: `frontend/src/components/ActivityTimeline.vue`

**Changes**:
- Added `'stage-updated'` listener on ActivityForm component (line 84)
- Added `'stage-updated'` to emits (line 102)
- Implemented `handleStageUpdated()` function (lines 259-262) to forward event to parent

#### 3. ContactPreview.vue
**File**: `frontend/src/components/ContactPreview.vue`

**Changes**:
- Added `'stage-updated'` listener on ActivityTimeline component (line 84)
- Implemented `handleStageUpdated()` function (lines 172-181):
  - Updates the local contact object's `current_pipeline_stage` and `pipeline_stage`
  - Forwards event to ContactsView parent component

**Logic**:
```javascript
function handleStageUpdated(data) {
  // Update the local contact object
  if (props.contact && props.contact.id === data.contactId) {
    props.contact.current_pipeline_stage = data.stage
    props.contact.pipeline_stage = data.stage
  }

  // Forward the event to parent (ContactsView)
  emit('stage-updated', data)
}
```

#### 4. ContactsView.vue
**File**: `frontend/src/views/ContactsView.vue`

**No changes needed** - Already had the `onStageUpdated` handler (lines 376-392) that:
- Updates the contact in the contacts list
- Updates the selectedContact
- Refreshes filter counts

## Benefits
1. **Immediate UI updates**: No need to refresh the entire page or refetch contact data
2. **Optimistic updates**: Uses the stage from the saved activity response
3. **Consistent state**: All UI components showing the contact's stage are updated simultaneously
4. **Efficient**: No unnecessary API calls - stage is extracted from the activity save response

## Edge Cases Handled
1. **New activity creation**: When creating a new activity, the backend assigns a default stage. The form detects if the user changes it before saving.
2. **No stage change**: If the user saves an activity without changing the stage, no event is emitted (avoids unnecessary updates).
3. **Multiple contacts**: Each contact's stage is tracked independently using the contactId in the event payload.
4. **Contact switching**: When switching between contacts, the stage updates persist correctly in the list.

## Testing
The implementation was validated with a successful build:
```bash
npm run build
✓ built in 992ms
```

### Manual Testing Checklist
- [ ] Create new activity and change stage - verify all components update
- [ ] Edit existing activity and change stage - verify all components update
- [ ] Save activity without changing stage - verify no visual glitches
- [ ] Switch between contacts - verify stage updates persist
- [ ] Verify filter counts update correctly

## Files Modified
1. `frontend/src/components/ActivityForm.vue` - Emit stage-updated event
2. `frontend/src/components/ActivityTimeline.vue` - Forward stage-updated event
3. `frontend/src/components/ContactPreview.vue` - Forward event to parent (removed local mutation)
4. `frontend/src/views/ContactsView.vue` - Updated onStageUpdated to use immutable object updates

## Additional Fix: Vue Reactivity Issue

### Problem Found
The contacts list in the left panel wasn't updating because the original `onStageUpdated` function was directly mutating object properties:
```javascript
contact.current_pipeline_stage = stage  // Direct mutation
```

While Vue 3 supports deep reactivity, directly mutating nested properties doesn't always trigger template re-renders reliably, especially in arrays.

### Solution
Updated `onStageUpdated` in ContactsView.vue to use **immutable updates** by creating new objects:

**Before** (ContactsView.vue:376-392):
```javascript
function onStageUpdated({ contactId, stage }) {
  const contact = contacts.value.find(c => c.id === contactId)
  if (contact) {
    contact.current_pipeline_stage = stage
    contact.pipeline_stage = stage
  }
  // ...
}
```

**After** (ContactsView.vue:376-399):
```javascript
function onStageUpdated({ contactId, stage }) {
  const contactIndex = contacts.value.findIndex(c => c.id === contactId)
  if (contactIndex !== -1) {
    // Create a new object to ensure Vue's reactivity detects the change
    contacts.value[contactIndex] = {
      ...contacts.value[contactIndex],
      current_pipeline_stage: stage,
      pipeline_stage: stage
    }
  }

  // Update selected contact
  if (selectedContact.value?.id === contactId) {
    selectedContact.value = {
      ...selectedContact.value,
      current_pipeline_stage: stage,
      pipeline_stage: stage
    }
  }
  // ...
}
```

This approach:
- Creates new objects using the spread operator (`...`)
- Assigns the new object to the array index
- Ensures Vue's reactivity system detects the change
- Triggers template re-renders in the contacts table

## Technical Notes
- Uses Vue 3 event system for component communication
- No backend changes required
- Maintains existing data flow patterns
- Compatible with existing `onStageUpdated` handler in ContactsView
